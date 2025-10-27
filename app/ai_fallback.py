"""
Fallback AI responses when external AI services are unavailable
"""
import logging

logger = logging.getLogger(__name__)

class FallbackAI:
    """Fallback AI with predefined investment responses"""
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate fallback response for investment questions"""
        prompt_lower = prompt.lower()
        
        # Investment portfolio analysis
        if any(word in prompt_lower for word in ['портфель', 'портфолио', 'инвестиц']):
            return """
📊 **Анализ портфеля:**

💼 **Рекомендуемая структура:**
• Акции роста: 50-60%
• Облигации: 20-30%
• ETF: 10-20%
• Денежные средства: 5-10%

🎯 **Советы:**
1. Диверсифицируйте по секторам
2. Добавьте международные активы
3. Регулярно ребалансируйте портфель
4. Учитывайте свою толерантность к риску

💡 *Для точного анализа подключите AI-сервис*
            """
        
        # Stock market questions
        elif any(word in prompt_lower for word in ['акци', 'акция', 'stock', 'рынок']):
            return """
📈 **Анализ рынка акций:**

🔍 **Перспективные сектора:**
• Технологии и AI
• Зеленая энергетика  
• Здравоохранение
• Потребительские товары

⚡ **Рекомендации:**
• Изучайте фундаментальные показатели
• Диверсифицируйте вложения
• Рассмотрите ETF для широкого покрытия
• Следите за дивидендной политикой

📅 *Актуальный анализ требует подключения к AI*
            """
        
        # Bonds and fixed income
        elif any(word in prompt_lower for word in ['облигац', 'бонд', 'bond', 'доходность']):
            return """
💰 **Облигации и доходность:**

📊 **Типы облигаций:**
• Государственные (ОФЗ) - низкий риск
• Корпоративные - средний риск
• Муниципальные - региональные

📈 **Доходность:**
• ОФЗ: 6-9% годовых
• Корпоративные: 8-12% годовых
• Валютные: 3-5% годовых

🛡️ **Преимущества:**
• Предсказуемый доход
• Меньшая волатильность
• Регулярные выплаты

💡 *Для персональных рекомендаций нужен AI-анализ*
            """
        
        # General investment advice
        elif any(word in prompt_lower for word in ['совет', 'рекомендац', 'купить', 'продать']):
            return """
🎯 **Общие инвестиционные принципы:**

1. **Диверсификация** - не кладите все яйца в одну корзину
2. **Долгосрочность** - инвестируйте на перспективу
3. **Регулярность** - постоянные вложения лучше разовых
4. **Образование** - изучайте финансовые инструменты

📊 **Начните с:**
• ETF на широкий рынок
• Качественные облигации
• Постепенное обучение акциям

🤖 *Для персонализированных советов подключите AI-сервис*
            """
        
        # Market analysis
        elif any(word in prompt_lower for word in ['анализ рынка', 'market analysis', 'тренд']):
            return """
🌍 **Обзор финансовых рынков:**

📅 **Ключевые факторы:**
• Денежная политика ЦБ
• Макроэкономические показатели
• Геополитическая ситуация
• Корпоративные отчеты

🔮 **Общие тренды:**
• Рост интереса к AI и технологиям
• Стабилизация сырьевых рынков
• Поиск доходности в условиях неопределенности

💡 *Актуальный анализ требует подключения к AI-сервису*
            """
        
        # Greetings and general questions
        elif any(word in prompt_lower for word in ['привет', 'hello', 'hi', 'хай']):
            return "🤖 Привет! Я ваш инвестиционный советник. Задавайте вопросы об инвестициях, портфеле или рынке!"
        
        elif any(word in prompt_lower for word in ['помощь', 'help', 'команды']):
            return """
📋 **Доступные возможности:**

💼 **Анализ портфеля** - структура и рекомендации
📈 **Рынок акций** - перспективные направления  
💰 **Облигации** - доходность и риски
🎯 **Советы** - общие принципы инвестирования

🔧 *Для расширенного AI-анализа подключите внешние сервисы*
            """
        
        else:
            return f"""
🤖 **Инвестиционный советник:**

Ваш вопрос: "{prompt}"

💡 Я могу помочь с:
• Анализом структуры портфеля
• Рекомендациями по диверсификации  
• Общими принципами инвестирования
• Обзором рынков и инструментов

🔌 *Для точного AI-анализа необходимо подключение к внешним сервисам*

📞 Обратитесь к финансовому консультанту для персональных рекомендаций.
            """
    
    async def analyze_portfolio(self, portfolio_data: dict) -> str:
        """Analyze portfolio with fallback responses"""
        total_value = portfolio_data.get('total_value', 0)
        stocks_value = portfolio_data.get('stocks_value', 0)
        bonds_value = portfolio_data.get('bonds_value', 0)
        positions_count = portfolio_data.get('positions_count', 0)
        
        if total_value > 0:
            stocks_pct = (stocks_value / total_value) * 100
            bonds_pct = (bonds_value / total_value) * 100
            
            advice = self._get_portfolio_advice(stocks_pct, bonds_pct, positions_count)
            
            return f"""
📊 **Анализ вашего портфеля:**

💰 **Общая стоимость:** {total_value:,} руб.
• Акции: {stocks_pct:.1f}% ({stocks_value:,} руб.)
• Облигации: {bonds_pct:.1f}% ({bonds_value:,} руб.)
• Позиций: {positions_count}

🎯 **Рекомендации:**
{advice}

💡 *Для детального AI-анализа подключите внешние сервисы*
            """
        else:
            return """
💼 **Начало инвестирования:**

🎯 **Рекомендуемая стратегия:**
1. Начните с ETF на широкий рынок
2. Добавьте надежные облигации
3. Постепенно изучайте отдельные акции
4. Сформируйте emergency fund

📚 **Полезные инструменты:**
• ETF на индекс МосБиржи
• ОФЗ с разными сроками
• Долларовые облигации

🤖 *Для персонализированного плана подключите AI-сервис*
            """
    
    def _get_portfolio_advice(self, stocks_pct: float, bonds_pct: float, positions_count: int) -> str:
        """Get portfolio advice based on allocation"""
        advice = []
        
        if stocks_pct > 70:
            advice.append("• Снизьте долю акций до 60% для баланса")
        elif stocks_pct < 40:
            advice.append("• Увеличьте долю акций для роста портфеля")
        else:
            advice.append("• Баланс акций/облигаций хороший")
        
        if bonds_pct > 60:
            advice.append("• Диверсифицируйте облигационный портфель")
        
        if positions_count < 5:
            advice.append("• Увеличьте диверсификацию (минимум 8-10 позиций)")
        elif positions_count > 20:
            advice.append("• Возможно избыточное усложнение портфеля")
        else:
            advice.append("• Уровень диверсификации адекватный")
        
        advice.append("• Рассмотрите добавление международных активов")
        advice.append("• Регулярно ребалансируйте портфель")
        
        return "\n".join(advice)


# Global instance for fallback
_fallback_ai = FallbackAI()

async def get_fallback_ai():
    """Get fallback AI instance"""
    return _fallback_ai