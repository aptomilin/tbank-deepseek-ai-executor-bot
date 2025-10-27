#!/usr/bin/env python3
"""
Test Telegram bot setup and configuration
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_environment():
    """Test Telegram environment configuration"""
    print("🔍 Checking Telegram environment...")
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        print("💡 Get token from @BotFather and add to .env:")
        print("   TELEGRAM_BOT_TOKEN=your_actual_token_here")
        return False
    
    if token.startswith('your_') or len(token) < 10:
        print("❌ TELEGRAM_BOT_TOKEN appears to be a placeholder")
        print("💡 Replace with actual token from @BotFather")
        return False
    
    print(f"✅ TELEGRAM_BOT_TOKEN found (length: {len(token)})")
    return True


async def test_telegram_connection():
    """Test connection to Telegram API"""
    try:
        from telegram import Bot
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            return False
            
        print("🔗 Testing Telegram API connection...")
        bot = Bot(token=token)
        
        # Test bot info
        bot_info = await bot.get_me()
        print(f"✅ Bot connected: @{bot_info.username} (ID: {bot_info.id})")
        print(f"✅ Bot name: {bot_info.first_name}")
        
        # Test webhook info
        webhook_info = await bot.get_webhook_info()
        print(f"📡 Webhook URL: {webhook_info.url or 'Not set'}")
        print(f"📡 Pending updates: {webhook_info.pending_update_count}")
        
        return True
        
    except ImportError:
        print("❌ python-telegram-bot not installed")
        print("💡 Run: pip install python-telegram-bot")
        return False
    except Exception as e:
        print(f"❌ Telegram connection failed: {e}")
        return False


async def test_bot_functionality():
    """Test basic bot functionality"""
    try:
        from telegram import Bot
        from telegram.ext import Application, CommandHandler
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            return False
            
        print("🤖 Testing bot functionality...")
        
        # Create application
        application = Application.builder().token(token).build()
        
        # Add test command
        async def test_command(update, context):
            await update.message.reply_text("✅ Bot is working!")
        
        application.add_handler(CommandHandler("test", test_command))
        
        # Test initialization
        await application.initialize()
        await application.start()
        print("✅ Bot application started successfully")
        
        # Cleanup
        await application.stop()
        await application.shutdown()
        
        return True
        
    except Exception as e:
        print(f"❌ Bot functionality test failed: {e}")
        return False


def check_bot_creation_guide():
    """Provide guide for creating bot"""
    print("\n🎯 HOW TO CREATE TELEGRAM BOT:")
    print("1. Open Telegram and search for @BotFather")
    print("2. Send /newbot command")
    print("3. Choose a name for your bot")
    print("4. Choose a username (must end with 'bot')")
    print("5. Copy the token and add to .env file:")
    print("   TELEGRAM_BOT_TOKEN=your_copied_token_here")
    print("6. Start chatting with your bot!")


async def main():
    """Run all Telegram tests"""
    print("=" * 50)
    print("TELEGRAM BOT SETUP TEST")
    print("=" * 50)
    
    # Test 1: Environment
    env_ok = test_environment()
    if not env_ok:
        check_bot_creation_guide()
        return
    
    # Test 2: Connection
    connection_ok = await test_telegram_connection()
    if not connection_ok:
        return
    
    # Test 3: Functionality
    functionality_ok = await test_bot_functionality()
    
    print("\n" + "=" * 50)
    if env_ok and connection_ok and functionality_ok:
        print("🎉 ALL TELEGRAM TESTS PASSED!")
        print("✅ Your bot is ready to use!")
        print("\n💡 Next steps:")
        print("   - Implement your command handlers")
        print("   - Add bot to your chat")
        print("   - Send /start to your bot")
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Check the errors above")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())