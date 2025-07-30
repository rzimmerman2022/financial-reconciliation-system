#!/usr/bin/env python3
"""
Main entry point for the Financial Reconciliation System.

Usage:
    python run.py --mode from_baseline
    python run.py --mode from_scratch
    python run.py --help
"""

import sys
import subprocess
from pathlib import Path

if __name__ == "__main__":
    # Run the main script
    script_path = Path(__file__).parent / "scripts" / "run_with_review.py"
    subprocess.run([sys.executable, str(script_path)] + sys.argv[1:])