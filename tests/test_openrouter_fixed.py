#!/usr/bin/env python3
"""
Fixed OpenRouter test with correct imports
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

async def test_openrouter_import():
    """Test if we can import OpenRouter module"""
    print("📦 TESTING IMPORTS")
    print("=" * 40)
    
    try:
        from app.ai_openrouter import OpenRouterAI
        print("✅ OpenRouterAI imported successfully")
        
        # Test initialization
        ai = OpenRouterAI()
        if ai.api_key:
            print(f"✅ API Key found: {ai.api_key[:15]}...")
        else:
            print("❌ API Key not found")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False

async def test_openrouter_connection():
    """Test OpenRouter connection"""
    print("\n🔗 TESTING CONNECTION")
    print("=" * 40)
    
    try:
        from app.ai_openrouter import OpenRouterAI
        
        async with OpenRouterAI() as ai:
            response = await ai.generate_response("Ответь одним словом: УСПЕХ")
            print(f"✅ Response: {response}")
            
            if "успех" in response.lower() or "success" in response.lower():
                print("🎉 OpenRouter is working correctly!")
                return True
            else:
                print(f"⚠️ Unexpected response: {response}")
                return False
                
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def test_ai_manager():
    """Test AI manager"""
    print("\n🎯 TESTING AI MANAGER")
    print("=" * 40)
    
    try:
        from app.ai_manager import get_ai_manager
        
        manager = await get_ai_manager()
        info = manager.get_provider_info()
        
        print(f"Active provider: {info['active_provider']}")
        print(f"Available providers: {info['available_providers']}")
        
        # Test response
        response = await manager.generate_response("Скажи привет и представься")
        print(f"Manager response: {response[:150]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Manager test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 COMPREHENSIVE OPENROUTER TEST")
    print("=" * 50)
    
    # Run tests
    success1 = asyncio.run(test_openrouter_import())
    success2 = asyncio.run(test_openrouter_connection())
    success3 = asyncio.run(test_ai_manager())
    
    print("\n" + "=" * 50)
    if success1 and success2 and success3:
        print("🎉 ALL TESTS PASSED! OpenRouter integration is ready!")
    else:
        print("⚠️ SOME TESTS FAILED - check configuration")
    print("=" * 50)