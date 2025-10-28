import logging
import aiohttp
import json
from decimal import Decimal
from typing import Dict, List, Optional
from datetime import datetime
import re
import random

logger = logging.getLogger(__name__)


class AutoPortfolioManager:
    """Автоматическое управление портфелем через DeepSeek AI"""
    
    def __init__(self, config):
        self.config = config
        self.api_key = config.DEEPSEEK_API_KEY
        self.api_url = config.DEEPSEEK_API_URL
        self.russian_instruments = self._load_russian_instruments()
        
    def _load_russian_instruments(self) -> Dict:
        """Загрузка списка российских инструментов"""
        return {
            "stocks": {
                "SBER": {"name": "Сбербанк", "sector": "Финансы", "risk": "средний"},
                "VTBR": {"name": "ВТБ", "sector": "Финансы", "risk": "средний"},
                "GAZP": {"name": "Газпром", "sector": "Энергетика", "risk": "низкий"},
                "LKOH": {"name": "Лукойл", "sector": "Энергетика", "risk": "низкий"},
                "ROSN": {"name": "Роснефть", "sector": "Энергетика", "risk": "средний"},
                "YNDX": {"name": "Яндекс", "sector": "IT", "risk": "высокий"},
                "TCSG": {"name": "TCS Group", "sector": "Финансы", "risk": "высокий"},
                "GMKN": {"name": "ГМК Норникель", "sector": "Металлургия", "risk": "высокий"},
                "POLY": {"name": "Полиметалл", "sector": "Металлургия", "risk": "высокий"},
                "MOEX": {"name": "Московская биржа", "sector": "Финансы", "risk": "средний"},
            },
            "bonds": {
                "SU26230": {"name": "ОФЗ-26230", "yield": 8.5, "risk": "низкий"},
                "SU26238": {"name": "ОФЗ-26238", "yield": 8.2, "risk": "низкий"},
                "SU26242": {"name": "ОФЗ-26242", "yield": 8.0, "risk": "низкий"},
            }
        }
        
    async def generate_trading_decisions(self, portfolio_data: Dict, market_context: str = "") -> List[Dict]:
        """Генерация торговых решений через AI"""
        try:
            # Пробуем получить решения от AI
            ai_decisions = await self._get_ai_trading_decisions(portfolio_data, market_context)
            if ai_decisions:
                logger.info(f"AI generated {len(ai_decisions)} trading decisions")
                return ai_decisions
            else:
                # Fallback: генерируем решения на основе алгоритмической логики
                logger.info("Using algorithmic fallback for trading decisions")
                return await self._generate_algorithmic_decisions(portfolio_data)
            
        except Exception as e:
            logger.error(f"Error generating trading decisions: {e}")
            return await self._generate_algorithmic_decisions(portfolio_data)
    
    async def _get_ai_trading_decisions(self, portfolio_data: Dict, market_context: str) -> List[Dict]:
        """Получение торговых решений от AI"""
        try:
            analysis_prompt = self._create_analysis_prompt(portfolio_data, market_context)
            ai_response = await self._get_ai_trading_advice(analysis_prompt)
            
            if ai_response:
                decisions = self._parse_trading_decisions(ai_response, portfolio_data)
                if decisions:
                    return decisions
            
            return []
            
        except Exception as e:
            logger.error(f"Error in AI trading decisions: {e}")
            return []
    
    async def _generate_algorithmic_decisions(self, portfolio_data: Dict) -> List[Dict]:
        """Алгоритмическая генерация торговых решений (fallback)"""
        decisions = []
        available_cash = portfolio_data['available_cash']
        positions = portfolio_data['positions']
        
        # Анализируем текущий портфель
        allocation = self._calculate_allocation(positions)
        sectors = self._analyze_sectors(positions)
        
        # Правило 1: Если есть доступные средства, инвестируем в недооцененные сектора
        if available_cash > Decimal('10000'):
            if sectors.get('IT', 0) < 15:
                # Добавляем IT-сектор
                amount = min(available_cash * Decimal('0.3'), Decimal('15000'))
                decisions.append({
                    'action': 'BUY',
                    'ticker': 'YNDX',
                    'amount': amount,
                    'rationale': 'Увеличение доли IT-сектора для роста доходности',
                    'expected_yield': 18.5,
                    'source': 'algorithm'
                })
            
            if sectors.get('Металлургия', 0) < 10:
                # Добавляем металлургию
                amount = min(available_cash * Decimal('0.2'), Decimal('10000'))
                decisions.append({
                    'action': 'BUY',
                    'ticker': 'GMKN',
                    'amount': amount,
                    'rationale': 'Диверсификация в экспортно-ориентированные активы',
                    'expected_yield': 16.0,
                    'source': 'algorithm'
                })
        
        # Правило 2: Ребалансировка переоцененных позиций
        for position in positions:
            if position['percentage'] < 5 and position['type'] == 'stock':
                # Увеличиваем слабые позиции
                if available_cash > Decimal('5000'):
                    amount = min(available_cash * Decimal('0.15'), Decimal('8000'))
                    decisions.append({
                        'action': 'BUY',
                        'ticker': position['ticker'],
                        'amount': amount,
                        'rationale': f'Усиление позиции {position["name"]}',
                        'expected_yield': position['percentage'] + 3.0,
                        'source': 'algorithm'
                    })
        
        # Правило 3: Добавление облигаций для баланса
        if allocation.get('Облигации', 0) < 20 and available_cash > Decimal('5000'):
            amount = min(available_cash * Decimal('0.25'), Decimal('12000'))
            decisions.append({
                'action': 'BUY',
                'ticker': 'SU26230',
                'amount': amount,
                'rationale': 'Балансировка портфеля защитными активами',
                'expected_yield': 8.5,
                'source': 'algorithm'
            })
        
        return decisions[:4]  # Ограничиваем 4 решениями
    
    def _create_analysis_prompt(self, portfolio_data: Dict, market_context: str) -> str:
        """Создает промпт для анализа и принятия решений"""
        
        prompt = f"""АНАЛИЗ ПОРТФЕЛЯ ДЛЯ АВТОМАТИЧЕСКОЙ ТОРГОВЛИ:

ДАННЫЕ ПОРТФЕЛЯ:
{self._format_portfolio_for_ai(portfolio_data)}

РЫНОЧНЫЙ КОНТЕКСТ:
{market_context if market_context else "Российский рынок акций и облигаций"}

ЗАДАЧА: Сгенерируй 3-5 конкретных торговых решений для максимизации доходности.

ФОРМАТ ОТВЕТА (обязательно):
BUY/SELL [ТИКЕР] [СУММА_В_РУБЛЯХ] [ОБОСНОВАНИЕ] [ОЖИДАЕМАЯ_ДОХОДНОСТЬ%]

ПРИМЕРЫ:
BUY YNDX 15000 РОСТ_IT_СЕКТОРА 18.5
SELL GAZP 8000 СТАГНАЦИЯ_ЭНЕРГЕТИКИ 5.2
BUY SU26230 12000 ЗАЩИТА_ПОРТФЕЛЯ 8.5

РЕШЕНИЯ:"""
        
        return prompt
    
    async def _get_ai_trading_advice(self, prompt: str) -> str:
        """Получает торговые рекомендации от DeepSeek AI"""
        if not self.api_key:
            logger.warning("DeepSeek API key not configured")
            return ""
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": """Ты - автоматический торговый алгоритм. Дай конкретные торговые решения в строгом формате: 
ACTION TICKER AMOUNT RATIONALE YIELD%
Где ACTION: BUY/SELL, AMOUNT: сумма в рублях, YIELD: ожидаемая доходность в %.
Только российские инструменты. Максимум 5 решений."""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.3,
            "stream": False
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.post(
                    f"{self.api_url}/chat/completions",
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data['choices'][0]['message']['content']
                        logger.info(f"AI Response: {content}")
                        return content
                    else:
                        error_text = await response.text()
                        logger.error(f"AI API error: {response.status} - {error_text}")
                        return ""
        except Exception as e:
            logger.error(f"AI request failed: {e}")
            return ""
    
    def _format_portfolio_for_ai(self, portfolio: Dict) -> str:
        """Форматирует данные портфеля для AI"""
        text = f"Общая стоимость: {portfolio['total_value']:,.0f} ₽\n"
        text += f"Доходность: {portfolio['total_yield']:+,.0f} ₽ ({portfolio['yield_percentage']:+.1f}%)\n"
        text += f"Доступные средства: {portfolio['available_cash']:,.0f} ₽\n\n"
        
        text += "Текущие позиции:\n"
        for position in portfolio['positions']:
            text += f"- {position['name']} ({position['ticker']}): {position['value']:,.0f} ₽ "
            text += f"(доходность: {position['percentage']:+.1f}%)\n"
        
        allocation = self._calculate_allocation(portfolio['positions'])
        text += f"\nРаспределение:\n"
        for asset_type, percentage in allocation.items():
            text += f"- {asset_type}: {percentage:.1f}%\n"
            
        return text
    
    def _parse_trading_decisions(self, ai_response: str, portfolio_data: Dict) -> List[Dict]:
        """Парсит торговые решения из AI ответа"""
        decisions = []
        lines = ai_response.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Пробуем разные форматы парсинга
            decision = self._parse_decision_line(line, portfolio_data)
            if decision:
                decisions.append(decision)
        
        logger.info(f"Parsed {len(decisions)} decisions from AI response")
        return decisions
    
    def _parse_decision_line(self, line: str, portfolio_data: Dict) -> Optional[Dict]:
        """Парсит одну строку с решением"""
        try:
            # Упрощенный парсинг для разных форматов
            parts = line.upper().split()
            if len(parts) < 4:
                return None
                
            # Ищем действие
            action = None
            if 'BUY' in parts[0]:
                action = 'BUY'
            elif 'SELL' in parts[0]:
                action = 'SELL'
            else:
                return None
            
            # Ищем тикер (второй элемент или следующий после действия)
            ticker = parts[1] if len(parts[1]) <= 6 else None
            if not ticker or ticker not in self._get_all_tickers():
                # Пробуем найти тикер в строке
                for part in parts[2:6]:
                    if part in self._get_all_tickers():
                        ticker = part
                        break
            
            if not ticker:
                return None
            
            # Ищем сумму
            amount = self._extract_amount(line, portfolio_data['available_cash'])
            
            # Ищем доходность
            expected_yield = self._extract_yield(line)
            
            # Обоснование - остальная часть строки
            rationale_parts = []
            for part in parts:
                if (part != action and part != ticker and 
                    not part.replace('₽', '').replace(',', '').replace('.', '').isdigit()):
                    rationale_parts.append(part)
            
            rationale = ' '.join(rationale_parts) if rationale_parts else 'AI рекомендация'
            
            return {
                'action': action,
                'ticker': ticker,
                'amount': amount,
                'rationale': rationale,
                'expected_yield': expected_yield,
                'source': 'ai',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error parsing decision line: {line} - {e}")
            return None
    
    def _get_all_tickers(self) -> set:
        """Возвращает все доступные тикеры"""
        tickers = set(self.russian_instruments["stocks"].keys())
        tickers.update(self.russian_instruments["bonds"].keys())
        return tickers
    
    def _extract_amount(self, text: str, available_cash: Decimal) -> Decimal:
        """Извлекает сумму из текста"""
        try:
            # Ищем числа с символами валюты
            matches = re.findall(r'(\d+[,\.]?\d*)\s*₽?', text)
            if matches:
                amount_str = matches[0].replace(',', '').replace('.', '')
                amount = Decimal(amount_str)
                # Проверяем что сумма разумная
                if amount < available_cash * Decimal('0.8'):
                    return amount
        except:
            pass
        
        # Fallback: 20% от доступных средств
        return available_cash * Decimal('0.2')
    
    def _extract_yield(self, text: str) -> float:
        """Извлекает ожидаемую доходность из текста"""
        try:
            matches = re.findall(r'(\d+[,\.]?\d*)%', text)
            if matches:
                return float(matches[0].replace(',', '.'))
        except:
            pass
        
        # Fallback: случайная доходность в разумных пределах
        return round(random.uniform(8.0, 25.0), 1)
    
    def _calculate_allocation(self, positions: List[Dict]) -> Dict[str, float]:
        """Рассчитывает распределение активов"""
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
    
    def _analyze_sectors(self, positions: List[Dict]) -> Dict[str, float]:
        """Анализ распределения по секторам"""
        sectors = {}
        total_value = sum(pos['value'] for pos in positions)
        
        if total_value == 0:
            return {}
            
        for position in positions:
            sector = position.get('sector', 'Другое')
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += float((position['value'] / total_value * 100))
                
        return sectors