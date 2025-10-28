import logging
from decimal import Decimal
from typing import Dict, List, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Анализатор инвестиционного портфеля для автоматического управления российскими инструментами"""

    def __init__(self, config):
        self.config = config
        self.russian_instruments = self._load_russian_instruments()

    def _load_russian_instruments(self) -> Dict:
        """Загрузка списка российских инструментов для автоматического управления"""
        return {
            "stocks": {
                "SBER": {"name": "Сбербанк", "sector": "Финансы", "risk": "средний"},
                "VTBR": {"name": "ВТБ", "sector": "Финансы", "risk": "средний"},
                "GAZP": {"name": "Газпром", "sector": "Энергетика", "risk": "низкий"},
                "LKOH": {"name": "Лукойл", "sector": "Энергетика", "risk": "низкий"},
                "ROSN": {"name": "Роснефть", "sector": "Энергетика", "risk": "средний"},
                "NVTK": {"name": "Новатэк", "sector": "Энергетика", "risk": "средний"},
                "GMKN": {"name": "ГМК Норникель", "sector": "Металлургия", "risk": "высокий"},
                "PLZL": {"name": "Полюс", "sector": "Металлургия", "risk": "высокий"},
                "YNDX": {"name": "Яндекс", "sector": "IT", "risk": "высокий"},
                "TCSG": {"name": "TCS Group", "sector": "Финансы", "risk": "высокий"},
                "MOEX": {"name": "Московская биржа", "sector": "Финансы", "risk": "средний"},
                "MGNT": {"name": "Магнит", "sector": "Ритейл", "risk": "средний"},
                "AFKS": {"name": "АФК Система", "sector": "Холдинг", "risk": "высокий"},
                "PHOR": {"name": "ФосАгро", "sector": "Химия", "risk": "средний"},
                "POLY": {"name": "Полиметалл", "sector": "Металлургия", "risk": "высокий"},
            },
            "bonds": {
                "SU26230": {"name": "ОФЗ-26230", "yield": 8.5, "risk": "низкий"},
                "SU26238": {"name": "ОФЗ-26238", "yield": 8.2, "risk": "низкий"},
                "SU26242": {"name": "ОФЗ-26242", "yield": 8.0, "risk": "низкий"},
            }
        }

    async def get_portfolio_analysis(self) -> str:
        """Получить анализ портфеля с акцентом на российские инструменты"""
        try:
            portfolio_data = await self._get_portfolio_data()
            return self._format_portfolio_analysis(portfolio_data)
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return self._get_fallback_analysis()

    async def get_portfolio_context(self) -> str:
        """Получить контекст портфеля для AI"""
        try:
            portfolio_data = await self._get_portfolio_data()
            return self._format_portfolio_context(portfolio_data)
        except Exception as e:
            logger.error(f"Error getting portfolio context: {e}")
            return self._get_fallback_context()

    async def get_auto_management_recommendations(self) -> str:
        """Получить рекомендации по автоматическому управлению портфелем"""
        try:
            portfolio_data = await self._get_portfolio_data()
            return await self._generate_management_recommendations(portfolio_data)
        except Exception as e:
            logger.error(f"Error generating management recommendations: {e}")
            return self._get_fallback_management_recommendations()

    async def _get_portfolio_data(self) -> Dict:
        """Получить данные портфеля"""
        # Здесь должна быть интеграция с Tinkoff API
        # Пока используем демо-данные с российскими инструментами
        return {
            "total_value": Decimal("150000.00"),
            "total_yield": Decimal("12500.00"),
            "yield_percentage": Decimal("9.1"),
            "available_cash": Decimal("25000.00"),
            "positions": [
                {"name": "Сбербанк", "ticker": "SBER", "value": Decimal("45000.00"), 
                 "yield": Decimal("3200.00"), "percentage": Decimal("7.7"), "type": "stock", "country": "RU"},
                {"name": "ВТБ", "ticker": "VTBR", "value": Decimal("35000.00"), 
                 "yield": Decimal("1800.00"), "percentage": Decimal("5.4"), "type": "stock", "country": "RU"},
                {"name": "Газпром", "ticker": "GAZP", "value": Decimal("28000.00"), 
                 "yield": Decimal("1500.00"), "percentage": Decimal("5.7"), "type": "stock", "country": "RU"},
                {"name": "ОФЗ-26242", "ticker": "SU26242", "value": Decimal("40000.00"), 
                 "yield": Decimal("2200.00"), "percentage": Decimal("5.8"), "type": "bond", "country": "RU"},
            ]
        }

    def _format_portfolio_analysis(self, data: Dict) -> str:
        """Форматирование анализа портфеля"""
        text = "📊 **Анализ портфеля (Российские инструменты)**\n\n"
        text += f"💼 **Общая стоимость:** {data['total_value']:,.2f} ₽\n"
        text += f"📈 **Доходность:** {data['total_yield']:+,.2f} ₽ ({data['yield_percentage']:+.1f}%)\n"
        text += f"💳 **Доступные средства:** {data['available_cash']:,.2f} ₽\n\n"

        # Анализ распределения
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
        """Форматирование контекста портфеля для AI"""
        context = "Текущий портфель пользователя (российские инструменты):\n"
        context += f"- Общая стоимость: {data['total_value']:,.0f} ₽\n"
        context += f"- Доходность: {data['total_yield']:+,.0f} ₽ ({data['yield_percentage']:+.1f}%)\n"
        context += f"- Доступные средства: {data['available_cash']:,.0f} ₽\n\n"

        context += "Позиции:\n"
        for position in data['positions']:
            context += f"• {position['name']} ({position['ticker']}): {position['value']:,.0f} ₽ "
            context += f"({position['percentage']:+.1f}%)\n"

        # Анализ распределения
        allocation = self._analyze_allocation(data['positions'])
        context += f"\nРаспределение:\n"
        for asset_type, percentage in allocation.items():
            context += f"- {asset_type}: {percentage:.1f}%\n"

        context += "\nВажно: использовать только российские инструменты для максимальной доходности."
        return context

    async def _generate_management_recommendations(self, data: Dict) -> str:
        """Генерация рекомендаций по автоматическому управлению"""
        recommendations = []
        available_cash = data['available_cash']
        
        # Анализ текущего портфеля
        allocation = self._analyze_allocation(data['positions'])
        current_stocks = allocation.get('Акции', 0)
        current_bonds = allocation.get('Облигации', 0)

        # Стратегия автоуправления
        if current_stocks < 70 and available_cash > 10000:
            recommendations.append(f"📈 **Увеличить долю акций до 70%** (+{(70 - current_stocks):.1f}%)")
            recommendations.extend(self._get_stock_recommendations(available_cash * 0.7))
        
        if current_bonds < 30 and available_cash > 5000:
            recommendations.append(f"🛡️ **Добавить облигации до 30%** (+{(30 - current_bonds):.1f}%)")
            recommendations.extend(self._get_bond_recommendations(available_cash * 0.3))

        # Рекомендации по оптимизации
        if data['yield_percentage'] < 8:
            recommendations.append("⚡ **Повысить доходность** - добавить акции роста (YNDX, TCSG)")

        if len(data['positions']) < 8:
            recommendations.append("🔄 **Диверсифицировать портфель** - добавить 2-3 новые позиции")

        text = "🤖 **Рекомендации по автоуправлению**\n\n"
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                text += f"{i}. {rec}\n"
        else:
            text += "✅ Портфель оптимально сбалансирован. Рекомендуется сохранить текущую структуру.\n"

        text += f"\n💡 **Доступно для инвестиций:** {available_cash:,.0f} ₽"
        text += "\n\n🇷🇺 *Стратегия: максимальная доходность через российские инструменты*"
        
        return text

    def _analyze_allocation(self, positions: List[Dict]) -> Dict[str, float]:
        """Анализ распределения активов"""
        allocation = {}
        total_value = sum(pos['value'] for pos in positions)
        
        if total_value == 0:
            return {}
            
        for position in positions:
            asset_type = "Акции" if position['type'] == 'stock' else "Облигации"
            if asset_type not in allocation:
                allocation[asset_type] = 0
            allocation[asset_type] += float((position['value'] / total_value * 100))
            
        return allocation

    def _get_stock_recommendations(self, amount: Decimal) -> List[str]:
        """Рекомендации по акциям"""
        recommendations = []
        stocks = self.russian_instruments["stocks"]
        
        # Выбираем акции с потенциалом роста
        growth_stocks = ["YNDX", "TCSG", "POLY", "GMKN"]
        for ticker in growth_stocks[:2]:  # Рекомендуем 2 акции роста
            if ticker in stocks:
                stock = stocks[ticker]
                rec_amount = amount * Decimal('0.4')  # 40% на каждую акцию роста
                recommendations.append(f"   - {stock['name']} ({ticker}): {rec_amount:,.0f} ₽ - потенциал роста")

        # Добавляем дивидендные акции
        dividend_stocks = ["SBER", "GAZP", "LKOH"]
        for ticker in dividend_stocks[:1]:  # Рекомендуем 1 дивидендную акцию
            if ticker in stocks:
                stock = stocks[ticker]
                rec_amount = amount * Decimal('0.2')  # 20% на дивидендную акцию
                recommendations.append(f"   - {stock['name']} ({ticker}): {rec_amount:,.0f} ₽ - дивидендный доход")
                
        return recommendations

    def _get_bond_recommendations(self, amount: Decimal) -> List[str]:
        """Рекомендации по облигациям"""
        recommendations = []
        bonds = self.russian_instruments["bonds"]
        
        # Рекомендуем ОФЗ с лучшей доходностью
        best_bond = max(bonds.items(), key=lambda x: x[1]["yield"])
        bond_name = best_bond[1]["name"]
        bond_yield = best_bond[1]["yield"]
        
        recommendations.append(f"   - {bond_name}: {amount:,.0f} ₽ - доходность {bond_yield}%")
        
        return recommendations

    def _get_fallback_analysis(self) -> str:
        """Запасной анализ"""
        return """📊 **Анализ портфеля (демо-данные)**

