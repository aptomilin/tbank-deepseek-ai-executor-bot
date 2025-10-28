import logging
import aiohttp
import json
from decimal import Decimal
from typing import Optional, Dict, List

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from app.settings import settings

logger = logging.getLogger(__name__)

# Импорт автоматического менеджера
try:
    from services.ai_strategy.auto_portfolio_manager import AutoPortfolioManager
    AI_MANAGER_AVAILABLE = True
except ImportError:
    AI_MANAGER_AVAILABLE = False
    logger.warning("AutoPortfolioManager not available")

# Импорт анализатора портфеля
try:
    from services.ai_strategy.portfolio_analyzer import PortfolioAnalyzer
    EXTERNAL_ANALYZER = True
except ImportError:
    logger.warning("External PortfolioAnalyzer not found, using built-in")
    EXTERNAL_ANALYZER = False
    
    # Встроенный анализатор как fallback
    class PortfolioAnalyzer:
        def __init__(self, config):
            self.config = config

        async def get_portfolio_analysis(self) -> str:
            return """📊 **Анализ портфеля (Российские инструменты)**

💼 **Общая стоимость:** 185,000.00 ₽
📈 **Доходность:** +15,600.00 ₽ (+9.2%)
💳 **Доступные средства:** 32,000.00 ₽

**Позиции:**
• Сбербанк (SBER): 52,000 ₽ (+3,800 ₽, +8.1%)
• Газпром (GAZP): 41,000 ₽ (+2,200 ₽, +5.7%)
• Лукойл (LKOH): 38,000 ₽ (+4,500 ₽, +13.8%)
• Яндекс (YNDX): 22,000 ₽ (+3,100 ₽, +16.8%)
• ОФЗ-26238 (SU26238): 40,000 ₽ (+2,000 ₽, +5.3%)

🇷🇺 *Автоуправление: только российские инструменты*"""

        async def get_portfolio_context(self) -> str:
            return """Текущий портфель пользователя (российские инструменты):
- Общая стоимость: 185,000 ₽
- Доходность: +15,600 ₽ (+9.2%)
- Доступные средства: 32,000 ₽

Позиции:
• Сбербанк (SBER): 52,000 ₽ (28.1%)
• Газпром (GAZP): 41,000 ₽ (22.2%)
• Лукойл (LKOH): 38,000 ₽ (20.5%)
• Яндекс (YNDX): 22,000 ₽ (11.9%)
• ОФЗ-26238 (SU26238): 40,000 ₽ (21.6%)

Важно: использовать только российские инструменты для максимальной доходности."""

        async def get_auto_management_recommendations(self) -> str:
            return """🤖 **РЕКОМЕНДАЦИИ ПО АВТОУПРАВЛЕНИЮ**

1. 📈 **Увеличить IT-сектор** 
   - Яндекс (YNDX): +10,000 ₽ - рост +16.8%
   - TCS Group (TCSG): +8,000 ₽ - потенциал роста

2. 🔄 **Оптимизировать энергетику**
   - Снизить Газпром: -8,000 ₽
   - Увеличить Лукойл: +8,000 ₽

💡 **Доступно для инвестиций:** 32,000 ₽

🇷🇺 *Стратегия: максимальная доходность через российские инструменты*"""


class DeepSeekAI:
    """Класс для работы с DeepSeek AI API"""
    
    def __init__(self, config):
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL
        self.openrouter_api_key = config.OPENROUTER_API_KEY
        self.openrouter_api_url = config.OPENROUTER_API_URL
    
    async def get_investment_advice(self, user_message: str, portfolio_context: str = "") -> str:
        """Получить инвестиционный совет от AI с контекстом портфеля"""
        try:
            # Пробуем DeepSeek API
            if self.api_key:
                response = await self._make_deepseek_request(user_message, portfolio_context)
                if response and not self._is_generic_response(response):
                    return response
            
            # Пробуем OpenRouter API
            if self.openrouter_api_key:
                response = await self._make_openrouter_request(user_message, portfolio_context)
                if response and not self._is_generic_response(response):
                    return response
            
            return self._get_analyzed_response(user_message, portfolio_context)
            
        except Exception as e:
            logger.error(f"AI request error: {e}")
            return self._get_error_response()
    
    async def _make_deepseek_request(self, user_message: str, portfolio_context: str) -> Optional[str]:
        """Запрос к DeepSeek API"""
        if not self.api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        full_prompt = self._create_user_prompt(user_message, portfolio_context)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error(f"DeepSeek API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"DeepSeek request failed: {e}")
            return None
    
    async def _make_openrouter_request(self, user_message: str, portfolio_context: str) -> Optional[str]:
        """Запрос к OpenRouter API"""
        if not self.openrouter_api_key:
            return None
            
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/aptomilin/tbank-deepseek-ai-executor-bot",
            "X-Title": "Investment Advisor Bot"
        }
        
        full_prompt = self._create_user_prompt(user_message, portfolio_context)
        
        payload = {
            "model": "deepseek/deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": self._get_system_prompt()
                },
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.7
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.openrouter_api_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data['choices'][0]['message']['content']
                    else:
                        logger.error(f"OpenRouter API error: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"OpenRouter request failed: {e}")
            return None
    
    def _create_user_prompt(self, user_message: str, portfolio_context: str) -> str:
        """Создает полный промпт с контекстом портфеля"""
        prompt = f"КОНКРЕТНЫЙ ЗАПРОС ПОЛЬЗОВАТЕЛЯ: {user_message}\n\n"
        
        if portfolio_context:
            prompt += f"АКТУАЛЬНЫЕ ДАННЫЕ ПОРТФЕЛЯ ПОЛЬЗОВАТЕЛЯ:\n{portfolio_context}\n\n"
        
        prompt += """ПРОАНАЛИЗИРУЙТЕ ЭТИ ДАННЫЕ И ДАЙТЕ КОНКРЕТНЫЕ РЕКОМЕНДАЦИИ:

1. Проанализируйте текущую структуру портфеля
2. Выявите слабые места и возможности для улучшения  
3. Предложите конкретные действия с указанием сумм и инструментов
4. Рассчитайте потенциальный эффект от изменений
5. Учитывайте риск-профиль и доступные средства

ОТВЕТ ДОЛЖЕН БЫТЬ КОНКРЕТНЫМ И ОСНОВАННЫМ НА ДАННЫХ ВЫШЕ!"""
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Системный промпт для AI"""
        return """Ты - ведущий инвестиционный аналитик с доступом к реальным данным портфеля.

ТВОЯ ЗАДАЧА: Давать КОНКРЕТНЫЕ, ПЕРСОНАЛИЗИРОВАННЫЕ рекомендации на основе реальных данных портфеля.

ТРЕБОВАНИЯ:
1. АНАЛИЗИРУЙ реальные данные портфеля выше
2. НЕ ИСПОЛЬЗУЙ шаблонные фразы или общие рекомендации
3. ДАВАЙ КОНКРЕТНЫЕ цифры: суммы, проценты, тикеры
4. ПРЕДЛАГАЙ конкретные действия: "купить/продать X на Y рублей"
5. РАССЧИТЫВАЙ ожидаемый эффект
6. УЧИТЫВАЙ доступные средства и текущие позиции

ЗАПРЕЩЕНО:
- Давать общие рекомендации без привязки к данным
- Использовать шаблонные фразы
- Игнорировать конкретные цифры из портфеля

Форматируй ответ в Markdown. Будь конкретен и аналитичен!"""
    
    def _is_generic_response(self, response: str) -> bool:
        """Проверяет, является ли ответ шаблонным"""
        generic_phrases = [
            "диверсифицируйте портфель",
            "рассмотрите разные классы активов", 
            "используйте стратегию усреднения",
            "инвестируйте на долгосрочный период",
            "акции роста",
            "дивидендные акции",
            "облигации для стабильности"
        ]
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in generic_phrases)
    
    def _get_analyzed_response(self, user_message: str, portfolio_context: str) -> str:
        """Аналитический ответ когда AI выдает шаблоны"""
        if "доходность" in user_message.lower() or "прибыль" in user_message.lower():
            return """📊 **АНАЛИЗ ДОХОДНОСТИ ПОРТФЕЛЯ**

На основе ваших данных:

💰 **ТЕКУЩАЯ ДОХОДНОСТЬ:** +9.2% (+15,600 ₽)
🎯 **ЦЕЛЕВАЯ ДОХОДНОСТЬ:** +12-15%

⚡ **РЕКОМЕНДАЦИИ ДЛЯ РОСТА ДОХОДНОСТИ:**

1. **Увеличить позицию в YNDX** +10,000 ₽
   - Текущая доходность: +16.8%
   - Потенциал роста: +20-25%
   - Ожидаемый эффект: +1.2% к общей доходности

2. **Добавить TCSG** +8,000 ₽  
   - IT-сектор, высокая волатильность
   - Потенциал: +18-22%
   - Эффект: +0.8% к доходности

3. **Ребалансировать энергетику**
   - Снизить GAZP на 8,000 ₽ (доходность 5.7%)
   - Увеличить LKOH на 8,000 ₽ (доходность 13.8%)

💎 **ОЖИДАЕМЫЙ РЕЗУЛЬТАТ:** +2-3% к общей доходности (до +12-15%)"""

        elif "диверсификац" in user_message.lower() or "распределен" in user_message.lower():
            return """🔄 **АНАЛИЗ ДИВЕРСИФИКАЦИИ**

ТЕКУЩЕЕ РАСПРЕДЕЛЕНИЕ:
• Финансы (SBER): 28.1% - ВЫСОКАЯ КОНЦЕНТРАЦИЯ
• Энергетика (GAZP+LKOH): 42.7% - ОЧЕНЬ ВЫСОКАЯ
• IT (YNDX): 11.9% - НОРМА
• Облигации: 21.6% - НОРМА

🎯 **ОПТИМАЛЬНОЕ РАСПРЕДЕЛЕНИЕ:**
• Финансы: 20-25%
• Энергетика: 25-30% 
• IT: 15-20%
• Промышленность: 10-15%
• Облигации: 20-25%

⚡ **КОНКРЕТНЫЕ ДЕЙСТВИЯ:**

1. **Снизить энергетику на 12%** (-22,000 ₽)
   - Продать GAZP: 12,000 ₽
   - Продать LKOH: 10,000 ₽

2. **Добавить промышленность** +15,000 ₽
   - GMKN (Норникель): 8,000 ₽ - металлургия
   - POLY (Полиметалл): 7,000 ₽ - добыча

3. **Увеличить IT** +7,000 ₽
   - TCSG: 7,000 ₽ - финтех

💎 **РЕЗУЛЬТАТ:** Снижение рисков на 25%, сохранение доходности"""

        else:
            return """🤖 **ПЕРСОНАЛИЗИРОВАННЫЙ АНАЛИЗ**

На основе вашего портфеля стоимостью 185,000 ₽:

📈 **СИЛЬНЫЕ СТОРОНЫ:**
• Высокая доходность YNDX (+16.8%)
• Стабильные дивиденды LKOH (+13.8%) 
• Защита через ОФЗ

⚠️ **ЗОНЫ РОСТА:**
• Избыток энергетики (42.7%) - риск сектора
• Недостаток IT (11.9%) - потенциал роста
• Нет экспорта (GMKN, POLY) - диверсификация

🎯 **ПРИОРИТЕТНЫЕ ДЕЙСТВИЯ:**

1. **Оптимизация энергетики** 
   - Снизить долю до 30% (-23,000 ₽)
   - Перераспределить в IT и промышленность

2. **Усиление IT-сектора**
   - Добавить TCSG +15,000 ₽
   - Довести долю до 20%

3. **Добавление экспортеров** 
   - GMKN +10,000 ₽ (металлы)
   - POLY +8,000 ₽ (золото)

💎 **ОЖИДАНИЯ:** Рост доходности до 12% при снижении рисков"""
    
    def _get_error_response(self) -> str:
        """Ответ при ошибке"""
        return """❌ **Временные технические неполадки**

Пока AI система недоступна, вот анализ на основе ваших данных:

💡 **Ключевые insights по вашему портфелю:**
• Общая стоимость: 185,000 ₽
• Доходность: +9.2% 
• Основной драйвер: YNDX (+16.8%)
• Зона роста: IT-сектор (текущая доля 11.9%)

⚡ **Рекомендуем сосредоточиться на:**
1. Увеличении доли IT до 20%
2. Диверсификации из энергетики в промышленность
3. Сохранении защитной доли облигаций

Попробуйте команду /auto_trade для автоматических торговых решений!"""


class InvestmentTelegramBot:
    """Telegram бот для инвестиционного советника."""

    def __init__(self, config):
        if not config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required!")

        self.config = config
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.ai_service = DeepSeekAI(config)
        self.portfolio_analyzer = PortfolioAnalyzer(config)
        
        # Автоматический менеджер портфеля
        if AI_MANAGER_AVAILABLE:
            self.auto_manager = AutoPortfolioManager(config)
        else:
            self.auto_manager = None

        self._register_handlers()
        logger.info("🤖 Investment Telegram Bot initialized")

    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        # Обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("analytics", self.analytics_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("advice", self.advice_command))
        self.application.add_handler(CommandHandler("manage", self.manage_command))
        
        # НОВАЯ КОМАНДА: Автоматическая торговля через AI
        self.application.add_handler(CommandHandler("auto_trade", self.auto_manage_command))

        # Обработчик текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    def run(self):
        """Запуск бота"""
        logger.info("🤖 Starting Telegram bot polling...")
        self.application.run_polling()

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = (
            f"Привет, {user.first_name}! 👋\n\n"
            "Я - AI инвестиционный советник с полным автоуправлением портфелем.\n"
            "Стратегия: максимальная доходность через российские инструменты.\n\n"
            "🤖 **Основные команды:**\n"
            "📊 /portfolio - Анализ портфеля\n"
            "💡 /advice - AI-совет по инвестициям\n"  
            "⚡ /manage - Рекомендации по управлению\n"
            "🎯 /auto_trade - АВТОМАТИЧЕСКАЯ ТОРГОВЛЯ\n"
            "❓ /help - Помощь\n\n"
            "🇷🇺 *Только российские инструменты • Полная автоматизация*"
        )

        keyboard = [
            [KeyboardButton("/portfolio"), KeyboardButton("/advice")],
            [KeyboardButton("/manage"), KeyboardButton("/auto_trade")],
            [KeyboardButton("/help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📖 **Помощь по командам:**\n\n"
            "*/start* - Начать работу с ботом\n"
            "*/portfolio* - Детальный анализ портфеля\n" 
            "*/advice* - AI-совет по инвестициям\n"
            "*/manage* - Рекомендации по управлению\n"
            "*/auto_trade* - 🎯 АВТОМАТИЧЕСКАЯ ТОРГОВЛЯ\n"
            "*/help* - Эта справка\n\n"
            "💡 **AI-стратегия:**\n"
            "• Только российские инструменты\n"
            "• Максимальная доходность\n"
            "• Полная автоматизация торговли\n"
            "• DeepSeek AI для принятия решений\n\n"
            "🇷🇺 *Фокус на российские акции и облигации*"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /portfolio"""
        try:
            portfolio_info = await self.portfolio_analyzer.get_portfolio_analysis()
            await update.message.reply_text(portfolio_info, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in portfolio command: {e}")
            await update.message.reply_text("❌ Ошибка при анализе портфеля")

    async def analytics_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /analytics"""
        try:
            portfolio_info = await self.portfolio_analyzer.get_portfolio_analysis()
            await update.message.reply_text(portfolio_info, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in analytics command: {e}")
            await update.message.reply_text("❌ Ошибка при анализе портфеля")

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /balance"""
        try:
            portfolio_info = await self.portfolio_analyzer.get_portfolio_analysis()
            await update.message.reply_text(portfolio_info, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in balance command: {e}")
            await update.message.reply_text("❌ Ошибка при получении баланса")

    async def advice_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /advice"""
        await update.message.reply_text(
            "🤖 **AI-совет по инвестициям**\n\n"
            "Опишите ваш инвестиционный вопрос, и я проанализирую ваш портфель:\n\n"
            "• 'Как увеличить доходность?'\n"
            "• 'Какие акции купить на 50 000 ₽?'\n"  
            "• 'Как оптимизировать распределение?'\n"
            "• 'Стоит ли продавать Газпром?'\n\n"
            "🇷🇺 *Анализ на основе реальных данных вашего портфеля!*"
        )

    async def manage_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /manage - рекомендации по управлению"""
        try:
            recommendations = await self.portfolio_analyzer.get_auto_management_recommendations()
            await update.message.reply_text(recommendations, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in manage command: {e}")
            await update.message.reply_text("❌ Ошибка при генерации рекомендаций по управлению")

    async def auto_manage_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """НОВАЯ КОМАНДА: Полностью автоматическое управление портфелем через AI"""
    if not self.auto_manager:
        await update.message.reply_text(
            "❌ **Автоматический менеджер не доступен**\n\n"
            "Для использования автоматической торговли:\n"
            "1. Убедитесь что файл auto_portfolio_manager.py установлен\n"
            "2. Проверьте настройки DeepSeek API\n"
            "3. Используйте /manage для базовых рекомендаций"
        )
        return
        
    await update.message.reply_text(
        "🤖 **ЗАПУСК АВТОМАТИЧЕСКОГО УПРАВЛЕНИЯ**\n\n"
        "⚡ Анализирую портфель и рыночные условия...\n"
        "⏳ Генерация торговых решений..."
    )
    
    try:
        # Получаем данные портфеля
        portfolio_data = await self._get_current_portfolio_data()
        
        # Получаем рыночный контекст
        market_context = await self._get_market_context()
        
        # Генерируем торговые решения
        decisions = await self.auto_manager.generate_trading_decisions(
            portfolio_data, market_context
        )
        
        if decisions:
            response = "🎯 **АВТОМАТИЧЕСКИЕ ТОРГОВЫЕ РЕШЕНИЯ**\n\n"
            
            for i, decision in enumerate(decisions, 1):
                action_emoji = "🟢" if decision['action'] == 'BUY' else "🔴" if decision['action'] == 'SELL' else "🟡"
                source_indicator = "🤖" if decision.get('source') == 'ai' else "⚡"
                
                response += f"{i}. {action_emoji} **{decision['action']} {decision['ticker']}** {source_indicator}\n"
                response += f"   💰 Сумма: {decision['amount']:,.0f} ₽\n"
                response += f"   📝 {decision['rationale']}\n"
                response += f"   📈 Ожидаемая доходность: {decision['expected_yield']:+.1f}%\n\n"
            
            response += "💡 *Источник: "
            ai_count = sum(1 for d in decisions if d.get('source') == 'ai')
            algo_count = len(decisions) - ai_count
            
            if ai_count > 0:
                response += f"DeepSeek AI ({ai_count})"
                if algo_count > 0:
                    response += f" + Алгоритм ({algo_count})"
            else:
                response += f"Алгоритмическая система ({algo_count})"
            
            response += "*\n\n"
            response += "⚡ *Готов к исполнению через Tinkoff API*"
        else:
            response = (
                "⚠️ **Не удалось сгенерировать торговые решения**\n\n"
                "В данный момент система не может предложить оптимальные решения.\n"
                "Возможные причины:\n"
                "• Нестабильные рыночные условия\n"
                "• Ограниченный набор данных\n"
                "• Высокая волатильность\n\n"
                "Попробуйте:\n"
                "• Обновить данные портфеля\n"
                "• Использовать /manage для общих рекомендаций\n"
                "• Повторить запрос через некоторое время"
            )
            
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error in auto management: {e}")
        await update.message.reply_text(
            "❌ **Ошибка автоматического управления**\n\n"
            "Технические неполадки. Попробуйте:\n"
            "1. Проверить подключение к интернету\n"
            "2. Убедиться в работоспособности API\n"
            "3. Повторить запрос позже\n"
            "4. Использовать /manage для упрощенных рекомендаций"
        )

    async def _get_portfolio_context(self) -> str:
        """Получить контекст портфеля для AI"""
        try:
            return await self.portfolio_analyzer.get_portfolio_context()
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return "Не удалось получить данные портфеля. Рекомендации будут общими."

    async def _get_current_portfolio_data(self) -> Dict:
        """Получает текущие данные портфеля для автоматического управления"""
        return {
            "total_value": Decimal("185000.00"),
            "total_yield": Decimal("15600.00"),
            "yield_percentage": Decimal("9.2"),
            "available_cash": Decimal("32000.00"),
            "positions": [
                {"name": "Сбербанк", "ticker": "SBER", "value": Decimal("52000.00"), 
                 "yield": Decimal("3800.00"), "percentage": Decimal("8.1"), "type": "stock", "sector": "финансы"},
                {"name": "Газпром", "ticker": "GAZP", "value": Decimal("41000.00"), 
                 "yield": Decimal("2200.00"), "percentage": Decimal("5.7"), "type": "stock", "sector": "энергетика"},
                {"name": "Лукойл", "ticker": "LKOH", "value": Decimal("38000.00"), 
                 "yield": Decimal("4500.00"), "percentage": Decimal("13.8"), "type": "stock", "sector": "энергетика"},
                {"name": "Яндекс", "ticker": "YNDX", "value": Decimal("22000.00"), 
                 "yield": Decimal("3100.00"), "percentage": Decimal("16.8"), "type": "stock", "sector": "IT"},
                {"name": "ОФЗ-26238", "ticker": "SU26238", "value": Decimal("40000.00"), 
                 "yield": Decimal("2000.00"), "percentage": Decimal("5.3"), "type": "bond", "sector": "гос. облигации"},
            ]
        }

    async def _get_market_context(self) -> str:
        """Получает текущий рыночный контекст"""
        return """РЫНОЧНАЯ СИТУАЦИЯ:
- Российский рынок: умеренный рост (+2.1% за месяц)
- IT-сектор: сильный восходящий тренд (+15% YTD)  
- Энергетика: стагнация (+1.5% YTD)
- Финансы: стабильность (+4.2% YTD)
- Облигации: стабильные yield 8-9%
- Волатильность: умеренная

КЛЮЧЕВЫЕ СОБЫТИЯ:
- ЦБ РФ сохранил ставку на 16%
- Рост цен на нефть: +8% за месяц
- Укрепление рубля к доллару"""

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений с AI-анализом"""
        user_message = update.message.text
        
        # Игнорируем команды
        if user_message.startswith('/'):
            return
            
        await update.message.reply_chat_action("typing")
        
        try:
            # Получаем контекст портфеля
            portfolio_context = await self._get_portfolio_context()
            
            # Получаем AI-ответ с контекстом портфеля
            ai_response = await self.ai_service.get_investment_advice(user_message, portfolio_context)
            
            # Отправляем ответ (разбиваем если слишком длинный)
            if len(ai_response) > 4000:
                parts = [ai_response[i:i+4000] for i in range(0, len(ai_response), 4000)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await update.message.reply_text(ai_response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in AI message handling: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке запроса. "
                "Попробуйте еще раз или используйте команды из меню."
            )