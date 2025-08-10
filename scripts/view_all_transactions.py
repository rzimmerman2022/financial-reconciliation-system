#!/usr/bin/env python3
"""
Simple Transaction Viewer
=========================

View all transactions from the very beginning in chronological order.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import csv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def load_legacy_data():
    """Load Phase 4 legacy data (through Sept 30, 2024)."""
    print("=== PHASE 4 LEGACY DATA (Through Sept 30, 2024) ===")
    
    files = [
        ("test-data/legacy/Consolidated_Expense_History_20250622.csv", "Expense History"),
        ("test-data/legacy/Consolidated_Rent_Allocation_20250527.csv", "Rent Allocation"), 
        ("test-data/legacy/Zelle_From_Jordyn_Final.csv", "Zelle Payments")
    ]
    
    all_transactions = []
    
    for file_path, description in files:
        try:
            print(f"\n--- {description} ---")
            df = pd.read_csv(file_path)
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            
            # Show first few rows
            print("\nFirst 5 rows:")
            for i, row in df.head().iterrows():
                print(f"  {i+1}: {dict(row)}")
                
            all_transactions.extend([(file_path, description, row) for _, row in df.iterrows()])
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return all_transactions

def load_bank_exports():
    """Load Phase 5+ bank export data (Oct 1, 2024 onwards)."""
    print("\n\n=== PHASE 5+ BANK EXPORTS (Oct 1, 2024 onwards) ===")
    
    bank_files = list(Path("test-data/bank-exports").glob("*.csv"))
    
    all_transactions = []
    
    for file_path in bank_files:
        try:
            print(f"\n--- {file_path.name} ---")
            df = pd.read_csv(file_path)
            print(f"Columns: {list(df.columns)}")
            print(f"Shape: {df.shape}")
            
            # Show first few rows
            print("\nFirst 3 rows:")
            for i, row in df.head(3).iterrows():
                print(f"  {i+1}: {dict(row)}")
                
            all_transactions.extend([(str(file_path), file_path.name, row) for _, row in df.iterrows()])
            
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return all_transactions

def main():
    """Main function to view all transactions."""
    print("FINANCIAL RECONCILIATION - ALL TRANSACTIONS VIEWER")
    print("=" * 60)
    
    # Load all data
    legacy_transactions = load_legacy_data()
    bank_transactions = load_bank_exports()
    
    print(f"\n\nSUMMARY:")
    print(f"Legacy transactions (Phase 4): {len(legacy_transactions)}")
    print(f"Bank export transactions (Phase 5+): {len(bank_transactions)}")
    print(f"Total transactions found: {len(legacy_transactions) + len(bank_transactions)}")
    
    # Ask user what they want to see
    print(f"\nWhat would you like to view?")
    print(f"1. All legacy transactions (detailed)")
    print(f"2. All bank export transactions (detailed)")
    print(f"3. Summary by file")
    print(f"4. Exit")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        show_transactions(legacy_transactions, "LEGACY TRANSACTIONS")
    elif choice == "2":
        show_transactions(bank_transactions, "BANK EXPORT TRANSACTIONS")
    elif choice == "3":
        show_summary_by_file(legacy_transactions, bank_transactions)
    else:
        print("Exiting...")

def show_transactions(transactions, title):
    """Show detailed transaction list."""
    print(f"\n{title}")
    print("=" * len(title))
    
    for i, (file_path, description, row) in enumerate(transactions[:50], 1):  # Show first 50
        print(f"\n{i}. From: {description}")
        print(f"   Data: {dict(row)}")
        
        if i >= 50:
            print(f"\n... showing first 50 of {len(transactions)} transactions")
            break

def show_summary_by_file(legacy_transactions, bank_transactions):
    """Show summary statistics by file."""
    print(f"\nFILE SUMMARY")
    print("=" * 20)
    
    # Group by file
    file_counts = {}
    
    for file_path, description, row in legacy_transactions + bank_transactions:
        if file_path not in file_counts:
            file_counts[file_path] = {"description": description, "count": 0}
        file_counts[file_path]["count"] += 1
    
    for file_path, info in file_counts.items():
        print(f"{info['description']}: {info['count']} transactions")
        print(f"  File: {file_path}")

if __name__ == "__main__":
    main()