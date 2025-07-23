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
from description_decoder import DescriptionDecoder
from accounting_engine import AccountingEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase5AProcessor:
    """Process Phase 5A transactions with existing business rules."""
    
    def __init__(self):
        self.engine = AccountingEngine()
        self.decoder = DescriptionDecoder()
        self.starting_balance = STARTING_BALANCE
        self.processed_transactions = []
        self.manual_review = []
        
    def initialize_balance(self):
        """Initialize the accounting engine with the starting balance."""
        if self.starting_balance > 0:
            # Jordyn owes Ryan - set up the initial receivable/payable
            # This creates the starting debt position
            self.engine.ryan_receivable = self.starting_balance
            self.engine.jordyn_payable = self.starting_balance
            
            # Add initial balance transaction to audit trail
            initial_transaction = {
                'date': datetime(2024, 9, 30),
                'transaction_type': 'INITIAL_BALANCE',
                'description': 'Starting Balance from Phase 4',
                'ryan_debit': 0.0,
                'ryan_credit': float(self.starting_balance),
                'jordyn_debit': float(self.starting_balance), 
                'jordyn_credit': 0.0,
                'metadata': {'source': 'Phase 4 ending balance'},
                'timestamp': datetime.now()
            }
            # Create a Transaction object and add to engine's transaction list
            from accounting_engine import Transaction, TransactionType
            transaction = Transaction(
                date=datetime(2024, 9, 30),
                transaction_type=TransactionType.SETTLEMENT,
                description="Starting Balance from Phase 4",
                ryan_debit=Decimal('0'),
                ryan_credit=self.starting_balance,
                jordyn_debit=self.starting_balance,
                jordyn_credit=Decimal('0'),
                metadata={'source': 'Phase 4 ending balance'}
            )
            self.engine.transactions.append(transaction)
            
            logger.info(f"Initialized with starting balance: Jordyn owes Ryan ${self.starting_balance}")
    
    def process_rent_payment(self, row):
        """Process rent payments - Jordyn pays full amount, Ryan owes 43%."""
        if row['payer'] == 'Jordyn':
            # Jordyn paid rent - use the accounting engine's rent method
            self.engine.post_rent(
                date=row['date'],
                total_rent=abs(row['amount']),
                ryan_percentage=0.43
            )
            
            ryan_share = abs(row['amount']) * Decimal('0.43')
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
            # Jordyn → Ryan transfer - use accounting engine's settlement method
            self.engine.post_settlement(
                date=row['date'],
                amount=abs(row['amount']),
                from_person="Jordyn",
                to_person="Ryan"
            )
            
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
        result = self.decoder.decode_transaction(row['description'], row['amount'], row['payer'])
        action = result['action']
        
        if action == 'gift':
            # Gift - no split needed
            self.processed_transactions.append({
                'transaction_id': f"GIFT_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'transaction_type': 'gift',
                'pattern': action,
                'source': row['source']
            })
            return
            
        elif action in ['personal_ryan', 'personal_jordyn']:
            # Personal expense - no split
            self.processed_transactions.append({
                'transaction_id': f"PERSONAL_{row.name}",
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': row['amount'],
                'transaction_type': 'personal',
                'pattern': action,
                'source': row['source']
            })
            return
            
        elif action == 'full_reimbursement':
            # Full reimbursement needed - use accounting engine's expense method
            if row['payer'] == 'Ryan':
                # Ryan paid, Jordyn owes full amount
                self.engine.post_expense(
                    date=row['date'],
                    payer="Ryan",
                    ryan_share=Decimal('0'),
                    jordyn_share=abs(row['amount']),
                    description=f"Full Reimbursement: {row['description']}"
                )
            else:  # Jordyn paid
                # Jordyn paid, Ryan owes full amount
                self.engine.post_expense(
                    date=row['date'],
                    payer="Jordyn", 
                    ryan_share=abs(row['amount']),
                    jordyn_share=Decimal('0'),
                    description=f"Full Reimbursement: {row['description']}"
                )
            
        else:
            # Default 50/50 split - use accounting engine's expense method
            half_amount = abs(row['amount']) / Decimal('2')
            
            self.engine.post_expense(
                date=row['date'],
                payer=row['payer'],
                ryan_share=half_amount,
                jordyn_share=half_amount,
                description=f"50/50 Split: {row['description']}"
            )
        
        self.processed_transactions.append({
            'transaction_id': f"{action}_{row.name}",
            'date': row['date'],
            'description': row['description'],
            'payer': row['payer'],
            'amount': row['amount'],
            'transaction_type': 'expense',
            'pattern': action,
            'source': row['source']
        })
    
    def categorize_transaction(self, row):
        """Categorize transaction based on description and amount."""
        desc_lower = row['description'].lower()
        
        # Check for rent - expanded patterns
        rent_keywords = ['rent', 'san palmas', '7755 e thomas', 'apartment', 'rental']
        if any(keyword in desc_lower for keyword in rent_keywords):
            return 'rent'
        
        # Improved Zelle transfer detection
        if 'zelle' in desc_lower:
            # Check if it's between Ryan and Jordyn (not to/from others like mom)
            if ('to ryan' in desc_lower or 'from jordyn' in desc_lower or 
                ('zimmerman' in desc_lower and 'joan' not in desc_lower)):
                return 'zelle'
            # Zelle to others (mom, etc.) is personal
            elif any(word in desc_lower for word in ['to mom', 'from joan', 'joan zimmerman']):
                return 'personal'
        
        # Expanded personal transaction patterns
        personal_keywords = [
            'autopay', 'card payment', 'credit card', 'chase card ending',
            'payment thank you', 'apple card', 'usbank card', 'savings transfer',
            'checking transfer', 'internal transfer', 'automatic payment'
        ]
        if any(keyword in desc_lower for keyword in personal_keywords):
            return 'personal'
        
        # Expanded income patterns  
        income_keywords = [
            'direct deposit', 'payroll', 'salary', 'from joan', 'deposit',
            'brokerage activity', 'cash back', 'refund', 'interest earned'
        ]
        if any(keyword in desc_lower for keyword in income_keywords):
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
            # Skip transactions with missing amounts
            if pd.isna(row['amount']) or row['amount'] is None:
                self.manual_review.append({
                    'index': idx,
                    'date': row['date'],
                    'description': row['description'],
                    'payer': row['payer'],
                    'amount': 'MISSING',
                    'source': row['source'],
                    'reason': 'Missing amount due to encoding error'
                })
                continue
                
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
        # Get final balance and account summary
        balance_status, balance_amount = self.engine.get_current_balance()
        account_summary = self.engine.get_account_summary()
        
        # Create output directory
        output_dir = Path("output/phase5a")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Save transaction log from accounting engine
        transaction_log = self.engine.get_transaction_log()
        ledger_df = pd.DataFrame(transaction_log)
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
            'ending_balance': float(balance_amount),
            'ending_balance_description': balance_status,
            'total_transactions': len(self.processed_transactions),
            'manual_review_count': len(self.manual_review),
            'ryan_receivable': float(account_summary['ryan_receivable']),
            'ryan_payable': float(account_summary['ryan_payable']),
            'jordyn_receivable': float(account_summary['jordyn_receivable']),
            'jordyn_payable': float(account_summary['jordyn_payable'])
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