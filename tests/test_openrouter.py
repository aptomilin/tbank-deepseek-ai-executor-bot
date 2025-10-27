#!/usr/bin/env python3
"""
Test OpenRouter API with DeepSeek models
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_openrouter():
    """Test OpenRouter connection"""
    print("🤖 OPENROUTER API TEST")
    print("=" * 50)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    try:
        from app.ai_openrouter import OpenRouterAI
        
        async with OpenRouterAI() as ai:
            # Test basic response
            print("🔄 Testing basic response...")
            response = await ai.generate_response("Скажи 'ТЕСТ ПРОЙДЕН' одним словом")
            print(f"✅ Response: {response}")
            
            # Test available models
            print("🔄 Getting available models...")
            models = await ai.get_available_models()
            deepseek_models = [m for m in models if 'deepseek' in m.lower()]
            print(f"✅ DeepSeek models: {deepseek_models[:3]}")
            
            return True
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

async def test_ai_manager():
    """Test AI manager with OpenRouter"""
    print("\n🎯 TESTING AI MANAGER")
    print("=" * 50)
    
    try:
        from app.ai_manager import get_ai_manager
        
        manager = await get_ai_manager()
        info = manager.get_provider_info()
        
        print(f"Active provider: {info['active_provider']}")
        print(f"Available providers: {info['available_providers']}")
        
        # Test response
        response = await manager.generate_response("Привет! Скажи что AI работает")
        print(f"Manager response: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING OPENROUTER INTEGRATION")
    print("=" * 50)
    
    success1 = asyncio.run(test_openrouter())
    success2 = asyncio.run(test_ai_manager())
    
    if success1 and success2:
        print("\n🎉 OPENROUTER INTEGRATION SUCCESSFUL!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("=" * 50)