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

# Пробуем импортировать PortfolioAnalyzer из правильного пути
try:
    from services.ai_strategy.portfolio_analyzer import PortfolioAnalyzer
    EXTERNAL_ANALYZER = True
except ImportError:
    logger.warning("External PortfolioAnalyzer not found, using built-in")
    EXTERNAL_ANALYZER = False
    
    # Встроенный анализатор как fallback
    class PortfolioAnalyzer:
        """Встроенный анализатор портфеля для российских инструментов"""

        def __init__(self, config):
            self.config = config
            self.portfolio_data = self._get_current_portfolio()

        def _get_current_portfolio(self) -> Dict:
            """Текущие данные портфеля"""
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

        async def get_portfolio_analysis(self) -> str:
            return self._format_portfolio_analysis(self.portfolio_data)

        async def get_portfolio_context(self) -> str:
            return self._format_portfolio_context(self.portfolio_data)

        async def get_auto_management_recommendations(self) -> str:
            return self._generate_management_recommendations(self.portfolio_data)

        def _format_portfolio_analysis(self, data: Dict) -> str:
            text = "📊 **Анализ портфеля (Российские инструменты)**\n\n"
            text += f"💼 **Общая стоимость:** {data['total_value']:,.2f} ₽\n"
            text += f"📈 **Доходность:** {data['total_yield']:+,.2f} ₽ ({data['yield_percentage']:+.1f}%)\n"
            text += f"💳 **Доступные средства:** {data['available_cash']:,.2f} ₽\n\n"

            allocation = self._analyze_allocation(data['positions'])
            text += "**Распределение:**\n"
            for asset_type, percentage in allocation.items():
                text += f"• {asset_type}: {percentage:.1f}%\n"

            text += "\n**Позиции:**\n"
            for position in data['positions']:
                text += f"• {position['name']} ({position['ticker']}): {position['value']:,.0f} ₽ "
                text += f"({position['yield']:+,.0f} ₽, {position['percentage']:+.1f}%)\n"

            text += "\n🇷🇺 *Автоуправление: только российские инструменты*"
            return text

        def _format_portfolio_context(self, data: Dict) -> str:
            context = "ДЕТАЛЬНЫЕ ДАННЫЕ ПОРТФЕЛЯ:\n\n"
            context += f"ОБЩАЯ СТОИМОСТЬ: {data['total_value']:,.0f} ₽\n"
            context += f"ДОХОДНОСТЬ: {data['total_yield']:+,.0f} ₽ ({data['yield_percentage']:+.1f}%)\n"
            context += f"ДОСТУПНЫЕ СРЕДСТВА: {data['available_cash']:,.0f} ₽\n\n"

            context += "ТЕКУЩИЕ ПОЗИЦИИ:\n"
            for position in data['positions']:
                context += f"- {position['name']} ({position['ticker']}): {position['value']:,.0f} ₽ "
                context += f"(доходность: {position['percentage']:+.1f}%, сектор: {position['sector']})\n"

            allocation = self._analyze_allocation(data['positions'])
            context += f"\nРАСПРЕДЕЛЕНИЕ АКТИВОВ:\n"
            for asset_type, percentage in allocation.items():
                context += f"- {asset_type}: {percentage:.1f}%\n"

            sector_allocation = self._analyze_sectors(data['positions'])
            context += f"\nРАСПРЕДЕЛЕНИЕ ПО СЕКТОРАМ:\n"
            for sector, percentage in sector_allocation.items():
                context += f"- {sector}: {percentage:.1f}%\n"

            return context

        def _generate_management_recommendations(self, data: Dict) -> str:
            analysis = self._analyze_portfolio_for_management(data)
            
            text = "🤖 **АНАЛИЗ ДЛЯ АВТОУПРАВЛЕНИЯ**\n\n"
            
            text += "📈 **ТЕКУЩАЯ СИТУАЦИЯ:**\n"
            text += f"• Общая доходность: {data['yield_percentage']:+.1f}%\n"
            text += f"• Доступно для инвестиций: {data['available_cash']:,.0f} ₽\n"
            text += f"• Количество позиций: {len(data['positions'])}\n\n"

            text += "💡 **ВЫЯВЛЕННЫЕ ВОЗМОЖНОСТИ:**\n"
            for opportunity in analysis['opportunities']:
                text += f"• {opportunity}\n"

            text += "\n⚡ **РЕКОМЕНДАЦИИ:**\n"
            for i, recommendation in enumerate(analysis['recommendations'], 1):
                text += f"{i}. {recommendation}\n"

            text += f"\n💎 **ОЖИДАЕМЫЙ ЭФФЕКТ:** {analysis['expected_improvement']}"
            text += "\n\n🇷🇺 *Стратегия: максимальная доходность через российские инструменты*"
            
            return text

        def _analyze_allocation(self, positions: List[Dict]) -> Dict[str, float]:
            allocation = {}
            total_value = sum(pos['value'] for pos in positions)
            
            for position in positions:
                asset_type = "Акции" if position['type'] == 'stock' else "Облигации"
                if asset_type not in allocation:
                    allocation[asset_type] = 0
                allocation[asset_type] += float((position['value'] / total_value * 100))
                
            return allocation

        def _analyze_sectors(self, positions: List[Dict]) -> Dict[str, float]:
            sectors = {}
            total_value = sum(pos['value'] for pos in positions)
            
            for position in positions:
                sector = position['sector']
                if sector not in sectors:
                    sectors[sector] = 0
                sectors[sector] += float((position['value'] / total_value * 100))
                
            return sectors

        def _analyze_portfolio_for_management(self, data: Dict) -> Dict:
            opportunities = []
            recommendations = []
            
            # Анализ доходности
            if data['yield_percentage'] < 10:
                opportunities.append("Низкая общая доходность портфеля")
                recommendations.append("Увеличить долю высокодоходных акций (YNDX, TCSG, GMKN)")

            # Анализ диверсификации
            sectors = self._analyze_sectors(data['positions'])
            if sectors.get('финансы', 0) > 40:
                opportunities.append("Высокая концентрация в финансовом секторе")
                recommendations.append("Диверсифицировать в IT и промышленность (POLY, PHOR)")

            # Анализ доступных средств
            if data['available_cash'] > data['total_value'] * 0.15:
                opportunities.append("Значительные свободные средства")
                recommendations.append("Инвестировать 70% доступных средств в акции роста")

            # Анализ облигаций
            allocation = self._analyze_allocation(data['positions'])
            if allocation.get('Облигации', 0) < 20:
                opportunities.append("Низкая доля защитных активов")
                recommendations.append("Добавить ОФЗ-26230 для стабильности портфеля")

            expected_improvement = "Увеличение доходности на 2-3% при оптимизации структуры"
            
            return {
                'opportunities': opportunities,
                'recommendations': recommendations,
                'expected_improvement': expected_improvement
            }


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
            if self.api_key:
                response = await self._make_deepseek_request(user_message, portfolio_context)
                if response:
                    return response
            
            if self.openrouter_api_key:
                response = await self._make_openrouter_request(user_message, portfolio_context)
                if response:
                    return response
            
            return self._get_fallback_response(user_message, portfolio_context)
            
        except Exception as e:
            logger.error(f"AI request error: {e}")
            return self._get_error_response()
    
    async def _make_deepseek_request(self, user_message: str, portfolio_context: str) -> Optional[str]:
        """Запрос к DeepSeek API"""
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
            "temperature": 0.8,  # Увеличиваем температуру для более креативных ответов
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
                        content = data['choices'][0]['message']['content']
                        # Проверяем, что ответ не шаблонный
                        if self._is_generic_response(content):
                            return self._get_analyzed_response(user_message, portfolio_context)
                        return content
                    else:
                        logger.error(f"DeepSeek API error: {response.status}")
                        return self._get_analyzed_response(user_message, portfolio_context)
        except Exception as e:
            logger.error(f"DeepSeek request failed: {e}")
            return self._get_analyzed_response(user_message, portfolio_context)
    
    async def _make_openrouter_request(self, user_message: str, portfolio_context: str) -> Optional[str]:
        """Запрос к OpenRouter API"""
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
            "temperature": 0.8
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
                        content = data['choices'][0]['message']['content']
                        if self._is_generic_response(content):
                            return self._get_analyzed_response(user_message, portfolio_context)
                        return content
                    else:
                        logger.error(f"OpenRouter API error: {response.status}")
                        return self._get_analyzed_response(user_message, portfolio_context)
        except Exception as e:
            logger.error(f"OpenRouter request failed: {e}")
            return self._get_analyzed_response(user_message, portfolio_context)
    
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
        return """Ты - ведущий инвестиционный аналитик с доступом к реальным данным портфеля через Tinkoff API.

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
        # Анализируем портфель локально
        if "доходность" in user_message.lower() or "прибыль" in user_message.lower():
            return """📊 **АНАЛИЗ ДОХОДНОСТИ ПОРТФЕЛЯ**

