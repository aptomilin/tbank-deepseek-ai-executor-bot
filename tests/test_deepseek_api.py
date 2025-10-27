#!/usr/bin/env python3
"""
Test DeepSeek API connection
"""
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_deepseek_connection():
    """Test direct DeepSeek API connection"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return False
    
    print(f"🔑 API Key: {api_key[:10]}...")
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Привет! Ответь коротко 'Тест пройден'"}
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }
    
    try:
        print("🔄 Sending request to DeepSeek API...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                message = result['choices'][0]['message']['content']
                print(f"✅ DeepSeek Response: {message}")
                return True
            else:
                print(f"❌ Unexpected response format: {result}")
                return False
        else:
            print(f"❌ API Error {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def check_deepseek_key_format():
    """Check if API key format is correct"""
    api_key = os.getenv('DEEPSEEK_API_KEY')
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    # DeepSeek keys typically start with 'sk-' and are 32+ characters
    if api_key.startswith('sk-') and len(api_key) >= 20:
        print("✅ API key format looks correct")
        return True
    else:
        print(f"⚠️  API key format may be incorrect: {api_key[:10]}...")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 DEEPSEEK API TEST")
    print("=" * 50)
    
    if check_deepseek_key_format():
        if test_deepseek_connection():
            print("\n🎉 DeepSeek API is working!")
        else:
            print("\n❌ DeepSeek API test failed!")
    else:
        print("\n❌ API key issue!")
    
    print("=" * 50)