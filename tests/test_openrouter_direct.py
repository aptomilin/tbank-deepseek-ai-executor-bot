#!/usr/bin/env python3
"""
Direct OpenRouter test without complex imports
"""
import os
import sys
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

async def test_openrouter_direct():
    """Test OpenRouter API directly"""
    print("🤖 DIRECT OPENROUTER TEST")
    print("=" * 50)
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False
    
    print(f"🔑 API Key: {api_key[:15]}...")
    
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
    
    print("🔄 Sending request to OpenRouter...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, 
                json=data, 
                headers=headers, 
                timeout=30
            ) as response:
                
                print(f"📡 Status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    message = result['choices'][0]['message']['content']
                    print(f"✅ Response: {message}")
                    print("🎉 OpenRouter API is working!")
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
    success = asyncio.run(test_openrouter_direct())
    
    if success:
        print("\n🎉 OpenRouter is ready for integration!")
    else:
        print("\n❌ OpenRouter test failed")
    
    print("=" * 50)