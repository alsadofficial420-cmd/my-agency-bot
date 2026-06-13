import os
import sys
import json
import requests
from flask import Flask, request

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

app = Flask(__name__)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=30)
    log(f"SEND MESSAGE RESPONSE: {resp.status_code} {resp.text}")


def ask_gemini(user_message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()

        log(f"GEMINI STATUS: {response.status_code}")
        log(f"GEMINI DATA: {data}")

        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            return f"দুঃখিত, AI সার্ভিসে সমস্যা: {error_msg}"
        else:
            return "দুঃখিত, AI থেকে কোনো উত্তর পাওয়া যায়নি।"
    except Exception as e:
        log(f"EXCEPTION in ask_gemini: {str(e)}")
        return f"সার্ভার এরর: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    log("WEBHOOK HIT")
    try:
        update = request.get_json()
        log(f"UPDATE: {update}")

        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")

            log(f"CHAT_ID: {chat_id}, TEXT: {text}")

            if text == "/start":
                send_message(chat_id, "আসসালামু আলাইকুম! আমি লাইভ আছি। বলুন কীভাবে সাহায্য করতে পারি?")
            else:
                reply = ask_gemini(text)
                log(f"REPLY: {reply}")
                send_message(chat_id, reply)
        else:
            log("NO MESSAGE IN UPDATE")

    except Exception as e:
        log(f"WEBHOOK ERROR: {str(e)}")

    return "ok", 200


@app.route('/')
def home():
    return "Bot is running 24/7!", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
