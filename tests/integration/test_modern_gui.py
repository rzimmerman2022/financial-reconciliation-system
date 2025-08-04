#!/usr/bin/env python3
"""Test script to launch the modern GUI with error handling."""

import sys
import traceback
from pathlib import Path

# Add project root directory for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    print("Starting Modern Transaction Review GUI...")
    print("-" * 50)
    
    # Import and run
    from src.review.modern_visual_review_gui import src.main as main
    main()
    
except Exception as e:
    print(f"\nERROR: {type(e).__name__}: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    
    print("\nPress Enter to exit...")
    input()