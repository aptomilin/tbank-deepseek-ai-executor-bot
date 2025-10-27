#!/usr/bin/env python3
"""
Test runner for Telegram + DeepSeek AI integration tests
"""
import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def run_telegram_deepseek_tests():
    """Run Telegram + DeepSeek AI integration tests"""
    print("🤖 Running Telegram + DeepSeek AI Integration Tests...")
    print("="*60)
    
    # Run integration tests
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_telegram_deepseek_integration.py",
        "-v",
        "--tb=short",
        "--log-level=INFO"
    ], capture_output=True, text=True)
    
    # Print test output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_telegram_deepseek_tests())