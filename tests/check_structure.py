#!/usr/bin/env python3
"""
Check project structure
"""
import os

print("📁 PROJECT STRUCTURE CHECK")
print("=" * 40)

current_dir = os.getcwd()
print(f"Current directory: {current_dir}")

print("\n📂 Files and folders:")
for item in os.listdir('.'):
    if os.path.isdir(item):
        print(f"  📁 {item}/")
        # Show contents of app directory if it exists
        if item == 'app':
            for subitem in os.listdir('app'):
                print(f"    📄 {subitem}")
    else:
        print(f"  📄 {item}")

print("\n🔍 Python path:")
import sys
print(f"Python path: {sys.path[0]}")
print("=" * 40)