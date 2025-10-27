#!/usr/bin/env python3
"""
OpenRouter test with SSL verification disabled (for testing only)
"""
import os
import sys
import asyncio
import aiohttp
import ssl
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

async def test_openrouter_no_ssl():
    """Test OpenRouter with SSL verification disabled"""
    print("🔓 OPENROUTER TEST (SSL DISABLED - FOR TESTING ONLY)")
    print("=" * 60)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    print(f"🔑 API Key: {api_key[:15]}...")
    
    # Create SSL context that doesn't verify certificates
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "https://github.com/investment-bot",
        "X-Title": "Investment Advisor Test"
    }
    
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Ты инвестиционный советник. Отвечай кратко на русском."
            },
            {
                "role": "user",
                "content": "Скажи одним словом: РАБОТАЕТ"
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    print("🔄 Sending request to OpenRouter (SSL disabled)...")
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=30,
                ssl=ssl_context
            ) as response:
                
                print(f"📡 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content']
                    print(f"✅ Response: {message}")
                    print("🎉 OpenRouter API is working! (with SSL disabled)")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ Error {response.status}: {error_text}")
                    return False
                    
    except asyncio.TimeoutError:
        print("❌ Timeout - API not responding")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("⚠️  WARNING: SSL verification is disabled for this test!")
    print("⚠️  This should only be used for testing purposes!")
    print("=" * 60)
    
    success = asyncio.run(test_openrouter_no_ssl())
    
    if success:
        print("\n🎉 OpenRouter works! The issue is SSL certificates.")
        print("💡 Solution: Install/update SSL certificates on your system")
    else:
        print("\n❌ OpenRouter still doesn't work even with SSL disabled")
    
    print("=" * 60)