#!/usr/bin/env python3
"""
Simple DeepSeek API test
"""
import os
import requests
import json
from dotenv import load_dotenv

def main():
    print("=" * 50)
    print("🤖 SIMPLE DEEPSEEK API TEST")
    print("=" * 50)
    
    # Load environment
    load_dotenv()
    
    # Check API key
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ DEEPSEEK_API_KEY not found in .env file")
        print("💡 Make sure .env contains: DEEPSEEK_API_KEY=your_key_here")
        return
    
    print(f"✅ API Key found: {api_key[:8]}...")
    
    # Test API connection
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Say just 'TEST OK' in Russian"}
        ],
        "max_tokens": 10
    }
    
    print("🔄 Sending request to DeepSeek...")
    
    try:
        # Add timeout to prevent hanging
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result:
                message = result['choices'][0]['message']['content']
                print(f"✅ Response: {message}")
            else:
                print(f"❌ No choices in response: {result}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - API not responding")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - check internet connection")
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("=" * 50)

if __name__ == "__main__":
    main()