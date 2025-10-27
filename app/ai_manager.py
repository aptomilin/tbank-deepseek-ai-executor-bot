"""
AI manager with multiple providers and automatic fallback
"""
import logging

logger = logging.getLogger(__name__)

class AIManager:
    """Manage AI with multiple providers and automatic fallback"""
    
    def __init__(self):
        self.fallback_ai = None
        self.providers = {}
        self.active_provider = "fallback"
        
        # Initialize providers
        self._init_providers()
    
    async def _get_fallback(self):
        """Lazy initialization of fallback AI"""
        if self.fallback_ai is None:
            from app.ai_fallback import get_fallback_ai
            self.fallback_ai = await get_fallback_ai()
        return self.fallback_ai
    
    def _init_providers(self):
        """Initialize all available AI providers"""
        
        # Try OpenRouter first
        try:
            from app.ai_openrouter import OpenRouterAI
            openrouter_ai = OpenRouterAI()
            if openrouter_ai.api_key and openrouter_ai.api_key.startswith('sk-or-'):
                self.providers["openrouter"] = openrouter_ai
                self.active_provider = "openrouter"
                logger.info("✅ OpenRouter AI initialized")
            else:
                logger.warning("❌ OpenRouter API key not set or invalid")
        except ImportError as e:
            logger.warning(f"❌ OpenRouter not available: {e}")
        except Exception as e:
            logger.warning(f"❌ OpenRouter init error: {e}")
        
        # Try DeepSeek direct
        try:
            from app.ai_deepseek import DeepSeekAI
            deepseek_ai = DeepSeekAI()
            if deepseek_ai.api_key and deepseek_ai.api_key.startswith('sk-'):
                self.providers["deepseek"] = deepseek_ai
                if self.active_provider == "fallback":
                    self.active_provider = "deepseek"
                logger.info("✅ DeepSeek AI initialized")
            else:
                logger.warning("❌ DeepSeek API key not set or invalid")
        except ImportError:
            logger.warning("❌ DeepSeek AI not available")
        except Exception as e:
            logger.warning(f"❌ DeepSeek init error: {e}")
        
        logger.info(f"🎯 Active AI provider: {self.active_provider}")
        logger.info(f"📋 Available providers: {list(self.providers.keys())}")
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response with provider fallback"""
        
        # Try active provider first (if not fallback)
        if self.active_provider in self.providers and self.active_provider != "fallback":
            try:
                provider = self.providers[self.active_provider]
                response = await provider.generate_response(prompt, context)
                
                # Check if response indicates error
                if not self._is_error_response(response):
                    return response
                else:
                    logger.warning(f"{self.active_provider} returned error, trying other providers")
            except Exception as e:
                logger.error(f"{self.active_provider} error: {e}")
        
        # Try other providers
        for provider_name, provider in self.providers.items():
            if provider_name != self.active_provider:
                try:
                    response = await provider.generate_response(prompt, context)
                    if not self._is_error_response(response):
                        # Switch to this provider for future requests
                        self.active_provider = provider_name
                        logger.info(f"🔀 Switched to provider: {provider_name}")
                        return response
                except Exception as e:
                    logger.error(f"{provider_name} error: {e}")
        
        # Use fallback as last resort
        logger.info("🔄 Using fallback AI")
        fallback = await self._get_fallback()
        return await fallback.generate_response(prompt, context)
    
    async def analyze_portfolio(self, portfolio_data: dict) -> str:
        """Analyze portfolio with provider fallback"""
        # Try active provider first
        if self.active_provider in self.providers and self.active_provider != "fallback":
            try:
                provider = self.providers[self.active_provider]
                if hasattr(provider, 'analyze_portfolio'):
                    response = await provider.analyze_portfolio(portfolio_data)
                    if not self._is_error_response(response):
                        return response
            except Exception as e:
                logger.error(f"{self.active_provider} portfolio error: {e}")
        
        # Try other providers for portfolio analysis
        for provider_name, provider in self.providers.items():
            if (provider_name != self.active_provider and 
                hasattr(provider, 'analyze_portfolio')):
                try:
                    response = await provider.analyze_portfolio(portfolio_data)
                    if not self._is_error_response(response):
                        self.active_provider = provider_name
                        return response
                except Exception as e:
                    logger.error(f"{provider_name} portfolio error: {e}")
        
        # Use fallback
        fallback = await self._get_fallback()
        return await fallback.analyze_portfolio(portfolio_data)
    
    def _is_error_response(self, response: str) -> bool:
        """Check if response indicates an error"""
        if not response:
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
            "providers_count": len(self.providers)
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
        
        if self.fallback_ai and hasattr(self.fallback_ai, 'close'):
            try:
                await self.fallback_ai.close()
            except Exception as e:
                logger.error(f"Error closing fallback: {e}")


# Global instance
_ai_manager: AIManager = None

async def get_ai_manager():
    """Get AI manager instance"""
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager