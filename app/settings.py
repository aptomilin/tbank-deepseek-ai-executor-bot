import os
from typing import List


class Settings:
    """Настройки приложения"""

    def __init__(self):
        # Загружаем переменные окружения из .env файла
        self._load_env_file()

        # Tinkoff Invest API
        self.TINKOFF_TOKEN: str = os.getenv("TINKOFF_TOKEN", "")
        self.TINKOFF_APP_NAME: str = os.getenv("TINKOFF_APP_NAME", "InvestmentAdvisor")
        self.TINKOFF_ACCOUNT_ID: str = os.getenv("TINKOFF_ACCOUNT_ID", "")
        self.TINKOFF_SANDBOX_MODE: bool = os.getenv("TINKOFF_SANDBOX_MODE", "true").lower() == "true"

        # Telegram Bot
        self.TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

        # Парсим TELEGRAM_ADMIN_IDS из переменной окружения
        telegram_admin_ids = os.getenv("TELEGRAM_ADMIN_IDS", "")
        self.TELEGRAM_ADMIN_IDS: List[int] = []
        if telegram_admin_ids:
            self.TELEGRAM_ADMIN_IDS = list(map(int, telegram_admin_ids.split(',')))

        # Database
        self.DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./investment_bot.db")

        # AI Settings
        self.DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
        self.DEEPSEEK_API_URL: str = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1")
        self.OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
        self.OPENROUTER_API_URL: str = os.getenv("OPENROUTER_API_URL", "https://openrouter.ai/api/v1")

        # Проверяем обязательные настройки
        self._validate_settings()

    def _load_env_file(self):
        """Загружает переменные окружения из .env файла"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Если python-dotenv не установлен, продолжаем без него
            pass

    def _validate_settings(self):
        """Проверяет обязательные настройки"""
        if not self.TELEGRAM_BOT_TOKEN:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN is required! "
                "Please set it in .env file or environment variables. "
                "Get token from @BotFather: https://t.me/BotFather"
            )


# Создаем экземпляр настроек
settings = Settings()