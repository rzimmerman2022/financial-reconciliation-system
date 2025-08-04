#!/usr/bin/env python3
"""
Launcher for Ultra Modern Reconciliation GUI
==========================================

Simple launcher script for the beautiful reconciliation interface.
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
from src.review.ultra_modern_reconciliation_gui import main

if __name__ == "__main__":
    print("🚀 Launching Ultra Modern Reconciliation GUI...")
    print("✨ Features:")
    print("  - Beautiful gradient backgrounds")
    print("  - Smooth animations")
    print("  - Keyboard shortcuts (1-5 for categories, Enter to submit)")
    print("  - Visual progress tracking")
    print("  - Session statistics")
    print("\nPress Ctrl+C to exit\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using the reconciliation system!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure the database exists at: data/phase5_manual_reviews.db")