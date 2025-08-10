#!/usr/bin/env python3
"""
Premium Dashboard Launcher
==========================
Quick launcher for the ultra-modern financial reconciliation dashboard.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import and launch the dashboard
from ultra_modern_dashboard import main

if __name__ == "__main__":
    print("Launching Premium Financial Dashboard v5.0...")
    print("=" * 50)
    print("Features:")
    print("  * Ultra-modern glassmorphic design")
    print("  * Real-time data visualization")
    print("  * Premium animations and effects")
    print("  * Interactive charts and analytics")
    print("  * Dark/Light theme support")
    print("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nDashboard closed.")
    except Exception as e:
        print(f"\nError: {e}")
        input("Press Enter to exit...")