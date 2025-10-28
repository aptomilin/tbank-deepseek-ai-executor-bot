import logging
from decimal import Decimal
from typing import Dict, List, Optional
import aiohttp
import json

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Анализатор инвестиционного портфеля для российских инструментов"""

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

    def _format_portfolio_analysis(self, data: Dict) -> str:
        """Форматирование анализа портфеля"""
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
        """Форматирование контекста портфеля для AI"""
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

        context += "\nЦЕЛЬ: Максимальная доходность через российские инструменты."
        return context

    async def _generate_management_recommendations(self, data: Dict) -> str:
        """Генерация рекомендаций по автоматическому управлению"""
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
        """Анализ распределения активов"""
        allocation = {}
        total_value = sum(pos['value'] for pos in positions)
        
        for position in positions:
            asset_type = "Акции" if position['type'] == 'stock' else "Облигации"
            if asset_type not in allocation:
                allocation[asset_type] = 0
            allocation[asset_type] += float((position['value'] / total_value * 100))
                
        return allocation

    def _analyze_sectors(self, positions: List[Dict]) -> Dict[str, float]:
        """Анализ распределения по секторам"""
        sectors = {}
        total_value = sum(pos['value'] for pos in positions)
        
        for position in positions:
            sector = position['sector']
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += float((position['value'] / total_value * 100))
                
        return sectors

    def _analyze_portfolio_for_management(self, data: Dict) -> Dict:
        """Анализ портфеля для управления"""
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

    def _get_fallback_analysis(self) -> str:
        """Запасной анализ"""
        return """📊 **Анализ портфеля (демо-данные)**

💼 **Общая стоимость:** 185,000.00 ₽
📈 **Доходность:** +15,600.00 ₽ (+9.2%)
💳 **Доступные средства:** 32,000.00 ₽

**Распределение:**
• Акции: 78.4%
• Облигации: 21.6%

🤖 *Для реальных данных настройте Tinkoff API*
🇷🇺 *Стратегия: российские инструменты для максимальной доходности*"""

    def _get_fallback_context(self) -> str:
        """Запасной контекст"""
        return """Текущий портфель пользователя (демо-данные):
- Общая стоимость: 185,000 ₽
- Доходность: +15,600 ₽ (+9.2%)
- Доступные средства: 32,000 ₽

Позиции:
• Сбербанк (SBER): 52,000 ₽ (8.1%)
• Газпром (GAZP): 41,000 ₽ (5.7%)
• Лукойл (LKOH): 38,000 ₽ (13.8%)
• Яндекс (YNDX): 22,000 ₽ (16.8%)
• ОФЗ-26238 (SU26238): 40,000 ₽ (5.3%)

Распределение:
- Акции: 78.4%
- Облигации: 21.6%

Ограничение: использовать только российские инструменты."""

    def _get_fallback_management_recommendations(self) -> str:
        """Запасные рекомендации"""
        return """🤖 **РЕКОМЕНДАЦИИ ПО АВТОУПРАВЛЕНИЮ**

1. 📈 **Увеличить долю акций до 80%** (+1.6%)
   - Яндекс (YNDX): 10,000 ₽ - потенциал роста
   - TCS Group (TCSG): 8,000 ₽ - рост IT-сектора

2. 🛡️ **Добавить облигации до 20%** (-1.6%)
   - ОФЗ-26230: 6,000 ₽ - доходность 8.5%

💡 **Доступно для инвестиций:** 32,000 ₽

🇷🇺 *Стратегия: максимальная доходность через российские инструменты*"""