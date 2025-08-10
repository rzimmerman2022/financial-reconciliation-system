#!/usr/bin/env python3
"""
Ultra-Premium Financial GUI Launcher
====================================

Professional launcher for the world-class financial reconciliation interface.

Features:
- Ultra-modern glassmorphic design with premium aesthetics
- Smooth animations and delightful micro-interactions  
- Gold-standard color scheme and typography
- Intuitive category selection with visual feedback
- Keyboard shortcuts for power users
- Real-time validation and smart suggestions
- Session tracking and export capabilities
- Accessibility-compliant design

Version: 6.0.0 Ultra Premium
Date: August 10, 2025
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Ultra-Premium Financial Reconciliation GUI")
print("=" * 50)
print("Version: 6.0.0 Ultra Premium")
print("")
print("Features:")
print("  * Gold-standard design system with premium aesthetics")
print("  * Smooth animations and delightful micro-interactions")
print("  * Intuitive color-coded category selection")
print("  * Professional typography and visual hierarchy")
print("  * Keyboard shortcuts for efficient workflow")
print("  * Real-time validation and smart suggestions")
print("  * Session tracking and export capabilities")
print("  * Accessibility-compliant design (WCAG AA)")
print("")
print("=" * 50)
print("Starting application...")
print("")

try:
    from src.review.ultra_premium_gui import main
    main()
except KeyboardInterrupt:
    print("\nApplication closed by user.")
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"Error: {e}")
    input("Press Enter to exit...")