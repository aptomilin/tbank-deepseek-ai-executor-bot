import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class Config:
    # Telegram Bot
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
    
    # Tinkoff Invest
    TINKOFF_TOKEN = os.getenv("TINKOFF_TOKEN", "")
    
    # DeepSeek AI
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # App Settings
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
    USE_SANDBOX = os.getenv("USE_SANDBOX", "true").lower() == "true"
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        if not cls.BOT_TOKEN:
            errors.append("BOT_TOKEN is required")
        if not cls.DEEPSEEK_API_KEY:
            errors.append("DEEPSEEK_API_KEY is required")
        
        if not cls.TINKOFF_TOKEN and not cls.DEMO_MODE:
            logger.warning("TINKOFF_TOKEN not set and DEMO_MODE=false - running in demo mode")
        
        if errors:
            raise ValueError("Configuration errors: " + "; ".join(errors))

config = Config()