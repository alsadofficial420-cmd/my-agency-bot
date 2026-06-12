import os
import threading
from flask import Flask
import telebot
from google import genai

# Render-এর পরিবেশ থেকে টোকেন ও কি নেওয়া
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

# মেমোরি হিস্ট্রি রাখার ডিকশনারি
user_chats = {}

# ১. Render-কে খুশি রাখার জন্য একটি মিনি Flask ওয়েব অ্যাপ তৈরি
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running perfectly 24/7!"

# ২. বটের মেসেজ হ্যান্ডলার পার্ট
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। আমি সফলভাবে চালু হয়েছি! আপনার যেকোনো কাজ আমাকে দিন।")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    try:
        if user_id not in user_chats:
            user_chats[user_id] = client.chats.create(model="gemini-3.5-flash")
        
        response = user_chats[user_id].send_message(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, f"কোথাও একটা সমস্যা হয়েছে! আসল এরর: {str(e)}")

# ৩. ব্যাকগ্রাউন্ডে টেলিগ্রাম বট চালানোর ফাংশন
def run_bot():
    bot.remove_webhook()
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # টেলিগ্রাম বটটিকে আলাদা একটি থ্রেডে ব্যাকগ্রাউন্ডে চালু করা
    threading.Thread(target=run_bot, daemon=True).start()
    
    # Render-এর দেওয়া পোর্টে Flask ওয়েব অ্যাপটি রান করা
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
