#!/usr/bin/env python3
"""
Tinkoff Executor Bot with DeepSeek AI Integration
Главный файл для запуска Telegram бота с AI функционалом
"""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager

from app.loader import setup_bot, setup_dependencies
from app.handlers import ai_strategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def bot_lifetime(dp):
    """Управление жизненным циклом бота"""
    # Startup
    logger.info("Starting Tinkoff Executor Bot with DeepSeek AI...")
    
    # Регистрация обработчиков
    dp.include_router(ai_strategy.router)
    
    logger.info("Bot started successfully")
    
    yield
    
    # Shutdown
    logger.info("Bot stopped")

async def main():
    """Основная функция запуска бота"""
    try:
        # Инициализация бота и зависимостей
        bot, dp = setup_bot()
        dependencies = setup_dependencies()
        
        # Внедрение зависимостей
        dp['deepseek_client'] = dependencies['deepseek_client']
        dp['tinkoff_client'] = dependencies['tinkoff_client']
        dp['ai_strategy_manager'] = dependencies['ai_strategy_manager']
        
        # Запуск бота
        async with bot_lifetime(dp):
            await dp.start_polling(bot)
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)