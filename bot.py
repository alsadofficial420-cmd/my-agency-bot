import os
import logging
import requests
from flask import Flask, request

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
GEMINI_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Simple in-memory storage for conversation history per user
# Note: this resets if the server restarts (free plan sleeps after inactivity)
user_memory = {}

SYSTEM_PROMPT = (
    "তুমি একজন ব্যক্তিগত AI অ্যাসিস্ট্যান্ট যে একজন ডিজিটাল মার্কেটিং এজেন্সির মালিককে সাহায্য করো। "
    "তুমি বাংলা এবং ইংরেজি দুই ভাষায় কথা বলতে পারো, ব্যবহারকারী যেই ভাষায় লিখবে সেই ভাষায় উত্তর দেবে। "
    "তুমি ব্যবহারকারীর তথ্য (নাম, পেশা, পছন্দ ইত্যাদি) মনে রাখবে এবং পরের কথোপকথনে ব্যবহার করবে। "
    "কন্টেন্ট লেখা, রিপ্লাই বানানো, প্ল্যানিং, এবং সাধারণ প্রশ্নের উত্তর দিতে সাহায্য করো। "
    "সংক্ষিপ্ত এবং বন্ধুত্বপূর্ণ উত্তর দাও।"
)


def get_user_history(chat_id):
    if chat_id not in user_memory:
        user_memory[chat_id] = []
    return user_memory[chat_id]


def call_gemini(chat_id, user_text):
    history = get_user_history(chat_id)

    # Build conversation contents for Gemini
    contents = []
    for turn in history[-10:]:  # keep last 10 turns
        contents.append(turn)

    contents.append({"role": "user", "parts": [{"text": user_text}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
    }

    try:
        resp = requests.post(GEMINI_API, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        logger.error(f"Gemini error: {e}")
        reply = "দুঃখিত, একটা সমস্যা হয়েছে। আবার চেষ্টা করুন।"

    # Save to history
    history.append({"role": "user", "parts": [{"text": user_text}]})
    history.append({"role": "model", "parts": [{"text": reply}]})
    user_memory[chat_id] = history

    return reply


def send_telegram_message(chat_id, text):
    url = f"{TELEGRAM_API}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"


@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.get_json()
    logger.info(f"Received update: {update}")

    if "message" in update and "text" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        text = update["message"]["text"]

        if text == "/start":
            send_telegram_message(
                chat_id,
                "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। "
                "আপনার যেকোনো কাজে সাহায্য করতে পারি। কী করতে পারি বলুন!",
            )
        else:
            reply = call_gemini(chat_id, text)
            send_telegram_message(chat_id, reply)

    return "ok", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
