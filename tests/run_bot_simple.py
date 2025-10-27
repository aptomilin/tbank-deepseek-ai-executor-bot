#!/usr/bin/env python3
"""
Simple working bot without event loop issues
"""
import os
import logging
from dotenv import load_dotenv

# Load environment first
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main function"""
    print("=" * 60)
    print("🤖 INVESTMENT ADVISOR BOT - SIMPLE VERSION")
    print("=" * 60)
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        return
    
    print(f"✅ Token: {token[:10]}...")
    print("🚀 Starting bot...")
    
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Command handlers
        async def start(update, context):
            user = update.effective_user
            logger.info(f"START from {user.first_name}")
            await update.message.reply_text(
                f"🤖 Привет, {user.first_name}!\n\n"
                "Я ваш инвестиционный советник!\n"
                "Используйте /portfolio для анализа"
            )
        
        async def portfolio(update, context):
            logger.info("PORTFOLIO command")
            await update.message.reply_text(
                "📊 Анализ портфеля:\n"
                "• Акции: 100,000 руб\n"
                "• Облигации: 50,000 руб\n"
                "• Всего: 150,000 руб\n\n"
                "🎯 Рекомендация: Диверсифицируйте портфель"
            )
        
        async def handle_message(update, context):
            text = update.message.text
            user = update.effective_user
            logger.info(f"Message from {user.first_name}: {text}")
            await update.message.reply_text(f"📨 Получил: {text}")
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("portfolio", portfolio))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("📍 Бот запущен и слушает сообщения...")
        print("💬 Откройте Telegram и отправьте /start вашему боту")
        print("⏹️  Нажмите Ctrl+C для остановки")
        print("-" * 60)
        
        # Run polling - this will block until Ctrl+C
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message']
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install python-telegram-bot")
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()