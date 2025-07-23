"""
Phase 5A Transaction Processor: September 30 - October 18, 2024
==============================================================

This module processes the 18-day reconciliation period using the existing
transaction processing infrastructure from Phase 4.

Starting baseline: Jordyn owes Ryan $1,577.08 (as of September 30, 2024)
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from phase5a_loader import load_phase5a_data, STARTING_BALANCE
from description_decoder import decode_transaction
from accounting_engine import AccountingEngine, AccountingEntry, EntryType, Account

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase5AProcessor:
    """Process Phase 5A transactions with existing business rules."""
    
    def __init__(self):
        self.engine = AccountingEngine()
        self.starting_balance = STARTING_BALANCE
        self.processed_transactions = []
        self.manual_review = []
        
    def initialize_balance(self):
        """Initialize the accounting engine with the starting balance."""
        if self.starting_balance > 0:
            # Jordyn owes Ryan, so debit Jordyn's payable, credit Ryan's receivable
            entry = AccountingEntry(
                date=datetime(2024, 9, 30),
                description="Starting Balance from Phase 4",
                debit_account=Account.JORDYN_PAYABLE,
                credit_account=Account.RYAN_RECEIVABLE,
                amount=self.starting_balance,
                entry_type=EntryType.INITIAL_BALANCE,
                transaction_id="INIT_BALANCE"
            )
            self.engine.post_entry(entry)
            logger.info(f"Initialized with starting balance: Jordyn owes Ryan ${self.starting_balance}")
    
    def process_rent_payment(self, row):
        """Process rent payments - Jordyn pays full amount, Ryan owes 43%."""
        if row['payer'] == 'Jordyn':
            # Jordyn paid rent - Ryan owes his share
            ryan_share = abs(row['amount']) * Decimal('0.43')
            
            entry = AccountingEntry(
                date=row['date'],
                description=f"Rent Payment - Ryan owes 43%",
                debit_account=Account.RYAN_PAYABLE,
                credit_account=Account.JORDYN_RECEIVABLE,
                amount=ryan_share,
                entry_type=EntryType.EXPENSE,
                transaction_id=f"RENT_{row.name}"
            )
            self.engine.post_entry(entry)
            
            self.processed_transactions.append({
                'transaction_id': f"RENT_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'ryan_share': ryan_share,
                'jordyn_share': abs(row['amount']) - ryan_share,
                'transaction_type': 'rent',
                'pattern': 'rent_payment',
                'source': row['source']
            })
    
    def process_zelle_transfer(self, row):
        """Process Zelle transfers between Ryan and Jordyn."""
        # Determine direction from description
        desc_lower = row['description'].lower()
        
        if 'to ryan' in desc_lower or (row['payer'] == 'Jordyn' and 'zelle' in desc_lower):
            # Jordyn → Ryan transfer
            entry = AccountingEntry(
                date=row['date'],
                description=f"Zelle Transfer: Jordyn → Ryan",
                debit_account=Account.RYAN_RECEIVABLE,
                credit_account=Account.JORDYN_PAYABLE,
                amount=abs(row['amount']),
                entry_type=EntryType.PAYMENT,
                transaction_id=f"ZELLE_{row.name}"
            )
            self.engine.post_entry(entry)
            
            self.processed_transactions.append({
                'transaction_id': f"ZELLE_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'transaction_type': 'settlement',
                'pattern': 'zelle_transfer',
                'direction': 'Jordyn → Ryan',
                'source': row['source']
            })
    
    def process_expense(self, row):
        """Process shared expenses using description patterns."""
        # Decode the description
        result = decode_transaction(row['description'], row['amount'], row['payer'])
        pattern = result['pattern']
        
        if pattern == 'gift':
            # Gift - no split needed
            self.processed_transactions.append({
                'transaction_id': f"GIFT_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'transaction_type': 'gift',
                'pattern': pattern,
                'source': row['source']
            })
            return
            
        elif pattern == 'personal':
            # Personal expense - no split
            self.processed_transactions.append({
                'transaction_id': f"PERSONAL_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'transaction_type': 'personal',
                'pattern': pattern,
                'source': row['source']
            })
            return
            
        elif pattern == 'full_reimbursement':
            # Full reimbursement needed
            if row['payer'] == 'Ryan':
                entry = AccountingEntry(
                    date=row['date'],
                    description=f"Full Reimbursement: {row['description']}",
                    debit_account=Account.JORDYN_PAYABLE,
                    credit_account=Account.RYAN_RECEIVABLE,
                    amount=abs(row['amount']),
                    entry_type=EntryType.EXPENSE,
                    transaction_id=f"FULL_{row.name}"
                )
            else:  # Jordyn paid
                entry = AccountingEntry(
                    date=row['date'],
                    description=f"Full Reimbursement: {row['description']}",
                    debit_account=Account.RYAN_PAYABLE,
                    credit_account=Account.JORDYN_RECEIVABLE,
                    amount=abs(row['amount']),
                    entry_type=EntryType.EXPENSE,
                    transaction_id=f"FULL_{row.name}"
                )
            
            self.engine.post_entry(entry)
            
        else:
            # Default 50/50 split
            half_amount = abs(row['amount']) / Decimal('2')
            
            if row['payer'] == 'Ryan':
                entry = AccountingEntry(
                    date=row['date'],
                    description=f"50/50 Split: {row['description']}",
                    debit_account=Account.JORDYN_PAYABLE,
                    credit_account=Account.RYAN_RECEIVABLE,
                    amount=half_amount,
                    entry_type=EntryType.EXPENSE,
                    transaction_id=f"SPLIT_{row.name}"
                )
            else:  # Jordyn paid
                entry = AccountingEntry(
                    date=row['date'],
                    description=f"50/50 Split: {row['description']}",
                    debit_account=Account.RYAN_PAYABLE,
                    credit_account=Account.JORDYN_RECEIVABLE,
                    amount=half_amount,
                    entry_type=EntryType.EXPENSE,
                    transaction_id=f"SPLIT_{row.name}"
                )
            
            self.engine.post_entry(entry)
        
        self.processed_transactions.append({
            'transaction_id': f"{pattern}_{row.name}",
            'date': row['date'],
            'description': row['description'],
            'payer': row['payer'],
            'amount': row['amount'],
            'transaction_type': 'expense',
            'pattern': pattern,
            'source': row['source']
        })
    
    def categorize_transaction(self, row):
        """Categorize transaction based on description and amount."""
        desc_lower = row['description'].lower()
        
        # Check for rent
        if any(keyword in desc_lower for keyword in ['rent', 'san palmas']):
            return 'rent'
        
        # Check for Zelle transfers
        if 'zelle' in desc_lower and ('to ryan' in desc_lower or 'to mom' not in desc_lower):
            return 'zelle'
        
        # Check for credit card payments (not shared)
        if any(keyword in desc_lower for keyword in ['autopay', 'card payment', 'credit card']):
            return 'personal'
        
        # Check for income (not shared)
        if any(keyword in desc_lower for keyword in ['direct deposit', 'payroll', 'from joan']):
            return 'income'
        
        # Default to expense
        return 'expense'
    
    def process_all_transactions(self):
        """Process all Phase 5A transactions."""
        # Load data
        df = load_phase5a_data()
        
        # Initialize starting balance
        self.initialize_balance()
        
        # Process each transaction
        for idx, row in df.iterrows():
            category = self.categorize_transaction(row)
            
            if category == 'rent':
                self.process_rent_payment(row)
            elif category == 'zelle':
                self.process_zelle_transfer(row)
            elif category == 'expense':
                self.process_expense(row)
            elif category == 'personal':
                # Track but don't process
                self.processed_transactions.append({
                    'transaction_id': f"PERSONAL_{idx}",
                    'date': row['date'],
                    'description': row['description'],
                    'payer': row['payer'],
                    'amount': row['amount'],
                    'transaction_type': 'personal',
                    'pattern': 'not_shared',
                    'source': row['source']
                })
            elif category == 'income':
                # Track but don't process
                self.processed_transactions.append({
                    'transaction_id': f"INCOME_{idx}",
                    'date': row['date'],
                    'description': row['description'],
                    'payer': row['payer'],
                    'amount': row['amount'],
                    'transaction_type': 'income',
                    'pattern': 'not_shared',
                    'source': row['source']
                })
            else:
                # Manual review needed
                self.manual_review.append({
                    'index': idx,
                    'date': row['date'],
                    'description': row['description'],
                    'payer': row['payer'],
                    'amount': row['amount'],
                    'source': row['source'],
                    'reason': 'Could not categorize'
                })
    
    def generate_reports(self):
        """Generate Phase 5A reports."""
        # Get final balance
        balance = self.engine.get_balance()
        
        # Create output directory
        output_dir = Path("output/phase5a")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save ledger
        ledger_df = pd.DataFrame([entry.__dict__ for entry in self.engine.ledger])
        ledger_df.to_csv(output_dir / "phase5a_ledger.csv", index=False)
        
        # Save processed transactions
        processed_df = pd.DataFrame(self.processed_transactions)
        processed_df.to_csv(output_dir / "phase5a_processed.csv", index=False)
        
        # Save manual review items
        if self.manual_review:
            review_df = pd.DataFrame(self.manual_review)
            review_df.to_csv(output_dir / "phase5a_manual_review.csv", index=False)
        
        # Generate summary
        summary = {
            'period': 'September 30 - October 18, 2024',
            'starting_balance': float(self.starting_balance),
            'starting_balance_description': 'Jordyn owes Ryan',
            'ending_balance': float(balance['net_balance']),
            'ending_balance_description': 'Jordyn owes Ryan' if balance['net_balance'] > 0 else 'Ryan owes Jordyn',
            'total_transactions': len(self.processed_transactions),
            'manual_review_count': len(self.manual_review),
            'ryan_receivable': float(balance['ryan_receivable']),
            'ryan_payable': float(balance['ryan_payable']),
            'jordyn_receivable': float(balance['jordyn_receivable']),
            'jordyn_payable': float(balance['jordyn_payable'])
        }
        
        # Save summary
        import json
        with open(output_dir / "phase5a_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("PHASE 5A RECONCILIATION SUMMARY")
        print("="*60)
        print(f"Period: {summary['period']}")
        print(f"Starting Balance: ${summary['starting_balance']:.2f} ({summary['starting_balance_description']})")
        print(f"Ending Balance: ${abs(summary['ending_balance']):.2f} ({summary['ending_balance_description']})")
        print(f"Change: ${abs(summary['ending_balance'] - summary['starting_balance']):.2f}")
        print(f"\nTransactions Processed: {summary['total_transactions']}")
        print(f"Manual Review Needed: {summary['manual_review_count']}")
        print("="*60)
        
        return summary


def main():
    """Run Phase 5A reconciliation."""
    processor = Phase5AProcessor()
    processor.process_all_transactions()
    summary = processor.generate_reports()
    
    print("\nPhase 5A reconciliation complete!")
    print(f"Reports saved to: output/phase5a/")
    
    return summary


if __name__ == "__main__":
    main()