import os
import requests
from flask import Flask, request
import telebot

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Kono google library chara direct url diye gemini-te message bhejari function
def ask_gemini(user_message):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        return data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"Gemini error: {str(e)}"

# Apnar documentation-er shathe mil rekhe ekhane /webhook deya holo
@app.route('/webhook', methods=['POST'])
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
    bot.reply_to(message, "As-salamu alaykum! Ami apnar AI Assistant. Bolun kivabe sahajjo korte pari?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot_response = ask_gemini(message.text)
    bot.reply_to(message, bot_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
