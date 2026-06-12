import os
from flask import Flask, request
import telebot
from google import genai

# টোকেন ও এআই কি নেওয়া
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("BOT_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

user_chats = {}
app = Flask(__name__)

# ১. টেলিগ্রাম থেকে আসা মেসেজ রিসিভ করার রুট (Webhook Route)
@app.route(f'/{BOT_TOKEN}', methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

# ২. সার্ভার লাইভ আছে কিনা চেক করার রুট
@app.route('/')
def home():
    return "Bot is running perfectly 24/7!", 200

# ৩. বটের মূল কাজ (মেসেজ হ্যান্ডলার)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। আমি সফলভাবে চালু হয়েছি! বলুন আপনাকে কীভাবে সাহায্য করতে পারি?")

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

# ৪. Render-এর লিঙ্কের সাথে বটের কানেকশন জুড়ে দেওয়া
# (এটি আলাদা কোনো থ্রেড ছাড়াই টেলিগ্রামের সাথে বটকে সরাসরি কানেক্ট করে দেয়)
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
if RENDER_EXTERNAL_URL:
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
