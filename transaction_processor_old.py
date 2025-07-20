#!/usr/bin/env python3
"""
Transaction Processor - Phase 4
Final component that orchestrates all modules to determine who owes whom.
"""

import os
import sys
import json
import csv
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional

# Import our modules
from data_loader import load_expense_history, load_rent_allocation, load_zelle_payments
from description_decoder import DescriptionDecoder
from accounting_engine import AccountingEngine, Transaction


class TransactionProcessor:
    """Orchestrates the complete reconciliation process."""
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the processor with all required components."""
        self.output_dir = output_dir
        self.decoder = DescriptionDecoder()
        self.engine = AccountingEngine()
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Tracking
        self.all_transactions = []
        self.manual_review_items = []
        self.processing_errors = []
        self.stats = {
            'total_transactions': 0,
            'expenses_processed': 0,
            'rent_processed': 0,
            'zelle_processed': 0,
            'manual_review_count': 0,
            'errors_count': 0,
            'total_expense_amount': 0.0,
            'total_rent_amount': 0.0,
            'total_zelle_amount': 0.0
        }
    
    def load_all_data(self) -> List[Dict[str, Any]]:
        """Load and combine all transaction data."""
        print("Loading transaction data...")
        
        # Load expenses
        print("  - Loading expenses...")
        expenses_df = load_expense_history('data/raw/Consolidated_Expense_History_20250622.csv')
        expenses = expenses_df.to_dict('records')
        self.stats['expenses_processed'] = len(expenses)
        print(f"    Loaded {len(expenses)} expense transactions")
        
        # Load rent
        print("  - Loading rent allocations...")
        rent_df = load_rent_allocation('data/raw/Consolidated_Rent_Allocation_20250527.csv')
        rent = rent_df.to_dict('records')
        self.stats['rent_processed'] = len(rent)
        print(f"    Loaded {len(rent)} rent transactions")
        
        # Load Zelle settlements
        print("  - Loading Zelle settlements...")
        zelle_df = load_zelle_payments('data/raw/Zelle_From_Jordyn_Final.csv')
        zelle = zelle_df.to_dict('records')
        self.stats['zelle_processed'] = len(zelle)
        print(f"    Loaded {len(zelle)} Zelle transactions")
        
        # Combine all transactions
        all_transactions = []
        
        # Add expenses with type marker
        for expense in expenses:
            expense['transaction_type'] = 'expense'
            # Map fields to common structure
            expense['date'] = expense.get('date_of_purchase')
            amount = expense.get('actual_amount')
            expense['amount'] = float(amount) if amount is not None else 0.0
            expense['person'] = expense.get('name', '')
            all_transactions.append(expense)
            self.stats['total_expense_amount'] += expense['amount']
        
        # Add rent with type marker
        for rent_tx in rent:
            rent_tx['transaction_type'] = 'rent'
            # Map fields to common structure
            rent_tx['date'] = rent_tx.get('month')
            ryan_amt = rent_tx.get('ryan\'s_rent_(43%)', 0)
            jordyn_amt = rent_tx.get('jordyn\'s_rent_(57%)', 0)
            total_amt = rent_tx.get('gross_total', 0)
            rent_tx['ryan_amount'] = float(ryan_amt) if ryan_amt is not None else 0.0
            rent_tx['jordyn_amount'] = float(jordyn_amt) if jordyn_amt is not None else 0.0
            rent_tx['total_amount'] = float(total_amt) if total_amt is not None else 0.0
            # CRITICAL: Jordyn ALWAYS pays the full rent upfront
            rent_tx['paid_by'] = 'Jordyn'
            all_transactions.append(rent_tx)
            self.stats['total_rent_amount'] += rent_tx['ryan_amount'] + rent_tx['jordyn_amount']
        
        # Add Zelle with type marker
        for zelle_tx in zelle:
            zelle_tx['transaction_type'] = 'zelle'
            # Ensure amount is float
            amt = zelle_tx.get('amount', 0)
            zelle_tx['amount'] = float(amt) if amt is not None else 0.0
            zelle_tx['description'] = zelle_tx.get('notes', zelle_tx.get('original_statement', ''))
            all_transactions.append(zelle_tx)
            self.stats['total_zelle_amount'] += zelle_tx['amount']
        
        # Sort by date
        all_transactions.sort(key=lambda x: x.get('date', datetime.min))
        
        self.stats['total_transactions'] = len(all_transactions)
        print(f"\nTotal transactions to process: {len(all_transactions)}")
        
        return all_transactions
    
    def process_expense(self, expense: Dict[str, Any]) -> Optional[Transaction]:
        """Process an expense transaction."""
        try:
            # Decode the description
            decoded = self.decoder.decode(expense['description'])
            
            # Store decoded info in expense for output
            expense['decoded_action'] = decoded['action']
            expense['decoded_confidence'] = decoded['confidence']
            expense['decoded_details'] = decoded.get('details', '')
            
            # Handle based on action
            action = decoded['action']
            payer = expense['person']
            amount = expense['amount']
            
            if action == 'manual_review':
                self.manual_review_items.append({
                    **expense,
                    'reason': decoded.get('details', 'Requires manual review')
                })
                self.stats['manual_review_count'] += 1
                return None
            
            # Determine who owes what based on action
            if action == 'split_50_50':
                # Split evenly
                ryan_owes = amount / 2
                jordyn_owes = amount / 2
            elif action == 'full_reimbursement':
                # Non-payer owes full amount
                if payer == 'Ryan':
                    ryan_owes = 0
                    jordyn_owes = amount
                else:
                    ryan_owes = amount
                    jordyn_owes = 0
            elif action == 'gift':
                # No one owes anything
                ryan_owes = 0
                jordyn_owes = 0
            elif action == 'personal_ryan':
                # Ryan's personal expense
                ryan_owes = amount if payer != 'Ryan' else 0
                jordyn_owes = 0
            elif action == 'personal_jordyn':
                # Jordyn's personal expense
                ryan_owes = 0
                jordyn_owes = amount if payer != 'Jordyn' else 0
            else:
                # Default to 50/50 split
                ryan_owes = amount / 2
                jordyn_owes = amount / 2
            
            # Create transaction
            tx = Transaction(
                date=expense['date'],
                description=f"{expense['description']} [{action}]",
                ryan_owes=ryan_owes,
                jordyn_owes=jordyn_owes,
                paid_by=payer,
                amount=amount,
                category=expense.get('category', 'Expense'),
                metadata={
                    'original_description': expense['description'],
                    'decoded_action': action,
                    'confidence': decoded['confidence'],
                    'transaction_type': 'expense'
                }
            )
            
            return tx
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': expense,
                'error': str(e),
                'type': 'expense_processing'
            })
            self.stats['errors_count'] += 1
            return None
    
    def process_rent(self, rent: Dict[str, Any]) -> Optional[Transaction]:
        """Process a rent transaction.
        
        CRITICAL: Jordyn ALWAYS pays the full rent upfront.
        Ryan owes his portion (43% or 47% as specified in CSV).
        """
        try:
            # Jordyn pays full rent, Ryan owes his portion
            tx = Transaction(
                date=rent['date'],
                description=f"Rent - {rent['date'].strftime('%Y-%m') if hasattr(rent['date'], 'strftime') else rent['date']}",
                ryan_owes=rent['ryan_amount'],  # Ryan owes his portion
                jordyn_owes=0,  # Jordyn owes nothing (she paid)
                paid_by='Jordyn',  # ALWAYS Jordyn
                amount=rent['total_amount'],
                category='Rent',
                metadata={
                    'month': rent['date'].strftime('%Y-%m') if hasattr(rent['date'], 'strftime') else str(rent['date']),
                    'transaction_type': 'rent',
                    'note': 'Jordyn pays full rent, Ryan owes his portion'
                }
            )
            return tx
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': rent,
                'error': str(e),
                'type': 'rent_processing'
            })
            self.stats['errors_count'] += 1
            return None
    
    def process_zelle(self, zelle: Dict[str, Any]) -> Optional[Transaction]:
        """Process a Zelle settlement."""
        try:
            # Zelle is always from Jordyn to Ryan
            tx = Transaction(
                date=zelle['date'],
                description=f"Zelle Settlement - {zelle.get('description', '')}",
                ryan_owes=0,
                jordyn_owes=0,
                paid_by='Jordyn',
                amount=zelle['amount'],
                category='Settlement',
                metadata={
                    'transaction_type': 'zelle',
                    'is_settlement': True,
                    'settlement_from': 'Jordyn',
                    'settlement_to': 'Ryan',
                    'settlement_amount': zelle['amount']
                }
            )
            return tx
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': zelle,
                'error': str(e),
                'type': 'zelle_processing'
            })
            self.stats['errors_count'] += 1
            return None
    
    def process_all_transactions(self, transactions: List[Dict[str, Any]]) -> None:
        """Process all transactions through the accounting engine."""
        print("\nProcessing transactions...")
        
        total = len(transactions)
        for i, tx_data in enumerate(transactions):
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{total} transactions...")
            
            # Process based on type
            tx_type = tx_data.get('transaction_type')
            transaction = None
            
            if tx_type == 'expense':
                transaction = self.process_expense(tx_data)
            elif tx_type == 'rent':
                transaction = self.process_rent(tx_data)
            elif tx_type == 'zelle':
                transaction = self.process_zelle(tx_data)
            
            # Post to accounting engine if we have a valid transaction
            if transaction:
                try:
                    self.engine.post_transaction(transaction)
                    # Store for output
                    self.all_transactions.append({
                        'date': transaction.date.strftime('%Y-%m-%d'),
                        'description': transaction.description,
                        'paid_by': transaction.paid_by,
                        'amount': transaction.amount,
                        'ryan_owes': transaction.ryan_owes,
                        'jordyn_owes': transaction.jordyn_owes,
                        'ryan_balance': self.engine.ryan_account.get_balance(),
                        'jordyn_balance': self.engine.jordyn_account.get_balance(),
                        'category': transaction.category,
                        'metadata': transaction.metadata
                    })
                except Exception as e:
                    self.processing_errors.append({
                        'transaction': tx_data,
                        'error': str(e),
                        'type': 'posting_error'
                    })
                    self.stats['errors_count'] += 1
        
        print(f"\nProcessing complete. Total transactions posted: {len(self.all_transactions)}")
    
    def generate_outputs(self) -> None:
        """Generate all output files."""
        print("\nGenerating output files...")
        
        # 1. Reconciliation ledger
        ledger_path = os.path.join(self.output_dir, 'reconciliation_ledger.csv')
        with open(ledger_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'description', 'paid_by', 'amount', 
                'ryan_owes', 'jordyn_owes', 'ryan_balance', 'jordyn_balance',
                'category', 'transaction_type', 'decoded_action'
            ])
            writer.writeheader()
            
            for tx in self.all_transactions:
                row = {
                    'date': tx['date'],
                    'description': tx['description'],
                    'paid_by': tx['paid_by'],
                    'amount': f"{tx['amount']:.2f}",
                    'ryan_owes': f"{tx['ryan_owes']:.2f}",
                    'jordyn_owes': f"{tx['jordyn_owes']:.2f}",
                    'ryan_balance': f"{tx['ryan_balance']:.2f}",
                    'jordyn_balance': f"{tx['jordyn_balance']:.2f}",
                    'category': tx['category'],
                    'transaction_type': tx['metadata'].get('transaction_type', ''),
                    'decoded_action': tx['metadata'].get('decoded_action', '')
                }
                writer.writerow(row)
        print(f"  - Created: {ledger_path}")
        
        # 2. Manual review items
        if self.manual_review_items:
            review_path = os.path.join(self.output_dir, 'manual_review.csv')
            with open(review_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'date', 'description', 'person', 'amount', 'category', 'reason'
                ])
                writer.writeheader()
                
                for item in self.manual_review_items:
                    writer.writerow({
                        'date': item['date'].strftime('%Y-%m-%d'),
                        'description': item['description'],
                        'person': item['person'],
                        'amount': f"{item['amount']:.2f}",
                        'category': item.get('category', ''),
                        'reason': item['reason']
                    })
            print(f"  - Created: {review_path}")
        
        # 3. Summary JSON
        ryan_balance = self.engine.ryan_account.get_balance()
        jordyn_balance = self.engine.jordyn_account.get_balance()
        
        # Determine who owes whom
        if ryan_balance > 0:
            final_result = f"Jordyn owes Ryan ${ryan_balance:.2f}"
            who_owes = "Jordyn"
            amount_owed = ryan_balance
        else:
            final_result = f"Ryan owes Jordyn ${abs(ryan_balance):.2f}"
            who_owes = "Ryan"
            amount_owed = abs(ryan_balance)
        
        summary = {
            'final_result': final_result,
            'who_owes': who_owes,
            'amount_owed': round(amount_owed, 2),
            'ryan_balance': round(ryan_balance, 2),
            'jordyn_balance': round(jordyn_balance, 2),
            'statistics': self.stats,
            'verification': {
                'invariant_holds': abs(ryan_balance + jordyn_balance) < 0.01,
                'total_transactions_processed': len(self.all_transactions),
                'manual_review_count': len(self.manual_review_items),
                'errors_count': len(self.processing_errors)
            },
            'timestamp': datetime.now().isoformat()
        }
        
        summary_path = os.path.join(self.output_dir, 'summary.json')
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        print(f"  - Created: {summary_path}")
        
        # 4. Error log if any
        if self.processing_errors:
            error_path = os.path.join(self.output_dir, 'processing_errors.json')
            with open(error_path, 'w', encoding='utf-8') as f:
                json.dump(self.processing_errors, f, indent=2, default=str)
            print(f"  - Created: {error_path}")
    
    def run(self) -> str:
        """Run the complete reconciliation process."""
        print("="*60)
        print("FINANCIAL RECONCILIATION SYSTEM - PHASE 4")
        print("="*60)
        
        # Load all data
        transactions = self.load_all_data()
        
        # Process all transactions
        self.process_all_transactions(transactions)
        
        # Generate outputs
        self.generate_outputs()
        
        # Get final result
        ryan_balance = self.engine.ryan_account.get_balance()
        jordyn_balance = self.engine.jordyn_account.get_balance()
        
        print("\n" + "="*60)
        print("FINAL RECONCILIATION RESULT")
        print("="*60)
        print(f"Ryan's balance: ${ryan_balance:.2f}")
        print(f"Jordyn's balance: ${jordyn_balance:.2f}")
        print(f"Invariant check: {abs(ryan_balance + jordyn_balance) < 0.01}")
        
        if ryan_balance > 0:
            result = f"Jordyn owes Ryan ${ryan_balance:.2f}"
        else:
            result = f"Ryan owes Jordyn ${abs(ryan_balance):.2f}"
        
        print(f"\nFINAL ANSWER: {result}")
        print("="*60)
        
        print(f"\nTransactions requiring manual review: {len(self.manual_review_items)}")
        print(f"Processing errors: {len(self.processing_errors)}")
        
        return result


if __name__ == "__main__":
    processor = TransactionProcessor()
    result = processor.run()
    print(f"\n{result}")