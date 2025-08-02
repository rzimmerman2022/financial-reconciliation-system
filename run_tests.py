#!/usr/bin/env python3
"""
Test runner script for the Financial Reconciliation System.
This script runs all tests and generates coverage reports.
"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all tests with coverage reporting."""
    print("=" * 60)
    print("Financial Reconciliation System - Test Runner")
    print("=" * 60)
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ]
    
    print(f"\nRunning command: {' '.join(cmd)}")
    print("-" * 60)
    
    result = subprocess.run(cmd, cwd=project_root)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()