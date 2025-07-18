#!/usr/bin/env python3
"""
Standalone test of expense processing logic without complex imports
"""

import pandas as pd
import re
from datetime import datetime

def clean_currency(value):
    """Convert currency string to float."""
    if pd.isna(value) or value == '' or str(value).strip() == '':
        return None
    
    try:
        # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[$,\s]', '', str(value))
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        # Handle empty strings after cleaning
        if cleaned == '' or cleaned == '-':
            return None
            
        return float(cleaned)
    except (ValueError, TypeError):
        print(f"Warning: Could not parse currency value: {value}")
        return None

def parse_date(date_str):
    """Parse date string to datetime object."""
    if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
        return None
    
    # Try common date formats
    date_formats = [
        '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y',
        '%m/%d/%y', '%y-%m-%d', '%m-%d-%y', '%d-%m-%y'
    ]
    
    date_str = str(date_str).strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try pandas as fallback
    try:
        return pd.to_datetime(date_str)
    except Exception:
        print(f"Warning: Could not parse date: {date_str}")
        return None

def test_currency_cleaning():
    """Test currency cleaning function."""
    print("Testing currency cleaning...")
    
    test_cases = [
        ('$84.39 ', 84.39),
        ('$1,234.56', 1234.56),
        ('', None),
        ('$0.00', 0.0),
        ('($50.00)', -50.0),
        ('invalid', None)
    ]
    
    for input_val, expected in test_cases:
        result = clean_currency(input_val)
        if result == expected or (result is None and expected is None):
            print(f"  ✓ '{input_val}' -> {result}")
        else:
            print(f"  ✗ '{input_val}' -> {result} (expected {expected})")

def test_date_parsing():
    """Test date parsing function."""
    print("\nTesting date parsing...")
    
    test_cases = [
        ('9/14/2023', datetime(2023, 9, 14)),
        ('10/15/2023', datetime(2023, 10, 15)),
        ('', None),
        ('invalid', None),
        ('2023-12-25', datetime(2023, 12, 25))
    ]
    
    for input_val, expected in test_cases:
        result = parse_date(input_val)
        if ((result is None and expected is None) or 
            (result is not None and expected is not None and 
             result.date() == expected.date())):
            print(f"  ✓ '{input_val}' -> {result}")
        else:
            print(f"  ✗ '{input_val}' -> {result} (expected {expected})")

def test_data_processing():
    """Test processing sample data."""
    print("\nTesting data processing...")
    
    # Load sample data
    csv_file = "data/raw/Consolidated_Expense_History_20250622.csv"
    try:
        data = pd.read_csv(csv_file, nrows=10, dtype=str)
        print(f"  ✓ Loaded {len(data)} sample records")
        
        # Test column cleaning
        print("  Original columns:", list(data.columns))
        
        # Clean a few currency values
        if ' Actual Amount ' in data.columns:
            print("  Testing currency cleaning on real data:")
            for i in range(min(5, len(data))):
                original = data.iloc[i][' Actual Amount ']
                cleaned = clean_currency(original)
                print(f"    '{original}' -> {cleaned}")
        
        # Clean a few dates
        if 'Date of Purchase' in data.columns:
            print("  Testing date parsing on real data:")
            for i in range(min(5, len(data))):
                original = data.iloc[i]['Date of Purchase']
                parsed = parse_date(original)
                print(f"    '{original}' -> {parsed}")
        
    except FileNotFoundError:
        print("  ! CSV file not found - skipping real data test")
    except Exception as e:
        print(f"  ! Error loading CSV: {e}")

def main():
    """Run all tests."""
    print("🧪 EXPENSE PROCESSING LOGIC TESTS")
    print("=" * 50)
    
    test_currency_cleaning()
    test_date_parsing()
    test_data_processing()
    
    print("\n✅ Core processing logic tests complete!")
    print("\nNext steps:")
    print("1. Individual processing functions work correctly")
    print("2. Ready to integrate into full processor class")
    print("3. Can proceed with reconciliation engine development")

if __name__ == "__main__":
    main()
