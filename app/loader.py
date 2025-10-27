import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from services.tinkoff.client import TinkoffInvestClient
from services.ai_strategy import DeepSeekClient, AIStrategyManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def setup_bot():
    """Настройка бота и диспетчера"""
    try:
        # Validate configuration
        config.validate()
        
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        
        logger.info("Bot initialized successfully")
        return bot, dp
        
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        sys.exit(1)

def setup_dependencies():
    """Настройка зависимостей приложения"""
    try:
        # Validate DeepSeek configuration
        from config.deepseek import deepseek_config
        deepseek_config.validate()
        
        # Инициализация AI сервисов
        deepseek_client = DeepSeekClient()
        
        # Инициализация Tinkoff клиента
        tinkoff_client = TinkoffInvestClient()
        
        # Создаем AI Strategy Manager
        ai_strategy_manager = AIStrategyManager(deepseek_client, tinkoff_client)
        
        dependencies = {
            'deepseek_client': deepseek_client,
            'tinkoff_client': tinkoff_client,
            'ai_strategy_manager': ai_strategy_manager
        }
        
        mode_info = []
        if config.DEMO_MODE:
            mode_info.append("DEMO")
        if tinkoff_client.use_sandbox and tinkoff_client.is_configured:
            mode_info.append("SANDBOX")
        elif tinkoff_client.is_configured:
            mode_info.append("REAL")
        
        logger.info(f"Dependencies initialized successfully. Mode: {'+'.join(mode_info)}")
        return dependencies
        
    except Exception as e:
        logger.error(f"Failed to initialize dependencies: {e}")
        sys.exit(1)