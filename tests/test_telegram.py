# test_telegram_token.py
import os
from telegram import Bot

token = os.getenv('TELEGRAM_BOT_TOKEN')
if token:
    bot = Bot(token=token)
    try:
        info = bot.get_me()
        print(f"✅ Бот работает: @{info.username}")
    except Exception as e:
        print(f"❌ Ошибка токена: {e}")
else:
    print("❌ TELEGRAM_BOT_TOKEN не установлен")