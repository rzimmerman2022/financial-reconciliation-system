#!/usr/bin/env python3
"""Test database access and pending transactions."""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.review.manual_review_system import ManualReviewSystem

try:
    print("Testing database access...")
    review_system = ManualReviewSystem("../../data/phase5_manual_reviews.db")
    
    print("Getting pending reviews...")
    pending = review_system.get_pending_reviews()
    
    print(f"Found {len(pending)} pending transactions")
    
    if not pending.empty:
        print("\nFirst pending transaction:")
        print(pending.iloc[0])
    else:
        print("No pending transactions found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()