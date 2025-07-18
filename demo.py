#!/usr/bin/env python3
"""
Financial Reconciliation System - Full Demo

This script demonstrates the complete pipeline:
1. Load raw CSV data using the loaders
2. Process the data using the processors  
3. Generate analysis and insights

Run this from the project root directory.
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our modules
from loaders.expense_loader import ExpenseHistoryLoader
from processors.expense_processor import ExpenseProcessor

def main():
    print("🏦 FINANCIAL RECONCILIATION SYSTEM - FULL DEMO")
    print("=" * 60)
    
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)
    
    # Step 1: Load raw expense data
    print("\n📁 Step 1: Loading Raw Expense Data")
    print("-" * 40)
    
    expense_loader = ExpenseHistoryLoader()
    raw_expense_data = expense_loader.load_raw_data()
    
    print(f"✓ Loaded {len(raw_expense_data)} raw expense records")
    
    # Show some basic info
    validation = expense_loader.validate_structure()
    if not validation['is_valid']:
        print(f"⚠ Found {len(validation['issues'])} data quality issues")
        print("  Issues include:")
        for issue in validation['issues'][:3]:
            print(f"    • {issue}")
        if len(validation['issues']) > 3:
            print(f"    • ... and {len(validation['issues']) - 3} more")
    
    # Step 2: Process the data
    print("\n🔄 Step 2: Processing and Cleaning Data")
    print("-" * 40)
    
    expense_processor = ExpenseProcessor()
    processed_expense_data = expense_processor.load_and_process(raw_expense_data)
    
    print(f"✓ Processed {len(processed_expense_data)} expense records")
    
    # Get processing summary
    processing_summary = expense_processor.get_processing_summary()
    
    print(f"✓ Valid records: {processing_summary['valid_records']}")
    print(f"✓ Invalid records: {processing_summary['invalid_records']}")
    
    if processing_summary.get('validation_issues'):
        print("  Most common issues:")
        for issue, count in list(processing_summary['validation_issues'].items())[:3]:
            print(f"    • {issue}: {count} records")
    
    # Step 3: Analysis and insights
    print("\n📊 Step 3: Analysis and Insights")
    print("-" * 40)
    
    # Person breakdown
    if processing_summary.get('records_by_person'):
        print("Expenses by person:")
        for person, count in processing_summary['records_by_person'].items():
            print(f"  • {person}: {count} records")
    
    # Expense type breakdown
    if processing_summary.get('records_by_type'):
        print("\nExpenses by type:")
        for exp_type, count in processing_summary['records_by_type'].items():
            print(f"  • {exp_type}: {count} records")
    
    # Date range
    if processing_summary.get('date_range'):
        dr = processing_summary['date_range']
        print(f"\nDate range: {dr['earliest']} to {dr['latest']}")
        print(f"Total span: {dr['total_days']} days")
    
    # Amount statistics
    if processing_summary.get('amount_statistics'):
        stats = processing_summary['amount_statistics']
        print("\nFinancial summary:")
        print(f"  • Total expenses: ${stats['total_amount']:,.2f}")
        print(f"  • Average expense: ${stats['average_amount']:.2f}")
        print(f"  • Largest expense: ${stats['max_amount']:.2f}")
        print(f"  • Records with amounts: {stats['records_with_amounts']}")
    
    # Step 4: Save processed data
    print("\n💾 Step 4: Saving Processed Data")
    print("-" * 40)
    
    # Save to CSV
    output_file = Path("output") / "processed_expenses.csv"
    processed_expense_data.to_csv(output_file, index=False)
    print(f"✓ Saved processed data to: {output_file}")
    
    # Save summary to text file
    summary_file = Path("output") / "expense_summary.txt"
    with open(summary_file, 'w') as f:
        f.write("EXPENSE PROCESSING SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Total records processed: {processing_summary['total_records']}\n")
        f.write(f"Valid records: {processing_summary['valid_records']}\n")
        f.write(f"Invalid records: {processing_summary['invalid_records']}\n\n")
        
        if processing_summary.get('records_by_person'):
            f.write("RECORDS BY PERSON:\n")
            for person, count in processing_summary['records_by_person'].items():
                f.write(f"  {person}: {count}\n")
            f.write("\n")
        
        if processing_summary.get('amount_statistics'):
            stats = processing_summary['amount_statistics']
            f.write("FINANCIAL STATISTICS:\n")
            f.write(f"  Total expenses: ${stats['total_amount']:,.2f}\n")
            f.write(f"  Average expense: ${stats['average_amount']:.2f}\n")
            f.write(f"  Median expense: ${stats['median_amount']:.2f}\n")
            f.write(f"  Largest expense: ${stats['max_amount']:.2f}\n")
            f.write(f"  Smallest expense: ${stats['min_amount']:.2f}\n")
    
    print(f"✓ Saved summary to: {summary_file}")
    
    # Final summary
    print("\n🎯 Summary")
    print("-" * 40)
    print("✅ Data loading: Complete")
    print("✅ Data processing: Complete") 
    print("✅ Data analysis: Complete")
    print("✅ Output generation: Complete")
    print()
    print("📋 Next Steps:")
    print("  1. Review processed data in output/processed_expenses.csv")
    print("  2. Check summary in output/expense_summary.txt")
    print("  3. Implement rent allocation processing")
    print("  4. Build reconciliation engine")
    print("  5. Create comprehensive audit trail")
    
    return {
        'raw_data': raw_expense_data,
        'processed_data': processed_expense_data,
        'summary': processing_summary
    }

if __name__ == "__main__":
    results = main()
