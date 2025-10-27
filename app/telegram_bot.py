"""
Telegram bot for Investment Advisor with Tinkoff API integration
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.loader import get_tinkoff_client

logger = logging.getLogger(__name__)

class InvestmentTelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"START from {user.first_name} (ID: {user.id})")
        
        welcome_text = f"""
🤖 Привет, {user.first_name}!

Я - ваш персональный инвестиционный советник с AI-ассистентом.

📊 **Доступные команды:**
/start - Начать работу
/portfolio - Анализ вашего портфеля
/accounts - Список счетов
/help - Помощь по командам

💬 **Также можете задавать вопросы:**
- "Проанализируй мой портфель"
- "Какие акции купить?"
- "Что с рынком сегодня?"

Начните с команды /portfolio для анализа ваших инвестиций!
        """
        
        await update.message.reply_text(welcome_text)

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command with real Tinkoff data"""
        user = update.effective_user
        logger.info(f"PORTFOLIO from {user.first_name}")
        
        try:
            # Get Tinkoff client
            tinkoff_client = get_tinkoff_client()
            
            await update.message.reply_text("📊 Загружаю данные портфеля...")
            
            # Get accounts
            accounts_response = tinkoff_client.get_accounts()
            if not accounts_response.accounts:
                await update.message.reply_text("❌ Не найдено инвестиционных счетов")
                return
            
            account_id = accounts_response.accounts[0].id
            
            # Get portfolio
            portfolio = tinkoff_client.get_portfolio(account_id)
            
            # Format portfolio info
            total_shares = portfolio.total_amount_shares.units if portfolio.total_amount_shares else 0
            total_bonds = portfolio.total_amount_bonds.units if portfolio.total_amount_bonds else 0
            total_etf = portfolio.total_amount_etf.units if portfolio.total_amount_etf else 0
            total_currencies = portfolio.total_amount_currencies.units if portfolio.total_amount_currencies else 0
            
            total_value = total_shares + total_bonds + total_etf + total_currencies
            
            portfolio_text = f"""
📈 **Анализ вашего портфеля:**

💰 **Общая стоимость:** {total_value:,} руб.
├─ Акции: {total_shares:,} руб.
├─ Облигации: {total_bonds:,} руб.
├─ ETF: {total_etf:,} руб.
└─ Валюта: {total_currencies:,} руб.

🏢 **Позиций:** {len(portfolio.positions) if portfolio.positions else 0}

🎯 **Рекомендации AI:**
Портфель успешно загружен! Используйте AI-анализ для детальных рекомендаций.
            """
            
            await update.message.reply_text(portfolio_text)
            logger.info(f"Sent portfolio to {user.id}: {total_value} руб.")
            
        except Exception as e:
            logger.error(f"Portfolio error: {e}")
            await update.message.reply_text(
                "❌ Ошибка при загрузке портфеля. Проверьте настройки Tinkoff API."
            )

    async def accounts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /accounts command"""
        try:
            tinkoff_client = get_tinkoff_client()
            accounts_response = tinkoff_client.get_accounts()
            
            if not accounts_response.accounts:
                await update.message.reply_text("❌ Не найдено счетов")
                return
            
            accounts_text = "📋 **Ваши счета:**\n\n"
            for i, account in enumerate(accounts_response.accounts, 1):
                accounts_text += f"{i}. {account.name or 'Счет'} ({account.id[:8]}...)\n"
                if hasattr(account, 'status'):
                    accounts_text += f"   Статус: {account.status}\n"
                accounts_text += "\n"
            
            await update.message.reply_text(accounts_text)
            
        except Exception as e:
            logger.error(f"Accounts error: {e}")
            await update.message.reply_text("❌ Ошибка при загрузке счетов")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📋 **Помощь по командам:**

/start - Начать работу с ботом
/portfolio - Получить анализ инвестиционного портфеля
/accounts - Показать список счетов
/help - Показать это сообщение

💬 **Примеры вопросов для AI:**
• "Какая доходность у моего портфеля?"
• "Что купить для диверсификации?"
• "Какой прогноз по рублю?"

🤖 **AI-ассистент** поможет с анализом и рекомендациями!
        """
        
        await update.message.reply_text(help_text)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages with AI response"""
        user_message = update.message.text
        user = update.effective_user
        
        logger.info(f"Message from {user.first_name}: {user_message}")
        
        # Simple AI responses
        if any(word in user_message.lower() for word in ['привет', 'hello', 'hi', 'хай']):
            response = f"Привет, {user.first_name}! Рад вас видеть! 🤗"
        elif any(word in user_message.lower() for word in ['портфель', 'портфолио', 'инвестиц']):
            response = "Для детального анализа портфеля используйте команду /portfolio 📊"
        elif any(word in user_message.lower() for word in ['счет', 'счета', 'аккаунт']):
            response = "Для просмотра счетов используйте /accounts 📋"
        elif any(word in user_message.lower() for word in ['акци', 'акция', 'stock']):
            response = "📈 Для анализа акций используйте /portfolio или задайте конкретный вопрос!"
        elif any(word in user_message.lower() for word in ['доходность', 'прибыль', 'профит']):
            response = "📊 Анализ доходности доступен в команде /portfolio"
        elif any(word in user_message.lower() for word in ['спасибо', 'thanks', 'thank you']):
            response = "Всегда рад помочь! 🚀"
        else:
            response = (
                f"🤖 AI-анализ: Ваш вопрос '{user_message}' передан для обработки.\n\n"
                "Пока что я умею:\n"
                "• Анализировать портфель (/portfolio)\n"  
                "• Показывать счета (/accounts)\n"
                "• Отвечать на базовые вопросы\n\n"
                "Скоро будет полноценный AI-ассистент!"
            )
        
        await update.message.reply_text(response)

    def setup_handlers(self):
        """Setup all command handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("portfolio", self.portfolio_command))
        self.application.add_handler(CommandHandler("accounts", self.accounts_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

    def run(self):
        """Run the bot"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
            return
        
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("🤖 Investment Advisor Bot starting...")
        print("=" * 60)
        print("🤖 INVESTMENT ADVISOR BOT")
        print("=" * 60)
        print("📍 Бот запущен и слушает сообщения...")
        print("💬 Откройте Telegram и отправьте команды:")
        print("   /start - начать работу")
        print("   /portfolio - анализ портфеля") 
        print("   /accounts - список счетов")
        print("   /help - помощь")
        print("⏹️  Нажмите Ctrl+C для остановки")
        print("-" * 60)
        
        # Run polling
        self.application.run_polling(drop_pending_updates=True)

        """
Telegram bot with DeepSeek AI integration
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from app.loader import get_tinkoff_client
from app.ai_deepseek import get_deepseek_ai

logger = logging.getLogger(__name__)

class InvestmentTelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.application = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"START from {user.first_name}")
        
        welcome_text = f"""
🤖 Привет, {user.first_name}!

Я - ваш персональный инвестиционный советник с AI-ассистентом.

📊 **Доступные команды:**
/start - Начать работу
/portfolio - Анализ портфеля + AI
/accounts - Список счетов
/analysis - AI анализ рынка
/help - Помощь

💬 **Задавайте вопросы:**
- "Стоит ли покупать акции?"
- "Как диверсифицировать портфель?"
- "Что с рынком сегодня?"
        """
        
        await update.message.reply_text(welcome_text)

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command with AI analysis"""
        user = update.effective_user
        logger.info(f"PORTFOLIO from {user.first_name}")
        
        try:
            tinkoff_client = get_tinkoff_client()
            
            await update.message.reply_text("📊 Загружаю данные портфеля...")
            
            # Get portfolio data
            accounts_response = tinkoff_client.get_accounts()
            if not accounts_response.accounts:
                await update.message.reply_text("❌ Не найдено инвестиционных счетов")
                return
            
            account_id = accounts_response.accounts[0].id
            portfolio = tinkoff_client.get_portfolio(account_id)
            
            # Extract portfolio data
            total_shares = portfolio.total_amount_shares.units if portfolio.total_amount_shares else 0
            total_bonds = portfolio.total_amount_bonds.units if portfolio.total_amount_bonds else 0
            total_etf = portfolio.total_amount_etf.units if portfolio.total_amount_etf else 0
            total_currencies = portfolio.total_amount_currencies.units if portfolio.total_amount_currencies else 0
            
            total_value = total_shares + total_bonds + total_etf + total_currencies
            
            # Send basic portfolio info first
            portfolio_text = f"""
📈 **Ваш портфель:**

💰 **Общая стоимость:** {total_value:,} руб.
├─ Акции: {total_shares:,} руб.
├─ Облигации: {total_bonds:,} руб.
├─ ETF: {total_etf:,} руб.
└─ Валюта: {total_currencies:,} руб.

🔄 Запрашиваю AI-анализ...
            """
            
            await update.message.reply_text(portfolio_text)
            
            # Get AI analysis
            ai_client = await get_deepseek_ai()
            
            portfolio_data = {
                'total_value': total_value,
                'stocks_value': total_shares,
                'bonds_value': total_bonds,
                'etf_value': total_etf,
                'positions_count': len(portfolio.positions) if portfolio.positions else 0
            }
            
            ai_analysis = await ai_client.analyze_portfolio(portfolio_data)
            
            # Send AI analysis
            analysis_text = f"""
🎯 **AI Анализ:**

{ai_analysis}

💡 *Анализ предоставлен DeepSeek AI*
            """
            
            await update.message.reply_text(analysis_text)
            logger.info(f"Sent portfolio + AI analysis to {user.id}")
            
        except Exception as e:
            logger.error(f"Portfolio error: {e}")
            await update.message.reply_text("❌ Ошибка при анализе портфеля")

    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /analysis command for market analysis"""
        try:
            await update.message.reply_text("📈 Запрашиваю анализ рынка...")
            
            ai_client = await get_deepseek_ai()
            market_analysis = await ai_client.get_market_analysis()
            
            analysis_text = f"""
🌍 **Анализ рынка:**

{market_analysis}

💡 *Анализ предоставлен DeepSeek AI*
            """
            
            await update.message.reply_text(analysis_text)
            
        except Exception as e:
            logger.error(f"Market analysis error: {e}")
            await update.message.reply_text("❌ Ошибка при анализе рынка")

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages with AI"""
        user_message = update.message.text
        user = update.effective_user
        
        logger.info(f"AI Message from {user.first_name}: {user_message}")
        
        # Simple responses for common questions
        simple_responses = {
            'привет': f"Привет, {user.first_name}! 🤗",
            'hello': f"Hello, {user.first_name}! 👋",
            'как дела': "Отлично! Готов помочь с инвестициями! 💼",
            'start': "Используйте /start для начала работы",
            'help': "Используйте /help для списка команд",
            'портфель': "Используйте /portfolio для анализа портфеля",
            'анализ': "Используйте /analysis для анализа рынка"
        }
        
        message_lower = user_message.lower()
        for key, response in simple_responses.items():
            if key in message_lower:
                await update.message.reply_text(response)
                return
        
        # For other messages, use AI
        try:
            await update.message.reply_text("🤔 Думаю над ответом...")
            
            ai_client = await get_deepseek_ai()
            ai_response = await ai_client.generate_response(
                user_message,
                "Ты - инвестиционный советник. Отвечай кратко и по делу."
            )
            
            await update.message.reply_text(f"🤖 {ai_response}")
            
        except Exception as e:
            logger.error(f"AI message error: {e}")
            await update.message.reply_text(
                "❌ Ошибка AI сервиса. Попробуйте позже или используйте команды."
            )

    # ... остальные методы (setup_handlers, run и т.д.) остаются без изменений