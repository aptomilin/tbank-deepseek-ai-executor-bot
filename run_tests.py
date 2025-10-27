#!/usr/bin/env python3
"""
Test runner for regression tests
"""
import subprocess
import sys


def run_tests():
    """Run all regression tests"""
    print("Running TinkoffInvestClient regression tests...")
    
    # Run tests with pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_tinkoff_client.py",
        "-v",
        "--tb=short"
    ])
    
    if result.returncode == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
        
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())