#!/usr/bin/env python3
"""
Simple test to check if bot starts
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment FIRST
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def start(update, context):
    """Handle /start command"""
    user = update.effective_user
    logger.info(f"📨 START command from {user.first_name}")
    await update.message.reply_text(f"✅ Бот работает! Привет, {user.first_name}!")

async def run_bot():
    """Run the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        return
    
    print(f"🔑 Token: {token[:10]}...")
    
    try:
        from telegram.ext import Application, CommandHandler
    except ImportError as e:
        print(f"❌ Failed to import telegram: {e}")
        return
    
    # Create application
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    
    print("🚀 Starting bot polling...")
    print("📍 Bot is now listening for messages...")
    print("💬 Send /start to your bot in Telegram")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        # Run polling with proper error handling
        await application.run_polling(
            drop_pending_updates=True,
            allowed_updates=['message']
        )
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        logger.error(f"Bot error: {e}")

def main():
    """Main function"""
    print("=" * 50)
    print("🤖 SIMPLE BOT TEST")
    print("=" * 50)
    
    # Check if we're in an async environment
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("⚠️  Event loop is already running - using nested approach")
            # Create a new task in existing loop
            task = loop.create_task(run_bot())
            try:
                loop.run_until_complete(task)
            except KeyboardInterrupt:
                task.cancel()
                print("🛑 Bot stopped")
        else:
            # Normal execution
            asyncio.run(run_bot())
    except RuntimeError:
        # No event loop, create new one
        asyncio.run(run_bot())

if __name__ == "__main__":
    main()