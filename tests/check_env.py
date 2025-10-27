#!/usr/bin/env python3
"""
Check .env file and variables
"""
import os
from dotenv import load_dotenv

print("🔍 CHECKING ENVIRONMENT")
print("=" * 40)

# Check if .env exists
if os.path.exists('.env'):
    print("✅ .env file exists")
    
    # Read .env content (hide sensitive data)
    with open('.env', 'r') as f:
        lines = f.readlines()
        print(f"📄 .env has {len(lines)} lines")
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '=' in line:
                    key = line.split('=')[0]
                    value = line.split('=')[1]
                    if value:
                        print(f"   {key}: [SET] ({len(value)} chars)")
                    else:
                        print(f"   {key}: [EMPTY]")
                else:
                    print(f"   ⚠️  Invalid line: {line}")
else:
    print("❌ .env file not found!")

print("\n📋 LOADED VARIABLES:")
print("-" * 40)

# Load environment
load_dotenv()

variables = ['DEEPSEEK_API_KEY', 'TELEGRAM_BOT_TOKEN', 'TINKOFF_TOKEN']
for var in variables:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: Present ({len(value)} chars)")
    else:
        print(f"❌ {var}: NOT FOUND")

print("=" * 40)