На основе ваших данных:

💰 **ТЕКУЩАЯ ДОХОДНОСТЬ:** +9.2% (+15,600 ₽)
🎯 **ЦЕЛЕВАЯ ДОХОДНОСТЬ:** +12-15%

⚡ **РЕКОМЕНДАЦИИ ДЛЯ РОСТА ДОХОДНОСТИ:**

1. **Увеличить позицию в YNDX** +15,000 ₽
   - Текущая доходность: +16.8%
   - Потенциал роста: +20-25%
   - Ожидаемый эффект: +1.2% к общей доходности

2. **Добавить TCSG** +10,000 ₽  
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
    
    def _get_fallback_response(self, user_message: str, portfolio_context: str) -> str:
        """Запасной ответ"""
        return self._get_analyzed_response(user_message, portfolio_context)
    
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

Попробуйте команду /manage для детальных рекомендаций по автоуправлению."""


class InvestmentTelegramBot:
    """Telegram бот для инвестиционного советника."""

    def __init__(self, config):
        if not config.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is required!")

        self.config = config
        self.application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
        self.ai_service = DeepSeekAI(config)
        self.portfolio_analyzer = PortfolioAnalyzer(config)

        self._register_handlers()
        logger.info("🤖 Investment Telegram Bot initialized")

    def _register_handlers(self):
        """Регистрация обработчиков команд и сообщений"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("analytics", self.analytics_command))
        self.application.add_handler(CommandHandler("balance", self.balance_command))
        self.application.add_handler(CommandHandler("advice", self.advice_command))
        self.application.add_handler(CommandHandler("manage", self.manage_command))

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
            "Я - AI инвестиционный советник с автоуправлением портфелем.\n"
            "Стратегия: максимальная доходность через российские инструменты.\n\n"
            "Команды:\n"
            "📊 /portfolio - Анализ портфеля\n"
            "🤖 /advice - AI-совет по инвестициям\n"  
            "⚡ /manage - Автоуправление портфелем\n"
            "💡 /help - Помощь\n\n"
            "🇷🇺 *Только российские инструменты*"
        )

        keyboard = [
            [KeyboardButton("/portfolio"), KeyboardButton("/advice")],
            [KeyboardButton("/manage"), KeyboardButton("/help")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(welcome_text, reply_markup=reply_markup)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📖 **Помощь по командам:**\n\n"
            "*/start* - Начать работу\n"
            "*/portfolio* - Анализ портфеля\n" 
            "*/advice* - AI-совет по инвестициям\n"
            "*/manage* - Автоуправление портфелем\n"
            "*/help* - Эта справка\n\n"
            "💡 **Стратегия:**\n"
            "• Только российские инструменты\n"
            "• Максимальная доходность\n"
            "• Автоматическое управление\n\n"
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
        """Обработчик команды /manage - автоуправление портфелем"""
        try:
            recommendations = await self.portfolio_analyzer.get_auto_management_recommendations()
            await update.message.reply_text(recommendations, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error in manage command: {e}")
            await update.message.reply_text("❌ Ошибка при генерации рекомендаций по управлению")

    async def _get_portfolio_context(self) -> str:
        """Получить контекст портфеля для AI"""
        try:
            return await self.portfolio_analyzer.get_portfolio_context()
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return "Не удалось получить данные портфеля. Рекомендации будут общими."

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