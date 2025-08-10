#!/usr/bin/env python3
"""
Web Interface Launcher for Financial Reconciliation System

Run the web-based reconciliation interface with manual transaction review.

Usage: python reconcile_web.py
"""

import subprocess
import sys

def main():
    """Launch the gold standard web interface."""
    print("=" * 60)
    print("Financial Reconciliation System - Gold Standard Edition")
    print("=" * 60)
    print("Launching modern web interface...")
    print("Opening at: http://localhost:5000")
    print("=" * 60)
    
    try:
        subprocess.run([sys.executable, "-m", "src.review.web_interface"])
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()