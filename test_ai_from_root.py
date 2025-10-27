#!/usr/bin/env python3
"""
Test AI from root directory
"""
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    print("🎯 TESTING AI FROM ROOT DIRECTORY")
    print("=" * 50)
    
    # This should work since we're in root
    try:
        from app.ai_manager import get_ai_manager
        
        manager = await get_ai_manager()
        info = manager.get_provider_info()
        
        print(f"Active AI provider: {info['active_provider']}")
        print(f"Available providers: {info['available_providers']}")
        
        # Test response
        response = await manager.generate_response("Привет! Скажи что AI система работает")
        print(f"\n🤖 AI Response:\n{response}")
        
        print("\n🎉 AI SYSTEM IS READY!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())