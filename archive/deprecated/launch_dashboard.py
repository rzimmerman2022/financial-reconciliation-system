#!/usr/bin/env python3
"""
Dashboard Launcher
==================

Simple launcher for the modern financial dashboard.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Check for customtkinter
try:
    import customtkinter
except ImportError:
    print("Installing required package: customtkinter...")
    os.system(f"{sys.executable} -m pip install customtkinter")
    import customtkinter

# Launch the GUI
print("="*60)
print("LAUNCHING MODERN FINANCIAL DASHBOARD")
print("="*60)
print("\nFeatures:")
print("  - Real-time balance tracking")
print("  - Monthly summaries and analytics")
print("  - Beautiful dark/light theme")
print("  - Interactive transaction viewer")
print("  - Comprehensive financial insights")
print("\nLoading data...")

from modern_aesthetic_gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nThank you for using the Financial Dashboard!")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()