#!/usr/bin/env python3
"""
Final AI system test
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

# Add parent directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

async def test_final_ai_system():
    """Test the complete AI system"""
    print("🎯 FINAL AI SYSTEM TEST")
    print("=" * 50)
    
    try:
        from app.ai_manager import get_ai_manager
        
        manager = await get_ai_manager()
        info = manager.get_provider_info()
        
        print("📊 AI SYSTEM STATUS:")
        print(f"   Active provider: {info['active_provider']}")
        print(f"   Available providers: {info['available_providers']}")
        print(f"   Total providers: {info['providers_count']}")
        
        # Test portfolio analysis
        print("\n🧪 TESTING PORTFOLIO ANALYSIS:")
        portfolio_data = {
            'total_value': 150000,
            'stocks_value': 100000,
            'bonds_value': 50000,
            'etf_value': 0,
            'positions_count': 3
        }
        
        analysis = await manager.analyze_portfolio(portfolio_data)
        print(f"   Analysis: {analysis[:200]}...")
        
        # Test general question
        print("\n💬 TESTING GENERAL QUESTION:")
        response = await manager.generate_response("Какие акции купить для начинающего инвестора?")
        print(f"   Response: {response[:200]}...")
        
        print("\n🎉 AI SYSTEM IS OPERATIONAL!")
        print("💡 The system will automatically use the best available provider")
        
        return True
        
    except Exception as e:
        print(f"❌ AI system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_final_ai_system())
    
    if success:
        print("\n✅ YOUR INVESTMENT ADVISOR IS READY!")
        print("🤖 The bot will use AI when available, fallback when not")
    else:
        print("\n❌ AI system needs configuration")
    
    print("=" * 50)