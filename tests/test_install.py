#!/usr/bin/env python3
"""
Test if all required packages are installed
"""
import importlib

print("📦 CHECKING PACKAGES")
print("=" * 40)

packages = [
    'requests',
    'aiohttp', 
    'telegram',
    'tinkoff',
    'dotenv'
]

for package in packages:
    try:
        importlib.import_module(package)
        print(f"✅ {package}: INSTALLED")
    except ImportError as e:
        print(f"❌ {package}: MISSING - {e}")

print("=" * 40)