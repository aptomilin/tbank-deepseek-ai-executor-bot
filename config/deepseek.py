import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DeepSeekConfig:
    """Конфигурация для DeepSeek API"""
    API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    BASE_URL = "https://api.deepseek.com/chat/completions"
    MODEL = "deepseek-chat"
    TIMEOUT = 30
    MAX_TOKENS = 4000
    TEMPERATURE = 0.3
    
    @classmethod
    def is_configured(cls):
        """Проверка наличия API ключа"""
        return bool(cls.API_KEY and cls.API_KEY != "your_deepseek_api_key_here")
    
    @classmethod
    def validate(cls):
        """Validate DeepSeek configuration"""
        if not cls.is_configured():
            raise ValueError("DEEPSEEK_API_KEY is not properly configured")

deepseek_config = DeepSeekConfig()