💼 **Общая стоимость:** 150,000.00 ₽
📈 **Доходность:** +12,500.00 ₽ (+9.1%)
💳 **Доступные средства:** 25,000.00 ₽

**Распределение:**
• Акции: 72.0%
• Облигации: 28.0%

🤖 *Для реальных данных настройте Tinkoff API*
🇷🇺 *Стратегия: российские инструменты для максимальной доходности*"""

    def _get_fallback_context(self) -> str:
        """Запасной контекст"""
        return """Текущий портфель пользователя (демо-данные):
- Общая стоимость: 150,000 ₽
- Доходность: +12,500 ₽ (+9.1%)
- Доступные средства: 25,000 ₽

Позиции:
• Сбербанк (SBER): 45,000 ₽ (7.7%)
• ВТБ (VTBR): 35,000 ₽ (5.4%)
• Газпром (GAZP): 28,000 ₽ (5.7%)
• ОФЗ-26242 (SU26242): 40,000 ₽ (5.8%)

Распределение:
- Акции: 72.0%
- Облигации: 28.0%

Ограничение: использовать только российские инструменты."""

    def _get_fallback_management_recommendations(self) -> str:
        """Запасные рекомендации"""
        return """🤖 **Рекомендации по автоуправлению**

1. 📈 **Увеличить долю акций до 70%** (+0.0%)
   - Яндекс (YNDX): 7,000 ₽ - потенциал роста
   - TCS Group (TCSG): 7,000 ₽ - рост IT-сектора

2. 🛡️ **Добавить облигации до 30%** (+2.0%)
   - ОФЗ-26230: 6,000 ₽ - доходность 8.5%

💡 **Доступно для инвестиций:** 25,000 ₽

🇷🇺 *Стратегия: максимальная доходность через российские инструменты*"""