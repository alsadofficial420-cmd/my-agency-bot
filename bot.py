import os
from flask import Flask, request
import telebot
import google.generativeai as genai

# টোকেন ও এআই কি নেওয়া
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

# ১. টেলিগ্রাম থেকে আসা মেসেজ রিসিভ করার রুট
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ২. সার্ভার লাইভ চেক
@app.route('/')
def home():
    return "Bot is running perfectly 24/7!", 200

# ৩. বটের মূল কাজ (মেসেজ হ্যান্ডলার)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। বলুন আপনাকে কীভাবে সাহায্য করতে পারি?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        # গুগল জেমিনি থেকে উত্তর নেওয়া (সহজ ও ১০০% কার্যকরী কোড)
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"কোথাও একটা সমস্যা হয়েছে! এরর: {str(e)}")

# ৪. Render-এর লিঙ্কের সাথে বটের কানেকশন জুড়ে দেওয়া
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
