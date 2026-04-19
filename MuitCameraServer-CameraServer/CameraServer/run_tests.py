#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main test runner for Camera Server project
Runs all tests without connecting to real servers
"""

import sys
import os
import subprocess

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_test_file(test_file):
    """Run a single test file"""
    print(f"\n{'=' * 70}")
    print(f"Running: {test_file}")
    print('=' * 70)
    
    # Get the CameraServer directory (parent of tests)
    camera_server_dir = os.path.dirname(os.path.abspath(__file__))
    
    result = subprocess.run(
        [sys.executable, test_file],
        cwd=camera_server_dir
    )
    
    return result.returncode == 0


def main():
    """Main test runner"""
    print("\n")
    print("=" * 70)
    print(" CAMERA SERVER - STANDALONE TEST SUITE".center(70))
    print(" (No external servers required)".center(70))
    print("=" * 70)
    
    test_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
    
    tests = [
        os.path.join(test_dir, 'test_database.py'),
        os.path.join(test_dir, 'test_algorithms.py'),
        os.path.join(test_dir, 'test_integration.py'),
    ]
    
    results = {}
    total_tests = len(tests)
    passed_tests = 0
    
    for test_file in tests:
        test_name = os.path.basename(test_file)
        if os.path.exists(test_file):
            try:
                if run_test_file(test_file):
                    results[test_name] = "[OK] PASSED"
                    passed_tests += 1
                else:
                    results[test_name] = "[FAIL] FAILED"
            except Exception as e:
                results[test_name] = f"[ERROR]: {e}"
        else:
            results[test_name] = "[FAIL] NOT FOUND"
    
    # Print summary
    print("\n")
    print("=" * 70)
    print(" TEST SUMMARY".center(70))
    print("=" * 70)
    
    for test_name, result in results.items():
        status_str = f"{result}".ljust(20)
        print(f" {test_name.ljust(40)} {status_str} ")
    
    print("=" * 70)
    print(f" Total: {passed_tests}/{total_tests} tests passed".ljust(71))
    print("=" * 70 + "\n")
    
    if passed_tests == total_tests:
        print("[SUCCESS] All tests passed! Project is working correctly.\n")
        return 0
    else:
        print("[WARNING] Some tests failed. Check output above for details.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
