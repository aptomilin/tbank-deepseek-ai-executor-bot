#!/usr/bin/env python3
"""
Test all available AI providers
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_provider(provider_name, test_function):
    """Test a single provider"""
    print(f"\n🔍 TESTING {provider_name.upper()}")
    print("-" * 30)
    
    try:
        result = await test_function()
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {provider_name}")
        return result
    except Exception as e:
        print(f"❌ FAIL {provider_name}: {e}")
        return False

async def test_openrouter():
    """Test OpenRouter"""
    try:
        from app.ai_openrouter import OpenRouterAI
        
        async with OpenRouterAI() as ai:
            if not ai.api_key:
                print("  ⚠️ No API key")
                return False
                
            response = await ai.generate_response("Ответь 'OK'")
            return "ok" in response.lower() or "ок" in response.lower()
            
    except Exception as e:
        print(f"  Error: {e}")
        return False

async def test_deepseek():
    """Test direct DeepSeek"""
    try:
        from app.ai_deepseek import DeepSeekAI
        
        async with DeepSeekAI() as ai:
            if not ai.api_key:
                print("  ⚠️ No API key")
                return False
                
            response = await ai.generate_response("Ответь 'OK'")
            return "ok" in response.lower() or "ок" in response.lower()
            
    except Exception as e:
        print(f"  Error: {e}")
        return False

async def test_fallback():
    """Test fallback AI"""
    try:
        from app.ai_fallback import FallbackAI
        
        ai = FallbackAI()
        response = await ai.generate_response("Тест")
        return len(response) > 0
        
    except Exception as e:
        print(f"  Error: {e}")
        return False

async def test_ai_manager_integration():
    """Test AI manager integration"""
    print("\n🔧 TESTING AI MANAGER INTEGRATION")
    print("-" * 40)
    
    try:
        from app.ai_manager import get_ai_manager
        
        manager = await get_ai_manager()
        info = manager.get_provider_info()
        
        print(f"Active provider: {info['active_provider']}")
        print(f"Available: {info['available_providers']}")
        
        # Test portfolio analysis
        portfolio_data = {
            'total_value': 150000,
            'stocks_value': 100000,
            'bonds_value': 50000,
            'positions_count': 3
        }
        
        response = await manager.analyze_portfolio(portfolio_data)
        print(f"Portfolio analysis: {response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Manager integration failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🤖 COMPREHENSIVE AI PROVIDERS TEST")
    print("=" * 50)
    
    # Test individual providers
    providers = [
        ("OpenRouter", test_openrouter),
        ("DeepSeek", test_deepseek),
        ("Fallback", test_fallback),
    ]
    
    results = []
    for name, test_func in providers:
        result = await test_provider(name, test_func)
        results.append(result)
    
    # Test integration
    integration_ok = await test_ai_manager_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for i, (name, _) in enumerate(providers):
        status = "✅ WORKING" if results[i] else "❌ NOT WORKING"
        print(f"{name}: {status}")
    
    print(f"AI Manager: {'✅ WORKING' if integration_ok else '❌ NOT WORKING'}")
    
    # Overall status
    working_providers = sum(results)
    if working_providers >= 1:
        print(f"\n🎉 SUCCESS: {working_providers} AI provider(s) working!")
    else:
        print("\n⚠️ WARNING: No AI providers working, only fallback available")
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())