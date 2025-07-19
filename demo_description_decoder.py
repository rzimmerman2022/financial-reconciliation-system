"""
Demo script showing how to use the Description Decoder with real transaction data.

This script reads actual transactions from the CSV files and shows how the
decoder interprets various description patterns.
"""

import csv
from decimal import Decimal, InvalidOperation
from description_decoder import decode_transaction
import os


def clean_amount(amount_str):
    """Clean and convert amount string to Decimal."""
    if not amount_str or amount_str.strip() in ['', '$ -', '$-', '-']:
        return Decimal('0')
    
    # Remove $ and spaces, handle commas
    cleaned = amount_str.replace('$', '').replace(',', '').replace(' ', '')
    if not cleaned or cleaned == '-':
        return Decimal('0')
    
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return Decimal('0')


def analyze_csv_transactions(csv_path, max_examples=20):
    """Analyze transactions from CSV file and show decoder results."""
    
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return
    
    print(f"\nAnalyzing transactions from: {os.path.basename(csv_path)}")
    print("=" * 80)
    
    interesting_patterns = []
    pattern_counts = {
        "full_reimbursement": 0,
        "gift": 0,
        "personal_ryan": 0,
        "personal_jordyn": 0,
        "manual_review": 0,
        "split_50_50": 0
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8', errors='ignore') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader):
                if i >= 100:  # Limit processing for demo
                    break
                
                # Extract data from CSV
                name = row.get('Name', '').strip()
                description = row.get(' Description ', '').strip()  # Note the spaces in column name
                actual_amount_str = row.get(' Actual Amount ', '').strip()  # Note the spaces in column name
                
                # Skip empty rows
                if not name or not actual_amount_str:
                    continue
                
                # Convert amount
                actual_amount = clean_amount(actual_amount_str)
                if actual_amount <= 0:
                    continue
                
                # Decode the transaction
                result = decode_transaction(description, actual_amount, name)
                
                # Count patterns
                pattern_counts[result["action"]] += 1
                
                # Collect interesting examples
                if result["action"] != "split_50_50" or "2x to calculate" in description.lower():
                    interesting_patterns.append({
                        "row": i + 2,  # +2 for header and 0-indexing
                        "name": name,
                        "description": description,
                        "amount": actual_amount,
                        "result": result
                    })
    
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Show interesting patterns
    print(f"\nFound {len(interesting_patterns)} transactions with special patterns:")
    print("-" * 80)
    
    shown = 0
    for example in interesting_patterns:
        if shown >= max_examples:
            print(f"\n... and {len(interesting_patterns) - shown} more examples")
            break
        
        print(f"\nRow {example['row']}: {example['name']} - ${example['amount']}")
        print(f"Description: {example['description']}")
        print(f"Action: {example['result']['action']}")
        print(f"Payer Share: ${example['result']['payer_share']}")
        print(f"Other Share: ${example['result']['other_share']}")
        print(f"Reason: {example['result']['reason']}")
        print(f"Confidence: {example['result']['confidence']}")
        
        if example['result']['extracted_data']:
            print(f"Extracted Data: {example['result']['extracted_data']}")
        
        print("-" * 40)
        shown += 1
    
    # Show summary statistics
    print("\nPattern Summary:")
    print("-" * 30)
    total = sum(pattern_counts.values())
    for pattern, count in pattern_counts.items():
        percentage = (count / total * 100) if total > 0 else 0
        print(f"{pattern:20}: {count:3} ({percentage:5.1f}%)")
    print(f"{'Total':20}: {total:3}")


def demo_specific_patterns():
    """Demonstrate specific patterns with detailed explanations."""
    
    print("\n" + "=" * 80)
    print("DESCRIPTION DECODER PATTERN DEMONSTRATIONS")
    print("=" * 80)
    
    test_cases = [
        {
            "description": "100% Jordyn (2x to calculate appropriately)",
            "amount": Decimal("11.20"),
            "payer": "Ryan",
            "explanation": "This is the classic '2x to calculate' pattern. The system originally doubled amounts for reimbursement calculations, so this means Jordyn owes Ryan the full $11.20."
        },
        {
            "description": "$85.31 (Birthday present portion, 2x to calculate)",
            "amount": Decimal("170.63"),
            "payer": "Ryan",
            "explanation": "Mixed pattern: birthday + 2x to calculate. The '2x to calculate' takes priority, so this is full reimbursement, not a gift."
        },
        {
            "description": "Jordyn Christmas Present",
            "amount": Decimal("6.50"),
            "payer": "Ryan",
            "explanation": "Clear gift pattern. Ryan bought this as a present for Jordyn, so no reimbursement needed."
        },
        {
            "description": "***Remove $29.99 for Back Stretching Device***",
            "amount": Decimal("100.69"),
            "payer": "Ryan",
            "explanation": "Exclusion pattern. Remove $29.99 from $100.69, leaving $70.70 to split 50/50 = $35.35 each."
        },
        {
            "description": "Lost (I will take half the financial burden as a sign of good faith)",
            "amount": Decimal("220.00"),
            "payer": "Ryan",
            "explanation": "Unclear pattern requiring manual review. The description indicates custom handling needed."
        },
        {
            "description": "Split $14.33 2463 / $29.06 EBT",
            "amount": Decimal("43.39"),
            "payer": "Ryan",
            "explanation": "Split payment pattern. Multiple payment methods used, requires manual review to properly allocate."
        },
        {
            "description": "Regular grocery shopping",
            "amount": Decimal("75.50"),
            "payer": "Ryan",
            "explanation": "Standard transaction with no special patterns. Split 50/50 between Ryan and Jordyn."
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nEXAMPLE {i}:")
        print(f"Description: {test['description']}")
        print(f"Amount: ${test['amount']}")
        print(f"Payer: {test['payer']}")
        print(f"Explanation: {test['explanation']}")
        print()
        
        result = decode_transaction(test['description'], test['amount'], test['payer'])
        
        print("DECODER RESULT:")
        print(f"  Action: {result['action']}")
        print(f"  {test['payer']} pays: ${result['payer_share']}")
        print(f"  Other person owes: ${result['other_share']}")
        print(f"  Reason: {result['reason']}")
        print(f"  Confidence: {result['confidence']}")
        
        if result['extracted_data']:
            print(f"  Extracted Data: {result['extracted_data']}")
        
        print("-" * 60)


if __name__ == "__main__":
    print("FINANCIAL RECONCILIATION - DESCRIPTION DECODER DEMO")
    print("=" * 60)
    
    # Demo specific patterns first
    demo_specific_patterns()
    
    # Analyze real CSV data
    csv_path = "data/raw/Consolidated_Expense_History_20250622.csv"
    if os.path.exists(csv_path):
        analyze_csv_transactions(csv_path, max_examples=15)
    else:
        print(f"\nCSV file not found: {csv_path}")
        print("Place your expense CSV file in the data/raw/ directory to see real data analysis.")
    
    print("\n" + "=" * 60)
    print("DECODER READY FOR INTEGRATION")
    print("=" * 60)
    print("The description_decoder.py module is ready to be integrated into your")
    print("financial reconciliation system. Import and use the decode_transaction()")
    print("function to process transaction descriptions automatically.")
