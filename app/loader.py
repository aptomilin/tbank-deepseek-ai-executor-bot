import logging
import os
from typing import Optional

from tinkoff.invest import AsyncClient

# Используем существующую структуру конфигурации из проекта
from app.settings import settings

# Создаем логгер для этого модуля
logger = logging.getLogger(__name__)


def load_config():
    """Загрузка конфигурации приложения"""
    return settings


async def initialize_tinkoff_client(config) -> AsyncClient:
    """Инициализация клиента Tinkoff Invest API"""
    try:
        client = AsyncClient(
            token=config.TINKOFF_TOKEN if config.TINKOFF_TOKEN else "sandbox_token",
            app_name=config.TINKOFF_APP_NAME
        )
        
        if config.TINKOFF_SANDBOX_MODE:
            logger.info("🔧 Initializing sandbox mode...")
            
            try:
                # Пытаемся создать новый счет с обработкой ошибок
                open_account_response = await client.sandbox.open_sandbox_account()
                account_id = open_account_response.account_id
                logger.info(f"✅ Created new sandbox account: {account_id}")
                
                # Пополняем счет после создания
                await setup_sandbox_account(client, account_id)
                
            except Exception as e:
                logger.warning(f"⚠️ Cannot create sandbox account: {e}")
                # Используем фиктивный account_id для продолжения работы
                account_id = "sandbox_account_id"
                logger.info(f"✅ Using fallback sandbox account: {account_id}")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Tinkoff client: {e}")
        raise


async def setup_sandbox_account(client: AsyncClient, account_id: str) -> str:
    """Настройка песочного счета (пополнение баланса)"""
    try:
        # Пополняем песочный счет
        from tinkoff.invest import MoneyValue, Currency
        await client.sandbox.sandbox_pay_in(
            account_id=account_id,
            amount=MoneyValue(units=1000000, nano=0, currency=Currency.RUB)
        )
        logger.info("💰 Sandbox account funded with 1,000,000 RUB")
        return account_id
        
    except Exception as e:
        logger.warning(f"⚠️ Could not fund sandbox account: {e}")
        return account_id


async def close_tinkoff_client(client: AsyncClient):
    """Закрытие клиента Tinkoff Invest API"""
    await client.close()
    logger.info("✅ Tinkoff client closed")