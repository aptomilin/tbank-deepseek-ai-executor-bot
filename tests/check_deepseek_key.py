#!/usr/bin/env python3
"""
Check DeepSeek API key format
"""
import os
from dotenv import load_dotenv

print("🔍 DEEPSEEK KEY CHECK")
print("=" * 40)

load_dotenv()

api_key = os.getenv('DEEPSEEK_API_KEY')

if api_key:
    print(f"Current key: {api_key}")
    print(f"Key length: {len(api_key)}")
    print(f"Key starts with: {api_key[:10]}")
    
    # DeepSeek keys typically start with 'sk-' and are 32+ characters
    if api_key.startswith('sk-') and len(api_key) >= 20:
        print("✅ Key format looks correct")
    else:
        print("❌ Key format is incorrect!")
        print("💡 DeepSeek keys should start with 'sk-' and be ~32 characters")
else:
    print("❌ No API key found")

print("=" * 40)