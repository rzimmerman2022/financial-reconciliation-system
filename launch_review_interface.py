#!/usr/bin/env python3
"""
Universal Launch Script for Financial Reconciliation Review Interfaces

This script provides a simple way to launch any of the available review interfaces:
- Gold Standard Web Interface (default and recommended)
- Desktop GUI Interface  
- Command Line Interface

Usage:
    python launch_review_interface.py [web|desktop|cli]
    
Examples:
    python launch_review_interface.py           # Launch web interface (default)
    python launch_review_interface.py web       # Launch web interface explicitly
    python launch_review_interface.py desktop   # Launch desktop GUI
    python launch_review_interface.py cli       # Launch command line interface
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the appropriate review interface based on user preference."""
    
    # Default to web interface
    interface = sys.argv[1] if len(sys.argv) > 1 else "web"
    
    print("🏦 Financial Reconciliation System - Review Interface Launcher")
    print("=" * 65)
    
    if interface == "web":
        print("🌟 Launching Gold Standard Web Interface...")
        print("   • Modern glassmorphism design")
        print("   • Responsive mobile-first layout")
        print("   • Real-time progress tracking")
        print("   • Keyboard shortcuts and smooth animations")
        print()
        print("🌐 Opening at: http://localhost:5000")
        print("=" * 65)
        
        subprocess.run([sys.executable, "create_modern_web_gui.py"])
        
    elif interface == "desktop":
        print("🖥️ Launching Desktop GUI Interface...")
        print("   • Material Design interface")
        print("   • Tkinter-based desktop application")
        print("   • Full-featured transaction review")
        print("=" * 65)
        
        subprocess.run([sys.executable, "-m", "src.review.modern_visual_review_gui"])
        
    elif interface == "cli":
        print("⌨️ Launching Command Line Interface...")
        print("   • Text-based transaction review")
        print("   • Keyboard-driven workflow")
        print("   • Lightweight and fast")
        print("=" * 65)
        
        subprocess.run([sys.executable, "bin/manual_review_cli.py"])
        
    else:
        print("❌ Invalid interface option. Available options:")
        print("   • web      - Gold Standard Web Interface (recommended)")
        print("   • desktop  - Desktop GUI Interface")
        print("   • cli      - Command Line Interface")
        print()
        print("Usage: python launch_review_interface.py [web|desktop|cli]")
        sys.exit(1)

if __name__ == "__main__":
    main()