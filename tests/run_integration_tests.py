#!/usr/bin/env python3
"""
Integration test runner
"""
import subprocess
import sys
import json


def run_integration_tests():
    """Run all integration tests with detailed reporting"""
    print("🚀 Running Comprehensive Integration Tests...")
    print("="*60)
    
    # Run integration tests
    result = subprocess.run([
        sys.executable, "-m", "pytest",
        "tests/test_integration.py",
        "-v",
        "--tb=short",
        "--log-level=INFO"
    ], capture_output=True, text=True)
    
    # Print test output
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    # Run component tests for completeness
    print("\n" + "="*60)
    print("Running Component Tests...")
    print("="*60)
    
    component_result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_tinkoff_client.py",
        "-v",
        "--tb=short"
    ], capture_output=True, text=True)
    
    print(component_result.stdout)
    
    # Generate final report
    print("\n" + "="*60)
    print("📊 FINAL TEST SUMMARY")
    print("="*60)
    
    if result.returncode == 0 and component_result.returncode == 0:
        print("✅ ALL TESTS PASSED!")
        print("🎯 Application is ready for production use")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please check the test output above")
        return 1


if __name__ == "__main__":
    sys.exit(run_integration_tests())