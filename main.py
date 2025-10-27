"""
Main application entry point
"""
import logging
import sys
from dotenv import load_dotenv
from app.loader import initialize_app
from app.telegram_bot import InvestmentTelegramBot

# Load environment first
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Main application function"""
    try:
        print("🚀 Starting Investment Advisor Application...")
        
        # Initialize Tinkoff API dependencies
        logger.info("Initializing dependencies...")
        if not initialize_app():
            logger.error("❌ Failed to initialize dependencies")
            return 1
        
        logger.info("✅ Dependencies initialized successfully")
        
        # Start Telegram bot
        bot = InvestmentTelegramBot()
        bot.run()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Application error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())