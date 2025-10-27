#!/usr/bin/env python3
"""
Basic Python environment test
"""
import sys

print("🐍 BASIC PYTHON TEST")
print("=" * 40)

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

try:
    import requests
    print("✅ requests module: OK")
except ImportError:
    print("❌ requests module: NOT FOUND")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv: OK")
except ImportError:
    print("❌ python-dotenv: NOT FOUND")

print("=" * 40)