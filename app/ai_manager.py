"""
AI manager - EXTENDED for portfolio management
"""
import logging
from typing import Optional, List, Dict
import asyncio
import json
import re

logger = logging.getLogger(__name__)

class AIManager:
    """Extended AI manager with portfolio management capabilities"""
    
    def __init__(self):
        self.fallback_ai = None
        self.providers = {}
        self.active_provider = "fallback"
        self.initialized = False
        
        self._init_providers()

    async def _get_fallback(self):
        """Lazy initialization of fallback AI"""
        if self.fallback_ai is None:
            try:
                from app.ai_fallback import get_fallback_ai
                self.fallback_ai = await get_fallback_ai()
            except Exception as e:
                logger.error(f"Failed to initialize fallback AI: {e}")
                from app.ai_fallback import FallbackAI
                self.fallback_ai = FallbackAI()
        return self.fallback_ai

    def _init_providers(self):
        """Initialize AI providers"""
        if self.initialized:
            return
            
        # Try OpenRouter first
        try:
            from app.ai_openrouter import OpenRouterAI
            openrouter_ai = OpenRouterAI()
            if openrouter_ai.api_key and openrouter_ai.api_key.startswith('sk-or-'):
                self.providers["openrouter"] = openrouter_ai
                self.active_provider = "openrouter"
                logger.info("✅ OpenRouter AI initialized successfully")
            else:
                logger.warning("❌ OpenRouter API key not set or invalid")
        except Exception as e:
            logger.warning(f"❌ OpenRouter not available: {e}")

        # Try DeepSeek direct
        try:
            from app.ai_deepseek import DeepSeekAI
            deepseek_ai = DeepSeekAI()
            if deepseek_ai.api_key and deepseek_ai.api_key.startswith('sk-'):
                self.providers["deepseek"] = deepseek_ai
                if self.active_provider == "fallback":
                    self.active_provider = "deepseek"
                logger.info("✅ DeepSeek AI initialized successfully")
            else:
                logger.warning("❌ DeepSeek API key not set or invalid")
        except Exception as e:
            logger.warning(f"❌ DeepSeek not available: {e}")

        self.initialized = True
        logger.info(f"🎯 Active AI provider: {self.active_provider}")

    async def generate_portfolio_strategy(self, portfolio_data: dict, market_context: str = "") -> Dict:
        """Generate AI portfolio management strategy for maximum returns"""
        try:
            strategy_prompt = self._create_strategy_prompt(portfolio_data, market_context)
            
            # Try active provider first
            if self.active_provider in self.providers and self.active_provider != "fallback":
                try:
                    provider = self.providers[self.active_provider]
                    response = await provider.generate_response(strategy_prompt, "portfolio_strategy")
                    strategy = self._parse_strategy_response(response, portfolio_data)
                    if strategy:
                        return strategy
                except Exception as e:
                    logger.error(f"{self.active_provider} strategy error: {e}")

            # Try other providers
            for provider_name, provider in self.providers.items():
                if provider_name != self.active_provider:
                    try:
                        response = await provider.generate_response(strategy_prompt, "portfolio_strategy")
                        strategy = self._parse_strategy_response(response, portfolio_data)
                        if strategy:
                            self.active_provider = provider_name
                            return strategy
                    except Exception as e:
                        logger.error(f"{provider_name} strategy error: {e}")

            # Fallback to basic strategy
            return await self._generate_fallback_strategy(portfolio_data)
            
        except Exception as e:
            logger.error(f"Portfolio strategy generation error: {e}")
            return await self._generate_fallback_strategy(portfolio_data)

    def _create_strategy_prompt(self, portfolio_data: dict, market_context: str) -> str:
        """Create AI prompt for portfolio optimization"""
        total_value = portfolio_data.get('total_portfolio_value', 0)
        available_cash = portfolio_data.get('total_cash', 0)
        
        prompt = f"""
ТЫ - ПРОФЕССИОНАЛЬНЫЙ АЛГОРИТМИЧЕСКИЙ ТРЕЙДЕР. 
ЦЕЛЬ: МАКСИМИЗАЦИЯ ДОХОДНОСТИ ПОРТФЕЛЯ.

ДАННЫЕ ПОРТФЕЛЯ:
- Общая стоимость: {total_value:,.0f} руб.
- Доступные средства: {available_cash:,.0f} руб.
- Текущая доходность: {portfolio_data.get('total_yield_percentage', 0):.1f}%

ТЕКУЩИЕ ПОЗИЦИИ:
"""
        
        for account in portfolio_data.get('accounts', []):
            for position in account.get('positions', []):
                prompt += f"- {position['name']} ({position['ticker']}): {position['quantity']} шт. × {position['current_price']:.2f} руб. = {position['value']:,.0f} руб. (доходность: {position.get('yield_percentage', 0):.1f}%)\n"

        prompt += f"""
РЫНОЧНЫЙ КОНТЕКСТ:
{market_context if market_context else "Российский рынок акций и облигаций"}

СГЕНЕРИРУЙ ОПТИМАЛЬНУЮ ТОРГОВУЮ СТРАТЕГИЮ ДЛЯ МАКСИМАЛЬНОЙ ДОХОДНОСТИ.

ФОРМАТ ОТВЕТА (JSON):
{{
    "strategy_name": "название стратегии",
    "target_return": 15.5,
    "risk_level": "medium",
    "time_horizon": "1-3 months",
    "actions": [
        {{
            "action": "BUY/SELL/HOLD",
            "ticker": "SBER",
            "quantity": 10,
            "reason": "обоснование действия",
            "expected_impact": "увеличение доходности на 2.5%",
            "urgency": "high/medium/low"
        }}
    ],
    "portfolio_optimization": {{
        "target_allocation": {{
            "stocks": 65.0,
            "bonds": 25.0, 
            "cash": 10.0
        }},
        "sector_diversification": {{
            "technology": 20.0,
            "finance": 25.0,
            "energy": 15.0,
            "other": 40.0
        }}
    }},
    "risk_management": {{
        "stop_loss_level": 8.0,
        "take_profit_level": 25.0,
        "max_position_size": 15.0
    }}
}}

Будь конкретен и ориентирован на максимальную доходность!
        """
        
        return prompt

    def _parse_strategy_response(self, response: str, portfolio_data: dict) -> Dict:
        """Parse AI strategy response"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                strategy_json = json_match.group(0)
                return json.loads(strategy_json)
            else:
                # Fallback to structured response parsing
                return self._parse_structured_response(response, portfolio_data)
                
        except Exception as e:
            logger.error(f"Strategy parsing error: {e}")
            return None

    def _parse_structured_response(self, response: str, portfolio_data: dict) -> Dict:
        """Parse structured text response"""
        actions = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip().upper()
            if 'BUY' in line or 'SELL' in line:
                parts = line.split()
                if len(parts) >= 3:
                    action = "BUY" if "BUY" in parts[0] else "SELL"
                    ticker = parts[1] if len(parts[1]) <= 6 else "UNKNOWN"
                    # Extract quantity if possible
                    quantity = 1
                    for part in parts[2:]:
                        if part.isdigit():
                            quantity = int(part)
                            break
                    
                    actions.append({
                        "action": action,
                        "ticker": ticker,
                        "quantity": quantity,
                        "reason": "AI optimization",
                        "expected_impact": "Increased returns",
                        "urgency": "medium"
                    })
        
        return {
            "strategy_name": "AI Optimized Strategy",
            "target_return": 12.0,
            "risk_level": "medium",
            "time_horizon": "1-3 months",
            "actions": actions,
            "portfolio_optimization": {
                "target_allocation": {"stocks": 70.0, "bonds": 20.0, "cash": 10.0},
                "sector_diversification": {"technology": 25.0, "finance": 25.0, "energy": 20.0, "other": 30.0}
            },
            "risk_management": {
                "stop_loss_level": 10.0,
                "take_profit_level": 30.0,
                "max_position_size": 15.0
            }
        }

    async def _generate_fallback_strategy(self, portfolio_data: dict) -> Dict:
        """Generate fallback portfolio strategy"""
        logger.info("Using fallback portfolio strategy")
        
        return {
            "strategy_name": "Balanced Growth Strategy",
            "target_return": 10.5,
            "risk_level": "medium",
            "time_horizon": "3-6 months",
            "actions": [
                {
                    "action": "BUY",
                    "ticker": "SBER",
                    "quantity": 5,
                    "reason": "Укрепление позиции в финансовом секторе",
                    "expected_impact": "Потенциальный рост 8-12%",
                    "urgency": "medium"
                },
                {
                    "action": "BUY", 
                    "ticker": "YNDX",
                    "quantity": 2,
                    "reason": "Диверсификация в IT сектор",
                    "expected_impact": "Высокий потенциал роста",
                    "urgency": "medium"
                }
            ],
            "portfolio_optimization": {
                "target_allocation": {"stocks": 65.0, "bonds": 25.0, "cash": 10.0},
                "sector_diversification": {"technology": 20.0, "finance": 30.0, "energy": 25.0, "other": 25.0}
            },
            "risk_management": {
                "stop_loss_level": 8.0,
                "take_profit_level": 25.0,
                "max_position_size": 15.0
            }
        }

    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate AI response"""
        if not self.api_key:
            logger.error("No AI API key available")
            return "❌ Сервис AI временно недоступен. Проверьте настройки API."
        
        if not self.session:
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(connector=connector)
        
        full_prompt = f"""
        {context}
        
        Пользователь спрашивает: {prompt}
        
        Ответь кратко и по делу на русском языке.
        """
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system", 
                    "content": "Ты - профессиональный инвестиционный советник. Отвечай точно и полезно."
                },
                {
                    "role": "user",
                    "content": full_prompt.strip()
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7,
            "stream": False
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            logger.info(f"Sending request to DeepSeek API: {prompt[:50]}...")
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                json=data,
                headers=headers,
                timeout=30
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    
                    if 'choices' in result and len(result['choices']) > 0:
                        message = result['choices'][0]['message']['content']
                        logger.info(f"DeepSeek response received: {message[:100]}...")
                        return message.strip()
                    else:
                        logger.error(f"Unexpected response format: {result}")
                        return "❌ Ошибка формата ответа от AI сервиса."
                
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    
                    if response.status == 401:
                        return "❌ Неверный API ключ DeepSeek."
                    elif response.status == 402:
                        return "❌ Недостаточно средств на счету DeepSeek."
                    elif response.status == 429:
                        return "❌ Превышен лимит запросов к AI сервису."
                    else:
                        return f"❌ Ошибка AI сервиса: {response.status}"
                        
        except asyncio.TimeoutError:
            logger.error("DeepSeek API timeout")
            return "❌ Таймаут запроса к AI сервису."
        except aiohttp.ClientError as e:
            logger.error(f"DeepSeek connection error: {e}")
            return "❌ Ошибка подключения к AI сервису."
        except Exception as e:
            logger.error(f"Unexpected DeepSeek error: {e}")
            return "❌ Непредвиденная ошибка AI сервиса."

    async def analyze_portfolio(self, portfolio_data: dict) -> str:
        """Analyze portfolio data using AI"""
        prompt = f"""
        Проанализируй инвестиционный портфель и дай конкретные рекомендации:
        
        ДАННЫЕ ПОРТФЕЛЯ:
        - Общая стоимость: {portfolio_data.get('total_value', 0):,} руб.
        - Акции: {portfolio_data.get('stocks_value', 0):,} руб.
        - Облигации: {portfolio_data.get('bonds_value', 0):,} руб.
        - ETF: {portfolio_data.get('etf_value', 0):,} руб.
        - Количество позиций: {portfolio_data.get('positions_count', 0)}
        
        ПРОАНИЛИЗИРУЙ:
        1. Диверсификацию портфеля
        2. Соотношение риск/доходность  
        3. Конкретные рекомендации по оптимизации
        4. Потенциальные риски
        
        Будь конкретен, полезен и говори на русском.
        """
        
        return await self.generate_response(prompt)

    def _is_error_response(self, response: str) -> bool:
        """Check if response indicates an error"""
        if not response or not isinstance(response, str):
            return True
            
        error_indicators = [
            'недоступен', 'ошибка', 'error', '❌', 'ключ', 
            'средств', 'лимит', 'invalid', 'authentication',
            'ssl', 'certificate', 'таймаут', 'timeout', 'connection'
        ]
        
        response_lower = response.lower()
        return any(indicator in response_lower for indicator in error_indicators)

    def get_provider_info(self) -> dict:
        """Get information about available providers"""
        return {
            "active_provider": self.active_provider,
            "available_providers": list(self.providers.keys()),
            "fallback_available": True,
            "providers_count": len(self.providers),
            "initialized": self.initialized
        }

    async def close(self):
        """Close all provider sessions"""
        for provider_name, provider in self.providers.items():
            if hasattr(provider, 'close'):
                try:
                    await provider.close()
                    logger.info(f"Closed {provider_name} session")
                except Exception as e:
                    logger.error(f"Error closing {provider_name}: {e}")

# Global instance
_ai_manager: Optional[AIManager] = None

async def get_ai_manager():
    """Get AI manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager