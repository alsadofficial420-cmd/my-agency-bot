# My Agency Bot

একটা personal AI assistant যা Telegram-এর মাধ্যমে কাজ করে।

## কী করে
- Telegram-এ message পাঠালে AI (Gemini) reply দেয়
- ব্যবহারকারীর তথ্য মনে রাখে (conversation history)
- বাংলা এবং ইংরেজি দুই ভাষায় কথা বলে
- Digital marketing related কাজ (content লেখা, reply বানানো ইত্যাদি) করতে সাহায্য করে

## Environment Variables (Render-এ সেট করতে হবে)
- `TELEGRAM_TOKEN` - BotFather থেকে পাওয়া token
- `GEMINI_API_KEY` - Google AI Studio থেকে পাওয়া API key

## Deploy (Render.com)
1. Build command: `pip install -r requirements.txt`
2. Start command: `gunicorn bot:app`
3. Environment variables যুক্ত করুন উপরে উল্লেখিত
4. Deploy হলে যে URL পাবেন (যেমন `https://my-agency-bot.onrender.com`), সেটা দিয়ে Telegram webhook সেট করতে হবে:

```
https://api.telegram.org/bot<TELEGRAM_TOKEN>/setWebhook?url=https://your-app.onrender.com/webhook
```

এই লিংক browser-এ একবার খুললেই webhook সেট হয়ে যাবে।
