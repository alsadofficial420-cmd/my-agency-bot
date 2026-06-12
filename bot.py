import os
import telebot
from google import genai

# Render-er Environment Variables theke token neya
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
client = genai.Client(api_key=GEMINI_KEY)

# Shob user-er kotha r kaj mone rakhar memory session
user_chats = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "আসসালামু আলাইকুম! আমি আপনার ব্যক্তিগত AI অ্যাসিস্ট্যান্ট। আপনার যেকোনো কাজে সাহায্য করতে পারি। কী করতে পারি বলুন!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    try:
        # User jodi prothom hoy tobe tar jonno memory clear kora
        if user_id not in user_chats:
            user_chats[user_id] = client.chats.create(model="gemini-3.5-flash")
        
        # User jekono kaj dile jomini sheta kore reply dibe
        response = user_chats[user_id].send_message(message.text)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        # Jodi kono error hoy tobe bot apnake ota message e bole dibe
        bot.reply_to(message, f"Kothao ekta shomosshe hoyese! Real Error: {str(e)}")

bot.polling()
