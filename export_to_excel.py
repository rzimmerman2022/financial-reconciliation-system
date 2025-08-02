#!/usr/bin/env python3
"""
Export reconciliation data to Excel for review in Excel/Power BI
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sqlite3

def export_data_to_excel():
    """Export all reconciliation data to Excel format."""
    
    output_dir = Path("output/excel_export")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create Excel writer
    excel_file = output_dir / f"reconciliation_data_{timestamp}.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
        
        # 1. Summary from JSON
        try:
            with open("output/gold_standard/summary.json", 'r') as f:
                summary = json.load(f)
            
            # Create summary dataframe
            summary_df = pd.DataFrame([
                ["Final Balance", f"${summary['final_balance']['amount']:,.2f}"],
                ["Who Owes Whom", summary['final_balance']['who_owes_whom']],
                ["Ryan Receivable", f"${summary['final_balance']['ryan_receivable']:,.2f}"],
                ["Jordyn Receivable", f"${summary['final_balance']['jordyn_receivable']:,.2f}"],
                ["", ""],
                ["Transactions Processed", summary['statistics']['transactions_processed']],
                ["Manual Review Required", summary['statistics']['manual_review_required']],
                ["Data Quality Issues", summary['statistics']['data_quality_issues']],
                ["Duplicates Found", summary['statistics']['duplicates_found']],
            ], columns=['Metric', 'Value'])
            
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
        except Exception as e:
            print(f"Warning: Could not load summary.json: {e}")
        
        # 2. Accounting Ledger
        try:
            ledger_df = pd.read_csv("output/gold_standard/accounting_ledger.csv")
            ledger_df.to_excel(writer, sheet_name='Accounting_Ledger', index=False)
        except Exception as e:
            print(f"Warning: Could not load accounting ledger: {e}")
        
        # 3. Manual Review Required
        try:
            manual_df = pd.read_csv("output/gold_standard/manual_review_required.csv")
            
            # Add columns for review decisions
            if 'allowed_amount' not in manual_df.columns:
                manual_df['allowed_amount'] = manual_df['amount']
            if 'notes' not in manual_df.columns:
                manual_df['notes'] = ''
            if 'category' not in manual_df.columns:
                manual_df['category'] = ''
            if 'decision' not in manual_df.columns:
                manual_df['decision'] = 'PENDING'
            
            manual_df.to_excel(writer, sheet_name='Manual_Review', index=False)
        except Exception as e:
            print(f"Warning: Could not load manual review data: {e}")
        
        # 4. Data Quality Issues
        try:
            quality_df = pd.read_csv("output/gold_standard/data_quality_issues.csv")
            quality_df.to_excel(writer, sheet_name='Data_Quality_Issues', index=False)
        except Exception as e:
            print(f"Warning: Could not load data quality issues: {e}")
        
        # 5. Review Database (if exists)
        try:
            db_path = "data/phase5_manual_reviews.db"
            if Path(db_path).exists():
                conn = sqlite3.connect(db_path)
                
                # Get reviews table
                reviews_df = pd.read_sql_query("SELECT * FROM reviews", conn)
                if not reviews_df.empty:
                    reviews_df.to_excel(writer, sheet_name='Review_Decisions', index=False)
                
                # Get transactions table
                transactions_df = pd.read_sql_query("SELECT * FROM transactions", conn)
                if not transactions_df.empty:
                    transactions_df.to_excel(writer, sheet_name='All_Transactions', index=False)
                
                conn.close()
        except Exception as e:
            print(f"Warning: Could not load review database: {e}")
    
    print(f"✅ Excel export complete: {excel_file}")
    print(f"📊 Sheets created:")
    print("   - Summary: Key metrics and final balance")
    print("   - Accounting_Ledger: Full transaction ledger")
    print("   - Manual_Review: Transactions needing review (EDITABLE)")
    print("   - Data_Quality_Issues: Data problems found")
    print("   - Review_Decisions: Manual review decisions made")
    print("   - All_Transactions: Complete transaction database")
    print()
    print("💡 You can now:")
    print("   1. Open in Excel and edit the Manual_Review sheet")
    print("   2. Import into Power BI for advanced analytics")
    print("   3. Use Excel formulas and pivot tables for analysis")
    
    return excel_file

if __name__ == "__main__":
    export_data_to_excel()