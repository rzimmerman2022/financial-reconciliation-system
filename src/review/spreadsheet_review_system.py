#!/usr/bin/env python3
"""
Spreadsheet-Based Review System for Financial Reconciliation
===========================================================

This system provides a gold standard review experience by:
1. Exporting transactions to a CSV that can be edited in Excel/Google Sheets
2. Allowing bulk review with all the same fields as Phase 4 data
3. Importing the reviewed CSV back into the system

Author: Claude (Anthropic)
Date: July 29, 2025
"""

import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, List, Optional
import hashlib

from manual_review_system import ManualReviewSystem, TransactionCategory, SplitType


class SpreadsheetReviewSystem:
    """Export/import transactions for spreadsheet-based review."""
    
    def __init__(self, review_db_path: str = "data/phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.export_path = Path("output/manual_review_export")
        self.export_path.mkdir(exist_ok=True, parents=True)
        
    def export_for_review(self, transactions_df: pd.DataFrame, 
                         filename: str = "transactions_for_review.csv") -> Path:
        """
        Export transactions in a format optimized for spreadsheet review.
        
        Format matches Phase 4 structure:
        - Name (payer)
        - Date of Purchase
        - Account (source)
        - Merchant
        - Merchant Description
        - Actual Amount
        - Allowed Amount (to be filled)
        - Description (notes)
        - Category
        - Is Personal (Y/N)
        - Split Type (50/50, Rent, Ryan Full, Jordyn Full, Custom)
        - Ryan Share (for custom splits)
        - Jordyn Share (for custom splits)
        """
        
        # Create export DataFrame with Phase 4-like structure
        export_df = pd.DataFrame()
        
        # Map fields from transactions to review format
        export_df['Name'] = transactions_df['payer']
        export_df['Date of Purchase'] = pd.to_datetime(transactions_df['date']).dt.strftime('%m/%d/%Y')
        export_df['Account'] = transactions_df['source']
        export_df['Merchant'] = transactions_df['description']
        export_df['Merchant Description'] = transactions_df.get('merchant_description', '')
        export_df['Actual Amount'] = transactions_df['amount'].apply(
            lambda x: f"${float(x):,.2f}" if pd.notna(x) else "$0.00"
        )
        
        # Fields to be filled during review
        export_df['Allowed Amount'] = export_df['Actual Amount']  # Default to actual
        export_df['Description'] = ''  # For notes
        export_df['Category'] = self._suggest_category(transactions_df)
        export_df['Is Personal'] = 'N'  # Default to shared
        export_df['Split Type'] = '50/50'  # Default split
        export_df['Ryan Share'] = ''  # Only for custom splits
        export_df['Jordyn Share'] = ''  # Only for custom splits
        
        # Add tracking fields (hidden columns)
        export_df['_transaction_id'] = transactions_df.index
        export_df['_review_status'] = 'pending'
        export_df['_original_amount'] = transactions_df['amount']
        
        # Save with instructions
        output_path = self.export_path / filename
        
        # Create instructions sheet
        instructions = pd.DataFrame({
            'Instructions': [
                'GOLD STANDARD MANUAL REVIEW INSTRUCTIONS',
                '========================================',
                '',
                'How to Review Transactions:',
                '1. Allowed Amount: Set to $0 for personal expenses, or adjust as needed',
                '2. Description: Add notes about what this purchase was for',
                '3. Category: Choose from: Rent, Utilities, Groceries, Dining, Transportation, Entertainment, Healthcare, Shopping, Personal_Ryan, Personal_Jordyn, Income_Ryan, Income_Jordyn, Settlement, Other',
                '4. Is Personal: Set to Y if this is a personal expense (not shared)',
                '5. Split Type: Choose from:',
                '   - 50/50: Equal split',
                '   - Rent: 47% Ryan / 53% Jordyn',
                '   - Ryan Full: Ryan pays 100%',
                '   - Jordyn Full: Jordyn pays 100%',
                '   - Custom: Fill in Ryan Share and Jordyn Share columns',
                '',
                'Tips:',
                '- Sort by Merchant to review similar transactions together',
                '- Use Excel formulas to apply patterns (e.g., all "Chase Credit Card Autopay" are personal)',
                '- Leave Allowed Amount as Actual Amount for normal shared expenses',
                '- Set Allowed Amount to $0 for personal expenses or transactions to exclude',
                '',
                'Save as CSV when done and import back into the system.'
            ]
        })
        
        # Write both sheets to Excel if possible, otherwise just CSV
        try:
            with pd.ExcelWriter(output_path.with_suffix('.xlsx'), engine='openpyxl') as writer:
                instructions.to_excel(writer, sheet_name='Instructions', index=False)
                export_df.to_excel(writer, sheet_name='Transactions', index=False)
                
                # Format the Transactions sheet
                workbook = writer.book
                worksheet = writer.sheets['Transactions']
                
                # Set column widths
                column_widths = {
                    'A': 10,  # Name
                    'B': 12,  # Date
                    'C': 20,  # Account
                    'D': 40,  # Merchant
                    'E': 30,  # Merchant Description
                    'F': 12,  # Actual Amount
                    'G': 12,  # Allowed Amount
                    'H': 50,  # Description
                    'I': 15,  # Category
                    'J': 10,  # Is Personal
                    'K': 12,  # Split Type
                    'L': 12,  # Ryan Share
                    'M': 12,  # Jordyn Share
                }
                
                for col, width in column_widths.items():
                    worksheet.column_dimensions[col].width = width
                
            print(f"[DONE] Exported {len(export_df)} transactions to: {output_path.with_suffix('.xlsx')}")
            
        except ImportError:
            # Fallback to CSV if openpyxl not available
            export_df.to_csv(output_path, index=False)
            instructions.to_csv(output_path.with_suffix('.instructions.txt'), index=False)
            print(f"[DONE] Exported {len(export_df)} transactions to: {output_path}")
            
        return output_path
    
    def import_reviewed_transactions(self, filepath: Path) -> Dict:
        """Import reviewed transactions from spreadsheet and apply to system."""
        
        # Read the reviewed file
        if filepath.suffix == '.xlsx':
            reviewed_df = pd.read_excel(filepath, sheet_name='Transactions')
        else:
            reviewed_df = pd.read_csv(filepath)
            
        # Validate required columns
        required_cols = ['Name', 'Date of Purchase', 'Actual Amount', 
                        'Allowed Amount', 'Category', 'Is Personal', 'Split Type']
        missing_cols = [col for col in required_cols if col not in reviewed_df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        # Process each reviewed transaction
        results = {
            'processed': 0,
            'errors': [],
            'review_decisions': []
        }
        
        for idx, row in reviewed_df.iterrows():
            try:
                # Parse amounts
                actual_amount = self._parse_amount(row['Actual Amount'])
                allowed_amount = self._parse_amount(row['Allowed Amount'])
                
                # Determine split amounts
                is_personal = str(row.get('Is Personal', 'N')).upper() == 'Y'
                split_type = row.get('Split Type', '50/50')
                
                if is_personal:
                    # Personal expense - assign to the payer
                    if row['Name'] == 'Ryan':
                        ryan_share = allowed_amount
                        jordyn_share = Decimal('0')
                    else:
                        ryan_share = Decimal('0')
                        jordyn_share = allowed_amount
                elif split_type == 'Custom':
                    ryan_share = self._parse_amount(row.get('Ryan Share', 0))
                    jordyn_share = self._parse_amount(row.get('Jordyn Share', 0))
                else:
                    ryan_share, jordyn_share = self._calculate_split(
                        allowed_amount, split_type
                    )
                
                # Create review decision
                decision = {
                    'date': pd.to_datetime(row['Date of Purchase']),
                    'description': row['Merchant'],
                    'amount': actual_amount,
                    'allowed_amount': allowed_amount,
                    'category': row.get('Category', 'Other'),
                    'split_type': split_type,
                    'ryan_share': float(ryan_share),
                    'jordyn_share': float(jordyn_share),
                    'is_personal': is_personal,
                    'notes': row.get('Description', ''),
                    'payer': row['Name']
                }
                
                results['review_decisions'].append(decision)
                results['processed'] += 1
                
            except Exception as e:
                results['errors'].append({
                    'row': idx + 2,  # +2 for header and 0-indexing
                    'error': str(e),
                    'data': row.to_dict()
                })
                
        # Save review decisions to database
        if results['review_decisions']:
            self._save_to_review_system(results['review_decisions'])
            
        return results
    
    def _suggest_category(self, df: pd.DataFrame) -> pd.Series:
        """Suggest categories based on merchant descriptions."""
        categories = []
        
        for _, row in df.iterrows():
            desc_lower = str(row.get('description', '')).lower()
            
            if any(term in desc_lower for term in ['rent', 'san palmas', 'yardi']):
                categories.append('Rent')
            elif any(term in desc_lower for term in ['srp', 'cox', 'at&t', 'electric']):
                categories.append('Utilities')
            elif any(term in desc_lower for term in ['fry', 'safeway', 'whole foods']):
                categories.append('Groceries')
            elif any(term in desc_lower for term in ['doordash', 'uber eats', 'restaurant']):
                categories.append('Dining')
            elif any(term in desc_lower for term in ['credit card', 'autopay', 'payment']):
                categories.append(f'Personal_{row.get("payer", "Unknown")}')
            elif any(term in desc_lower for term in ['zelle', 'transfer']):
                categories.append('Settlement')
            else:
                categories.append('Other')
                
        return pd.Series(categories)
    
    def _parse_amount(self, amount_str: str) -> Decimal:
        """Parse amount string to Decimal."""
        if pd.isna(amount_str) or amount_str == '':
            return Decimal('0')
            
        # Remove $ and commas
        clean_str = str(amount_str).replace('$', '').replace(',', '').strip()
        
        try:
            return Decimal(clean_str)
        except:
            return Decimal('0')
    
    def _calculate_split(self, amount: Decimal, split_type: str) -> Tuple[Decimal, Decimal]:
        """Calculate split amounts based on split type."""
        if split_type == '50/50':
            half = amount / 2
            return half, half
        elif split_type == 'Rent':
            ryan_share = amount * Decimal('0.47')
            jordyn_share = amount * Decimal('0.53')
            return ryan_share, jordyn_share
        elif split_type == 'Ryan Full':
            return amount, Decimal('0')
        elif split_type == 'Jordyn Full':
            return Decimal('0'), amount
        else:
            # Default to 50/50
            half = amount / 2
            return half, half
    
    def _save_to_review_system(self, decisions: List[Dict]):
        """Save review decisions to the manual review database."""
        for decision in decisions:
            # Create transaction hash for lookup
            tx_hash = hashlib.md5(
                f"{decision['date']}_{decision['description']}_{decision['amount']}".encode()
            ).hexdigest()
            
            # Map to review system format
            self.review_system.add_transaction_for_review(
                tx_hash=tx_hash,
                date=decision['date'],
                description=decision['description'],
                amount=decision['amount'],
                payer=decision['payer'],
                source=f"Manual Review Import",
                original_data=decision
            )
            
            # Apply the review decision
            # Note: This would need to be connected to the actual review_id
            # For now, we're storing the decisions for later application


if __name__ == "__main__":
    # Example usage
    review_system = SpreadsheetReviewSystem()
    
    print("Spreadsheet Review System")
    print("========================")
    print()
    print("1. Export transactions for review")
    print("2. Import reviewed transactions")
    print()
    
    choice = input("Select option (1 or 2): ").strip()
    
    if choice == "1":
        # Load transactions that need review
        from gold_standard_reconciliation import GoldStandardReconciler
        
        reconciler = GoldStandardReconciler()
        # This would load actual transactions needing review
        print("Loading transactions requiring manual review...")
        
        # For demo, create sample data
        sample_transactions = pd.DataFrame({
            'date': pd.date_range('2024-10-01', periods=5),
            'description': ['Fry\'s Food Store', 'Chase Credit Card Autopay', 
                          'San Palmas Rent', 'Doordash', 'Zelle to Ryan'],
            'amount': [125.50, 1500.00, 2800.00, 45.75, 500.00],
            'payer': ['Ryan', 'Jordyn', 'Jordyn', 'Ryan', 'Jordyn'],
            'source': ['Ryan_MonarchMoney', 'Jordyn_Chase', 'Jordyn_Chase', 
                      'Ryan_MonarchMoney', 'Jordyn_Chase']
        })
        
        output_path = review_system.export_for_review(sample_transactions)
        print(f"\nTransactions exported to: {output_path}")
        print("Edit in Excel/Google Sheets and import when complete.")
        
    elif choice == "2":
        filepath = input("Enter path to reviewed CSV/Excel file: ").strip()
        filepath = Path(filepath)
        
        if filepath.exists():
            print(f"\nImporting reviewed transactions from: {filepath}")
            results = review_system.import_reviewed_transactions(filepath)
            
            print(f"\nProcessed: {results['processed']} transactions")
            if results['errors']:
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors'][:5]:  # Show first 5 errors
                    print(f"  Row {error['row']}: {error['error']}")
        else:
            print(f"File not found: {filepath}")