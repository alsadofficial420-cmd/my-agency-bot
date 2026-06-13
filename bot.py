import os
import sys
import requests
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


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
def getMessage():
    log("WEBHOOK HIT")
    try:
        json_string = request.get_data().decode('utf-8')
        log(f"RAW UPDATE: {json_string}")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        log("PROCESSED UPDATE OK")
    except Exception as e:
        log(f"WEBHOOK ERROR: {str(e)}")
    return "!", 200


@app.route('/')
def home():
    return "Bot is running 24/7!", 200


@bot.message_handler(commands=['start'])
def send_welcome(message):
    log("START COMMAND RECEIVED")
    try:
        bot.reply_to(message, "আসসালামু আলাইকুম! আমি লাইভ আছি। বলুন কীভাবে সাহায্য করতে পারি?")
        log("START REPLY SENT")
    except Exception as e:
        log(f"START ERROR: {str(e)}")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    log(f"MESSAGE RECEIVED: {message.text}")
    try:
        bot_response = ask_gemini(message.text)
        log(f"SENDING REPLY: {bot_response}")
        bot.reply_to(message, bot_response)
        log("REPLY SENT OK")
    except Exception as e:
        log(f"MESSAGE HANDLER ERROR: {str(e)}")
        try:
            bot.reply_to(message, f"মেসেজ হ্যান্ডলার এরর: {str(e)}")
        except Exception as e2:
            log(f"REPLY ERROR TOO: {str(e2)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
