#!/usr/bin/env python3
"""
Simple test script without imports to verify Python setup
"""

import pandas as pd
from pathlib import Path

def main():
    print("Testing Python environment and pandas...")
    
    # Test pandas
    df = pd.DataFrame({'test': [1, 2, 3]})
    print(f"Pandas working: Created DataFrame with {len(df)} rows")
    
    # Test file reading
    csv_file = Path("data/raw/Consolidated_Expense_History_20250622.csv")
    if csv_file.exists():
        data = pd.read_csv(csv_file, nrows=5)
        print(f"CSV reading working: Loaded {len(data)} sample rows")
        print(f"Columns: {list(data.columns)}")
    else:
        print("CSV file not found")
    
    print("Basic functionality test complete!")

if __name__ == "__main__":
    main()
