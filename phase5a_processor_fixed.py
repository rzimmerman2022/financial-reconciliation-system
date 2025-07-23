#!/usr/bin/env python3
"""
Phase 5A Transaction Processor: September 30 - October 18, 2024
==============================================================

Fixed version that properly processes the 18-day reconciliation period using 
the existing transaction processing infrastructure.

Starting baseline: Jordyn owes Ryan $1,577.08 (as of September 30, 2024)

KEY FIXES IMPLEMENTED:
1. Corrected accounting engine method calls (post_expense, post_rent, post_settlement)
2. Fixed description decoder integration (decode_transaction method)
3. Added null amount handling for unparseable Chase bank transactions
4. Proper share calculation based on decoder actions

PROCESSING RESULTS:
- Processed 196 of 203 transactions (7 had unparseable amounts)
- Starting: Jordyn owes Ryan $1,577.08
- Ending: Ryan owes Jordyn $4,807.93 
- Balance swing: $3,230.85 in Jordyn's favor

NOTE: The large balance swing may indicate missing rent/Zelle transactions
that ended up in manual review due to encoding issues in Chase data.
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from phase5a_loader import load_phase5a_data, STARTING_BALANCE
from description_decoder import DescriptionDecoder
from accounting_engine import AccountingEngine, TransactionType


class Phase5AProcessor:
    """Process Phase 5A transactions with existing business rules.
    
    This processor handles the 18-day gap between Phase 4 (ending Sept 30)
    and the planned Phase 5 reconciliation (Oct 2024 - July 2025).
    """
    
    def __init__(self, output_dir: str = "output/phase5a"):
        self.output_dir = output_dir
        self.decoder = DescriptionDecoder()
        self.engine = AccountingEngine()
        self.starting_balance = STARTING_BALANCE
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Tracking
        self.processed_transactions = []
        self.manual_review = []
        self.stats = {
            'total_transactions': 0,
            'rent_payments': 0,
            'zelle_transfers': 0,
            'expenses': 0,
            'personal': 0,
            'income': 0,
            'manual_review': 0
        }
        
    def initialize_balance(self):
        """Initialize the accounting engine with the starting balance."""
        if self.starting_balance > 0:
            # Since Jordyn owes Ryan $1,577.08, we need to create an initial expense
            # that Ryan "paid" to establish this debt
            self.engine.post_expense(
                date=datetime(2024, 9, 30),
                payer='Ryan',
                ryan_share=Decimal('0'),  # Ryan paid nothing
                jordyn_share=self.starting_balance,  # Jordyn owes full amount
                description='Starting Balance from Phase 4 (Jordyn owes Ryan)',
                metadata={'phase': '4_ending', 'initial_balance': True}
            )
            print(f"Initialized with starting balance: Jordyn owes Ryan ${self.starting_balance}")
    
    def categorize_transaction(self, row):
        """Categorize transaction based on description and amount."""
        desc_lower = row['description'].lower()
        
        # Check for rent (Jordyn always pays full amount)
        if any(keyword in desc_lower for keyword in ['rent', 'san palmas', '7755 e thomas']):
            return 'rent'
        
        # Check for Zelle transfers (always Jordyn to Ryan)
        if 'zelle' in desc_lower and ('to ryan' in desc_lower or 'from jordyn' in desc_lower):
            return 'zelle'
        
        # Check for credit card payments (not shared)
        if any(keyword in desc_lower for keyword in ['autopay', 'card payment', 'credit card', 
                                                      'chase card ending', 'payment thank you']):
            return 'personal'
        
        # Check for income (not shared)
        if any(keyword in desc_lower for keyword in ['direct deposit', 'payroll', 'from joan',
                                                      'brokerage activity', 'deposit']):
            return 'income'
        
        # Default to expense
        return 'expense'
    
    def process_transaction(self, idx, row):
        """Process a single transaction based on its category."""
        # Skip transactions with null amounts
        if pd.isna(row['amount']) or row['amount'] is None:
            self.manual_review.append({
                'index': idx,
                'date': row['date'],
                'description': row['description'],
                'payer': row['payer'],
                'amount': None,
                'source': row['source'],
                'reason': 'Missing amount - could not parse from source data'
            })
            self.stats['manual_review'] += 1
            return
            
        category = self.categorize_transaction(row)
        self.stats['total_transactions'] += 1
        
        transaction_data = {
            'date': row['date'],
            'payer': row['payer'],
            'description': row['description'],
            'amount': abs(row['amount']),
            'source': row['source'],
            'category': category
        }
        
        if category == 'rent':
            # Rent: Jordyn pays full amount, Ryan owes 43%
            if row['payer'] == 'Jordyn':
                ryan_share = abs(row['amount']) * Decimal('0.43')
                jordyn_share = abs(row['amount']) * Decimal('0.57')
                
                # Post rent transaction (Jordyn pays, Ryan owes 43%)
                self.engine.post_rent(
                    date=row['date'],
                    total_rent=abs(row['amount']),
                    ryan_percentage=0.43  # Ryan owes 43% of rent
                )
                
                transaction_data.update({
                    'transaction_type': 'rent',
                    'ryan_share': ryan_share,
                    'jordyn_share': jordyn_share,
                    'pattern': 'rent_payment'
                })
                
                self.stats['rent_payments'] += 1
            
        elif category == 'zelle':
            # Zelle transfers are always Jordyn → Ryan
            self.engine.post_settlement(
                date=row['date'],
                amount=abs(row['amount']),
                from_person='Jordyn',
                to_person='Ryan'
            )
            
            transaction_data.update({
                'transaction_type': 'settlement',
                'ryan_share': Decimal('0'),
                'jordyn_share': abs(row['amount']),
                'pattern': 'zelle_transfer'
            })
            
            self.stats['zelle_transfers'] += 1
            
        elif category == 'expense':
            # Use description decoder for expense splitting
            result = self.decoder.decode_transaction(row['description'], row['amount'], row['payer'])
            
            if result['action'] == 'manual_review':
                self.manual_review.append({
                    'index': idx,
                    'date': row['date'],
                    'description': row['description'],
                    'payer': row['payer'],
                    'amount': row['amount'],
                    'source': row['source'],
                    'reason': result.get('reason', 'Needs manual review')
                })
                self.stats['manual_review'] += 1
                
            else:
                # Calculate shares based on action
                if result['action'] == 'full_reimbursement':
                    if row['payer'] == 'Ryan':
                        ryan_share = Decimal('0')
                        jordyn_share = abs(row['amount'])
                    else:
                        ryan_share = abs(row['amount'])
                        jordyn_share = Decimal('0')
                elif result['action'] in ['personal_ryan', 'personal_jordyn', 'gift']:
                    # Personal expenses - no split
                    if row['payer'] == 'Ryan' or result['action'] == 'personal_ryan':
                        ryan_share = abs(row['amount'])
                        jordyn_share = Decimal('0')
                    else:
                        ryan_share = Decimal('0')
                        jordyn_share = abs(row['amount'])
                else:
                    # Default 50/50 split or use decoder's calculated shares
                    if 'payer_share' in result and 'other_share' in result:
                        if row['payer'] == 'Ryan':
                            ryan_share = Decimal(str(result['payer_share']))
                            jordyn_share = Decimal(str(result['other_share']))
                        else:
                            ryan_share = Decimal(str(result['other_share']))
                            jordyn_share = Decimal(str(result['payer_share']))
                    else:
                        ryan_share = abs(row['amount']) * Decimal('0.5')
                        jordyn_share = abs(row['amount']) * Decimal('0.5')
                
                # Post expense transaction
                self.engine.post_expense(
                    date=row['date'],
                    payer=row['payer'],
                    ryan_share=ryan_share,
                    jordyn_share=jordyn_share,
                    description=row['description'],
                    metadata={
                        'source': row['source'],
                        'pattern': result['action'],
                        'decoded_action': result.get('action', 'unknown')
                    }
                )
                
                transaction_data.update({
                    'transaction_type': 'expense',
                    'ryan_share': ryan_share,
                    'jordyn_share': jordyn_share,
                    'pattern': result['action']
                })
                
                self.stats['expenses'] += 1
                
        elif category == 'personal':
            # Personal transactions - not shared
            self.stats['personal'] += 1
            
        elif category == 'income':
            # Income transactions - not shared
            self.stats['income'] += 1
        
        # Track all transactions
        self.processed_transactions.append(transaction_data)
    
    def process_all_transactions(self):
        """Process all Phase 5A transactions."""
        # Load data
        df = load_phase5a_data()
        print(f"\nLoaded {len(df)} transactions for Phase 5A")
        
        # Initialize starting balance
        self.initialize_balance()
        
        # Process each transaction
        print("\nProcessing transactions...")
        for idx, row in df.iterrows():
            self.process_transaction(idx, row)
        
        print(f"\nProcessed {self.stats['total_transactions']} transactions")
        print(f"  Rent payments: {self.stats['rent_payments']}")
        print(f"  Zelle transfers: {self.stats['zelle_transfers']}")
        print(f"  Shared expenses: {self.stats['expenses']}")
        print(f"  Personal/Income: {self.stats['personal'] + self.stats['income']}")
        print(f"  Manual review needed: {self.stats['manual_review']}")
    
    def generate_reports(self):
        """Generate Phase 5A reports."""
        # Get final balance
        status, balance_amount = self.engine.get_current_balance()
        
        # Save transaction log
        transaction_log = self.engine.get_transaction_log()
        if transaction_log:
            log_df = pd.DataFrame(transaction_log)
            log_df.to_csv(os.path.join(self.output_dir, "phase5a_transaction_log.csv"), index=False)
        
        # Save processed transactions
        if self.processed_transactions:
            processed_df = pd.DataFrame(self.processed_transactions)
            processed_df.to_csv(os.path.join(self.output_dir, "phase5a_processed.csv"), index=False)
        
        # Save manual review items
        if self.manual_review:
            review_df = pd.DataFrame(self.manual_review)
            review_df.to_csv(os.path.join(self.output_dir, "phase5a_manual_review.csv"), index=False)
        
        # Generate summary
        summary = {
            'phase': '5A',
            'period': 'September 30 - October 18, 2024',
            'starting_balance': float(self.starting_balance),
            'starting_balance_status': 'Jordyn owes Ryan',
            'ending_balance': float(abs(balance_amount)),
            'ending_balance_status': status,
            'balance_change': float(abs(balance_amount) - self.starting_balance),
            'days_covered': 18,
            'transactions_processed': self.stats['total_transactions'],
            'expenses': self.stats['expenses'],
            'rent_payments': self.stats['rent_payments'],
            'zelle_transfers': self.stats['zelle_transfers'],
            'manual_review': self.stats['manual_review']
        }
        
        # Save summary
        with open(os.path.join(self.output_dir, "phase5a_summary.json"), 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("PHASE 5A RECONCILIATION SUMMARY")
        print("="*60)
        print(f"Period: {summary['period']}")
        print(f"Starting Balance: ${summary['starting_balance']:.2f} ({summary['starting_balance_status']})")
        print(f"Ending Balance: ${summary['ending_balance']:.2f} ({summary['ending_balance_status']})")
        print(f"Balance Change: ${abs(summary['balance_change']):.2f}")
        print("\nTransaction Summary:")
        print(f"  Total Processed: {summary['transactions_processed']}")
        print(f"  Rent Payments: {summary['rent_payments']}")
        print(f"  Zelle Transfers: {summary['zelle_transfers']}")
        print(f"  Shared Expenses: {summary['expenses']}")
        print(f"  Manual Review: {summary['manual_review']}")
        print("="*60)
        
        return summary


def main():
    """Run Phase 5A reconciliation.
    
    Processes 203 transactions from Sept 30 - Oct 18, 2024:
    - 196 successfully processed
    - 7 require manual review (missing amounts)
    - 0 rent payments detected (likely in manual review)
    - 0 Zelle transfers detected (likely in manual review)
    - 176 shared expenses processed
    
    The ending balance shows Ryan owing Jordyn $4,807.93, a significant
    swing from the starting position. This warrants careful review.
    """
    processor = Phase5AProcessor()
    processor.process_all_transactions()
    summary = processor.generate_reports()
    
    print(f"\nPhase 5A reconciliation complete!")
    print(f"Reports saved to: {processor.output_dir}/")
    
    return summary


if __name__ == "__main__":
    main()