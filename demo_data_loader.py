"""
Demo script showing how to use the data_loader module with the actual data files.

This demonstrates:
1. Loading each CSV file
2. Showing the cleaned column names
3. Displaying sample data with correct types (Decimal for amounts)
4. Running data quality validation
5. Integration with description_decoder from Phase 1
"""

from data_loader import (
    load_expense_history,
    load_rent_allocation,
    load_zelle_payments,
    validate_data_quality
)
from description_decoder import decode_transaction
from decimal import Decimal
import pandas as pd


def main():
    print("Financial Reconciliation System - Data Loader Demo")
    print("=" * 60)
    
    # 1. Load Expense History
    print("\n1. LOADING EXPENSE HISTORY")
    print("-" * 40)
    
    try:
        expense_df = load_expense_history('data/raw/Consolidated_Expense_History_20250622.csv')
        
        print(f"✓ Loaded {len(expense_df)} expense records")
        print(f"\nColumn names after cleaning:")
        print(list(expense_df.columns))
        
        print(f"\nData types:")
        print(f"- actual_amount: {expense_df['actual_amount'].dtype} (Decimal objects)")
        print(f"- date_of_purchase: {expense_df['date_of_purchase'].dtype}")
        
        print(f"\nSample data (first 3 records):")
        for idx in range(min(3, len(expense_df))):
            row = expense_df.iloc[idx]
            print(f"\nRecord {idx + 1}:")
            print(f"  Name: {row['name']}")
            print(f"  Date: {row['date_of_purchase']}")
            print(f"  Merchant: {row.get('merchant', 'N/A')}")
            print(f"  Amount: ${row['actual_amount']}")
            print(f"  Description: {row.get('description', 'N/A')[:50]}...")
        
        # Validate data quality
        print(f"\nData Quality Check:")
        issues = validate_data_quality(expense_df, "Expense History")
        
    except Exception as e:
        print(f"✗ Error loading expense history: {e}")
    
    # 2. Load Rent Allocation
    print("\n\n2. LOADING RENT ALLOCATION")
    print("-" * 40)
    
    try:
        rent_df = load_rent_allocation('data/raw/Consolidated_Rent_Allocation_20250527.csv')
        
        print(f"✓ Loaded {len(rent_df)} rent allocation records")
        print(f"\nColumn names after cleaning:")
        print(list(rent_df.columns))
        
        print(f"\nSample data (first 3 records):")
        print(rent_df.head(3).to_string())
        
        # Validate data quality
        issues = validate_data_quality(rent_df, "Rent Allocation")
        
    except Exception as e:
        print(f"✗ Error loading rent allocation: {e}")
    
    # 3. Load Zelle Payments
    print("\n\n3. LOADING ZELLE PAYMENTS")
    print("-" * 40)
    
    try:
        zelle_df = load_zelle_payments('data/raw/Zelle_From_Jordyn_Final.csv')
        
        print(f"✓ Loaded {len(zelle_df)} Zelle payments")
        print(f"  All payments are FROM: {zelle_df['from_person'].iloc[0]}")
        print(f"  All payments are TO: {zelle_df['to_person'].iloc[0]}")
        
        print(f"\nColumn names after cleaning:")
        print(list(zelle_df.columns))
        
        print(f"\nSample data:")
        print(zelle_df.head(3).to_string())
        
        # Validate data quality
        issues = validate_data_quality(zelle_df, "Zelle Payments")
        
    except Exception as e:
        print(f"✗ Error loading Zelle payments: {e}")
    
    # 4. Demonstrate integration with description_decoder
    print("\n\n4. INTEGRATION WITH DESCRIPTION DECODER")
    print("-" * 40)
    
    if 'expense_df' in locals():
        print("Testing description decoder on sample transactions:")
        
        # Find some interesting transactions to decode
        test_indices = []
        
        # Look for specific patterns
        for idx, row in expense_df.iterrows():
            desc = str(row.get('description', '')).lower()
            if any(pattern in desc for pattern in ['2x to calculate', 'gift', '100%', 'remove']):
                test_indices.append(idx)
                if len(test_indices) >= 5:
                    break
        
        # If we didn't find interesting ones, just use first 3
        if not test_indices:
            test_indices = list(range(min(3, len(expense_df))))
        
        for idx in test_indices:
            row = expense_df.iloc[idx]
            
            # Decode the transaction
            result = decode_transaction(
                description=row.get('description', ''),
                amount=row['actual_amount'],
                payer=row['name']
            )
            
            print(f"\nTransaction:")
            print(f"  Payer: {row['name']}")
            print(f"  Amount: ${row['actual_amount']}")
            print(f"  Description: {row.get('description', 'N/A')[:60]}...")
            print(f"  → Action: {result['action']}")
            print(f"  → Payer Share: ${result['payer_share']}")
            print(f"  → Other Share: ${result['other_share']}")
            print(f"  → Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
    print("Demo complete! The data_loader module successfully:")
    print("- Cleaned column names (removed spaces, converted to lowercase)")
    print("- Converted currency values to Decimal for precision")
    print("- Parsed various date formats")
    print("- Validated data quality")
    print("- Integrated with the description_decoder from Phase 1")


if __name__ == "__main__":
    main()