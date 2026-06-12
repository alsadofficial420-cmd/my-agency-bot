import os
import requests
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# জেমিনি এপিআই-তে সরাসরি মেসেজ পাঠানোর ফাংশন (কোনো লাইব্রেরি ছাড়া)
def ask_gemini(user_message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"কোথাও একটা সমস্যা হয়েছে! এরর: {str(e)}"

@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আসসালামu আলাইকুম! আমি আপনার AI অ্যাসিস্ট্যান্ট। বলুন কীভাবে সাহায্য করতে পারি?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # ডাইরেক্ট জেমিনি থেকে উত্তর আসবে
    bot_response = ask_gemini(message.text)
    bot.reply_to(message, bot_response)

RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
