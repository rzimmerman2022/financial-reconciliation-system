#!/usr/bin/env python3
"""
Simple test of the financial reconciliation loaders
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.loaders.expense_loader import ExpenseHistoryLoader
from src.loaders.rent_loader import RentAllocationLoader  
from src.loaders.zelle_loader import ZellePaymentsLoader

def main():
    print("Testing Financial Reconciliation System Loaders")
    print("=" * 50)
    
    # Test expense loader
    print("\n1. Testing Expense History Loader...")
    expense_loader = ExpenseHistoryLoader()
    expense_data = expense_loader.load_raw_data()
    print(f"   Loaded {len(expense_data)} expense records")
    
    # Test rent loader  
    print("\n2. Testing Rent Allocation Loader...")
    rent_loader = RentAllocationLoader()
    rent_data = rent_loader.load_raw_data()
    print(f"   Loaded {len(rent_data)} rent records")
    
    # Test zelle loader
    print("\n3. Testing Zelle Payments Loader...")
    zelle_loader = ZellePaymentsLoader()
    zelle_data = zelle_loader.load_raw_data()
    print(f"   Loaded {len(zelle_data)} Zelle records")
    
    print("\n✅ All loaders working successfully!")
    print(f"\nTotal records loaded: {len(expense_data) + len(rent_data) + len(zelle_data)}")

if __name__ == "__main__":
    main()
