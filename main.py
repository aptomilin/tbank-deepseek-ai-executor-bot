#!/usr/bin/env python3
"""
Главный модуль Investment Advisor Application
Интеграция Tinkoff Invest API с Telegram ботом и AI-аналитикой
"""

import logging
import os
from app.loader import load_config
from app.bot.investment_bot import InvestmentTelegramBot


def setup_logging():
    """Настройка логирования"""
    # Создаем папку для логов
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Настраиваем корневой логгер
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )

    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Обработчик для файла
    file_handler = logging.FileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики к корневому логгеру
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)


def main():
    """Основная функция приложения"""
    # Настройка логирования
    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting Investment Advisor Application...")

    try:
        # Загрузка конфигурации
        config = load_config()
        logger.info("✅ Configuration loaded")

        # Создание бота
        bot = InvestmentTelegramBot(config)

        logger.info("✅ Bot initialized")
        logger.info("🤖 Starting Telegram bot...")

        # Запуск бота
        bot.run()

    except Exception as e:
        logger.error(f"❌ Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()