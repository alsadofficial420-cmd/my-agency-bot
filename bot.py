import os
import requests
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def ask_gemini(user_message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        
        # জেমিনির রেসপন্স চেক করা
        if 'candidates' in data and len(data['candidates']) > 0:
            return data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in data:
            return f"জেমিনি API এরর দিয়েছে: {data['error']['message']}"
        else:
            return f"জেমিনি থেকে কোনো উত্তর আসেনি। রেসপন্স ডেটা: {str(data)}"
    except Exception as e:
        return f"সার্ভার এরর: {str(e)}"

@app.route('/webhook', methods=['POST'])
def getMessage():
    try:
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"ওয়েবহুক প্রসেসিং এরর: {str(e)}")
    return "!", 200

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

@bot.message_handler(commands=['start'])
def send_welcome(message):
    try:
        bot.reply_to(message, "আসসালামু আলাইকুম! আমি লাইভ আছি। বলুন কীভাবে সাহায্য করতে পারি?")
    except Exception as e:
        print(f"স্টার্ট কম্যান্ড এরর: {str(e)}")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot_response = ask_gemini(message.text)
        bot.reply_to(message, bot_response)
    except Exception as e:
        try:
            bot.reply_to(message, f"মেসেজ হ্যান্ডলার এরর: {str(e)}")
        except:
            pass

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
