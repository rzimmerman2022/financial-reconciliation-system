#!/usr/bin/env python3
"""Test GUI state after initialization."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

try:
    from src.review.modern_visual_review_gui import ModernTransactionReviewGUI
    
    print("Creating GUI instance...")
    gui = ModernTransactionReviewGUI()
    
    print(f"GUI initialized successfully!")
    print(f"- Transactions loaded: {len(gui.transactions)}")
    print(f"- Current index: {gui.current_index}")
    print(f"- Stats: {gui.stats}")
    
    if gui.transactions:
        print(f"\nFirst transaction:")
        print(f"  Date: {gui.transactions[0]['date']}")
        print(f"  Description: {gui.transactions[0]['description']}")
        print(f"  Amount: ${gui.transactions[0]['amount']}")
        print(f"  Payer: {gui.transactions[0]['payer']}")
    
    print("\nGUI is ready to run. Call gui.run() to start the interface.")
    
    # Clean up
    gui.root.destroy()
    print("GUI cleaned up successfully.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()