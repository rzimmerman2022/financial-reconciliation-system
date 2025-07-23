"""
Phase 5A Runner - Simple reconciliation for Sept 30 - Oct 18, 2024
==================================================================

This module runs Phase 5A reconciliation using the existing transaction processor
with a modified data loader for the 18-day period.

Starting baseline: Jordyn owes Ryan $1,577.08 (as of September 30, 2024)
"""

import os
import sys
import json
import pandas as pd
from decimal import Decimal
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import existing modules
from transaction_processor import TransactionProcessor
from phase5a_loader import load_phase5a_data, STARTING_BALANCE


class Phase5AProcessor(TransactionProcessor):
    """Extended processor for Phase 5A with baseline support."""
    
    def __init__(self, output_dir: str = "output/phase5a"):
        super().__init__(output_dir)
        self.starting_balance = STARTING_BALANCE
        
    def initialize_with_baseline(self):
        """Initialize the accounting engine with starting balance."""
        if self.starting_balance > 0:
            # Post initial balance as a special transaction
            print(f"\nInitializing with baseline: Jordyn owes Ryan ${self.starting_balance}")
            
            # Create a pseudo-transaction for the starting balance
            # Since Jordyn owes Ryan, we treat it as if Ryan paid an expense
            # and Jordyn owes the full amount
            self.engine.post_expense(
                date=datetime(2024, 9, 30),
                payer="Ryan",
                ryan_share=Decimal('0'),
                jordyn_share=self.starting_balance,
                description="Starting Balance from Phase 4 (Jan-Sept 2024)",
                metadata={
                    'pattern': 'initial_balance',
                    'source_file': 'Phase 4 Reconciliation'
                }
            )
    
    def load_phase5a_data_as_transactions(self) -> list:
        """Convert Phase 5A data to transaction format expected by processor."""
        # Load Phase 5A data
        df = load_phase5a_data()
        
        transactions = []
        
        for idx, row in df.iterrows():
            # Skip rows with no amount
            if pd.isna(row['amount']) or row['amount'] is None:
                continue
                
            desc_lower = row['description'].lower()
            
            # Determine transaction type
            if any(keyword in desc_lower for keyword in ['rent', 'san palmas']):
                tx_type = 'RENT'
            elif 'zelle' in desc_lower and 'to ryan' in desc_lower:
                tx_type = 'ZELLE'
            elif any(keyword in desc_lower for keyword in ['autopay', 'card payment', 'direct deposit']):
                continue  # Skip non-shared transactions
            else:
                tx_type = 'EXPENSE'
            
            # Create transaction dict
            transaction = {
                'date': row['date'].strftime('%Y-%m-%d'),  # Convert to string
                'type': tx_type,
                'payer': row['payer'],
                'description': row['description'],
                'amount': float(row['amount']),  # Convert to float
                'category': row.get('category', 'Uncategorized'),
                'source_file': row['source']
            }
            
            # Add type-specific fields
            if tx_type == 'EXPENSE':
                transaction['actual_amount'] = float(row['amount'])
                transaction['merchant_description'] = row['description']
            elif tx_type == 'RENT':
                transaction['ryan_percentage'] = 0.43
                transaction['month'] = row['date'].strftime('%Y-%m')
            
            transactions.append(transaction)
        
        return transactions
    
    def load_all_data(self) -> list:
        """Override to load Phase 5A data instead."""
        print("\n" + "="*60)
        print("LOADING PHASE 5A DATA")
        print("="*60)
        
        transactions = self.load_phase5a_data_as_transactions()
        
        # Sort by date
        transactions.sort(key=lambda x: x['date'])
        
        print(f"\nLoaded {len(transactions)} transactions for Phase 5A")
        print(f"Date range: Sept 30 - Oct 18, 2024")
        
        # Debug: Show sample transactions
        if transactions:
            print(f"\nSample transactions:")
            for i, tx in enumerate(transactions[:3]):
                print(f"  {i+1}. {tx['date']} - {tx['type']} - {tx['payer']} - ${abs(tx['amount']):.2f} - {tx['description'][:50]}")
        
        return transactions
    
    def generate_phase5a_summary(self):
        """Generate Phase 5A specific summary."""
        # Get final balance
        status, amount = self.engine.get_current_balance()
        
        summary = {
            'phase': '5A',
            'period': 'September 30 - October 18, 2024',
            'starting_balance': float(self.starting_balance),
            'starting_balance_status': 'Jordyn owes Ryan',
            'ending_balance': float(amount),
            'ending_balance_status': status,
            'balance_change': float(amount - self.starting_balance),
            'days_covered': 18,
            'transactions_processed': self.stats['total_transactions'],
            'expenses': self.stats['expenses_processed'],
            'rent_payments': self.stats['rent_processed'],
            'zelle_transfers': self.stats['zelle_processed'],
            'manual_review': self.stats['manual_review_count']
        }
        
        # Save summary
        summary_path = os.path.join(self.output_dir, 'phase5a_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("PHASE 5A RECONCILIATION SUMMARY")
        print("="*60)
        print(f"Period: {summary['period']} ({summary['days_covered']} days)")
        print(f"\nStarting Balance: ${summary['starting_balance']:.2f} ({summary['starting_balance_status']})")
        print(f"Ending Balance: ${summary['ending_balance']:.2f} ({summary['ending_balance_status']})")
        print(f"Change: ${abs(summary['balance_change']):.2f}")
        print(f"\nTransactions Processed: {summary['transactions_processed']}")
        print(f"  - Expenses: {summary['expenses']}")
        print(f"  - Rent: {summary['rent_payments']}")
        print(f"  - Zelle: {summary['zelle_transfers']}")
        print(f"  - Manual Review: {summary['manual_review']}")
        print("="*60)
        
        return summary
    
    def run(self):
        """Run the complete Phase 5A reconciliation process."""
        print("\n" + "="*80)
        print("PHASE 5A FINANCIAL RECONCILIATION")
        print("September 30 - October 18, 2024")
        print("="*80)
        
        # Initialize with baseline
        self.initialize_with_baseline()
        
        # Load and process transactions
        transactions = self.load_all_data()
        self.process_all_transactions(transactions, start_date="2024-09-30", cutoff_date="2024-10-18")
        
        # Generate all outputs
        self.generate_outputs()
        
        # Generate Phase 5A specific summary
        summary = self.generate_phase5a_summary()
        
        print(f"\n✓ Phase 5A reconciliation complete!")
        print(f"✓ All outputs saved to: {self.output_dir}/")
        
        return summary


def main():
    """Run Phase 5A reconciliation."""
    processor = Phase5AProcessor()
    summary = processor.run()
    return summary


if __name__ == "__main__":
    main()