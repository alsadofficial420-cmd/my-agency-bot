import os
import sys
import requests
from flask import Flask, request

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={GEMINI_KEY}"

app = Flask(__name__)

# প্রতি user-এর কথোপকথনের history মনে রাখার জন্য (in-memory, server চলাকালীন)
user_memory = {}

SYSTEM_PROMPT = (
    "তুমি একজন ব্যক্তিগত AI অ্যাসিস্ট্যান্ট, যে একজন ডিজিটাল মার্কেটিং এজেন্সির মালিককে "
    "(যিনি 'The Gifty Gear' নামে একটা gadget ও gift item-এর dropshipping business চালান) "
    "সাহায্য করে। তুমি বাংলা এবং ইংরেজি দুই ভাষায় কথা বলতে পারো — ব্যবহারকারী যেই ভাষায় "
    "লিখবে সেই ভাষায় উত্তর দেবে। তুমি ব্যবহারকারীর তথ্য (নাম, পেশা, পছন্দ, business "
    "সংক্রান্ত তথ্য) মনে রাখবে এবং পরের কথোপকথনে ব্যবহার করবে। তুমি content লেখা, social "
    "media caption, ad copy, marketing plan, customer reply draft, এবং সাধারণ যেকোনো "
    "প্রশ্নের উত্তর দিতে সাহায্য করো। সংক্ষিপ্ত, স্পষ্ট, এবং বন্ধুত্বপূর্ণ উত্তর দাও।"
)


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def send_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    resp = requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=30)
    log(f"SEND MESSAGE RESPONSE: {resp.status_code}")


def get_history(chat_id):
    if chat_id not in user_memory:
        user_memory[chat_id] = []
    return user_memory[chat_id]


def ask_gemini(chat_id, user_message):
    try:
        history = get_history(chat_id)

        # conversation history থেকে contents বানানো (last 20 turns রাখা)
        contents = []
        for turn in history[-20:]:
            contents.append(turn)
        contents.append({"role": "user", "parts": [{"text": user_message}]})

        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=60)
        data = response.json()

        log(f"GEMINI STATUS: {response.status_code}")

        if 'candidates' in data and len(data['candidates']) > 0:
            reply = data['candidates'][0]['content']['parts'][0]['text']

            # history-তে save করা
            history.append({"role": "user", "parts": [{"text": user_message}]})
            history.append({"role": "model", "parts": [{"text": reply}]})
            user_memory[chat_id] = history

            return reply
        elif 'error' in data:
            error_msg = data['error'].get('message', 'Unknown error')
            log(f"GEMINI ERROR: {error_msg}")
            return f"দুঃখিত, AI সার্ভিসে সমস্যা: {error_msg}"
        else:
            log(f"UNEXPECTED GEMINI RESPONSE: {data}")
            return "দুঃখিত, AI থেকে কোনো উত্তর পাওয়া যায়নি।"
    except Exception as e:
        log(f"EXCEPTION in ask_gemini: {str(e)}")
        return f"সার্ভার এরর: {str(e)}"


@app.route('/webhook', methods=['POST'])
def webhook():
    log("WEBHOOK HIT")
    try:
        update = request.get_json()

        if update and "message" in update:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"].get("text", "")

            log(f"CHAT_ID: {chat_id}, TEXT: {text}")

            if text == "/start":
                user_memory[chat_id] = []  # নতুন শুরু করলে memory clear
                send_message(
                    chat_id,
                    "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। "
                    "আপনার তথ্য, পছন্দ, এবং কথোপকথন মনে রাখি যাতে আরো ভালোভাবে সাহায্য করতে পারি। "
                    "বলুন কীভাবে সাহায্য করতে পারি?"
                )
            elif text == "/reset":
                user_memory[chat_id] = []
                send_message(chat_id, "ঠিক আছে, আমি সব ভুলে গেছি। নতুন করে শুরু করা যাক!")
            else:
                reply = ask_gemini(chat_id, text)
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
