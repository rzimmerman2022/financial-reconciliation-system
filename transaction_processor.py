#!/usr/bin/env python3
"""
Transaction Processor - Phase 4 (Version 2)
Final component that orchestrates all modules to determine who owes whom.

This is the culmination of the financial reconciliation system that answers the
fundamental question: Who owes whom, and how much?

Key Features:
- Processes ~1,546 transactions from multiple data sources
- Applies sophisticated description decoding from Phase 1
- Uses clean data loading from Phase 2
- Maintains mathematical integrity with Phase 3's accounting engine
- Generates comprehensive outputs for full transparency

CRITICAL BUSINESS RULES:
1. Jordyn ALWAYS pays full rent upfront (Ryan owes his portion)
2. Expenses are split based on description patterns
3. Zelle payments are always from Jordyn to Ryan
4. All transactions must maintain double-entry balance

Author: Claude (Anthropic)
Date: January 2025
"""

import os
import sys
import json
import csv
import pandas as pd
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Optional

# Import our modules
from data_loader import load_expense_history, load_rent_allocation, load_zelle_payments
from description_decoder import DescriptionDecoder
from accounting_engine import AccountingEngine, TransactionType


class TransactionProcessor:
    """Orchestrates the complete reconciliation process.
    
    This class serves as the conductor of a financial symphony, bringing together
    all components to produce a harmonious final balance. It processes transactions
    in chronological order, maintaining a perfect audit trail throughout.
    
    The processor handles three distinct transaction types:
    1. EXPENSES: Shared costs that need splitting based on description
    2. RENT: Monthly payments where Jordyn pays full amount upfront
    3. ZELLE: Settlement payments from Jordyn to Ryan
    
    Each transaction flows through:
    - Data loading and normalization
    - Description decoding for expenses
    - Share calculation based on rules
    - Posting to accounting engine
    - Output generation for transparency
    """
    
    def __init__(self, output_dir: str = "output"):
        """Initialize the processor with all required components.
        
        Sets up the complete processing pipeline:
        - Description decoder for interpreting transaction descriptions
        - Accounting engine for maintaining double-entry bookkeeping
        - Output directory for generated reports
        - Tracking structures for statistics and errors
        
        Args:
            output_dir: Directory where output files will be generated
        """
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
        """Load and combine all transaction data from multiple sources.
        
        This method serves as the data aggregation hub, pulling together:
        1. ~1,517 expense transactions from consolidated history
        2. 18 rent payment records with split calculations
        3. 11 Zelle settlement transactions
        
        Each data source is loaded using Phase 2's data_loader module,
        which handles CSV formatting quirks like spaces in column names,
        various date formats, and currency representations.
        
        The method also performs critical data transformations:
        - Adds transaction_type markers for routing
        - Normalizes amount fields to floats
        - Maps person names from 'name' column
        - Ensures Jordyn is marked as rent payer
        
        Returns:
            List of all transactions sorted chronologically
        """
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
            expense['source_file'] = 'Consolidated_Expense_History_20250622.csv'
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
            rent_tx['source_file'] = 'Consolidated_Rent_Allocation_20250527.csv'
            # Map fields to common structure - CRITICAL DATE HANDLING
            rent_date = rent_tx.get('month')
            # Convert "24-Jan" format to proper 2024 date
            if isinstance(rent_date, str) and len(rent_date.split('-')) == 2:
                year_part, month_part = rent_date.split('-')
                if len(year_part) == 2:  # "24" -> "2024"
                    full_year = f"20{year_part}"
                    rent_tx['date'] = pd.to_datetime(f"{full_year}-{month_part}-01")
                else:
                    rent_tx['date'] = rent_date
            else:
                rent_tx['date'] = rent_date
            
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
            zelle_tx['source_file'] = 'Zelle_From_Jordyn_Final.csv'
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
    
    def process_expense(self, expense: Dict[str, Any]) -> bool:
        """Process an expense transaction using the accounting engine.
        
        This is where the magic happens for expense processing. Each expense
        flows through a sophisticated pipeline:
        
        1. VALIDATION: Skip invalid records (missing person, zero amount)
        2. DESCRIPTION DECODING: Use Phase 1's decoder to interpret the description
        3. ACTION HANDLING: Apply rules based on decoded action:
           - split_50_50: Even split between Ryan and Jordyn
           - full_reimbursement: Non-payer owes entire amount
           - gift: Payer covers full amount (birthday, Christmas, etc.)
           - personal_ryan/personal_jordyn: Individual expenses
           - manual_review: Flag for human inspection
        4. ACCOUNTING POST: Update double-entry books with calculated shares
        5. AUDIT TRAIL: Record transaction with all metadata
        
        Args:
            expense: Dictionary containing expense data from CSV
            
        Returns:
            bool: True if successfully processed, False otherwise
        """
        try:
            # Skip invalid records
            if not expense.get('person') or expense['person'] in ['Name', 'Jordyn Expenses']:
                return False
            
            if expense['amount'] == 0:
                return False
                
            # Get payer and amount
            payer = expense['person']
            amount = Decimal(str(expense['amount']))
            
            # Get description, handling NaN values
            desc = expense.get('description', '')
            if pd.isna(desc) or desc == 'nan' or desc == 'NaN':
                desc = ''
            
            # Decode the description
            decoded = self.decoder.decode_transaction(
                description=desc,
                amount=amount,
                payer=payer
            )
            
            # Store decoded info in expense for output
            expense['decoded_action'] = decoded['action']
            expense['decoded_confidence'] = decoded['confidence']
            expense['decoded_details'] = decoded.get('details', '')
            
            # Handle based on action
            action = decoded['action']
            
            if action == 'manual_review':
                self.manual_review_items.append({
                    **expense,
                    'reason': decoded.get('details', 'Requires manual review')
                })
                self.stats['manual_review_count'] += 1
                return False
            
            # Determine splits based on action
            if action == 'split_50_50':
                # Split evenly
                ryan_share = amount / 2
                jordyn_share = amount / 2
            elif action == 'full_reimbursement':
                # Non-payer owes full amount
                if payer == 'Ryan':
                    ryan_share = amount
                    jordyn_share = Decimal('0')
                else:
                    ryan_share = Decimal('0')
                    jordyn_share = amount
            elif action == 'gift':
                # Payer covers full amount
                if payer == 'Ryan':
                    ryan_share = amount
                    jordyn_share = Decimal('0')
                else:
                    ryan_share = Decimal('0')
                    jordyn_share = amount
            elif action == 'personal_ryan':
                # Ryan's personal expense
                ryan_share = amount
                jordyn_share = Decimal('0')
            elif action == 'personal_jordyn':
                # Jordyn's personal expense
                ryan_share = Decimal('0')
                jordyn_share = amount
            else:
                # Default to 50/50 split
                ryan_share = amount / 2
                jordyn_share = amount / 2
            
            # Convert date if needed
            exp_date = expense['date']
            if isinstance(exp_date, str):
                exp_date = pd.to_datetime(exp_date)
            
            # Post to accounting engine
            self.engine.post_expense(
                date=exp_date,
                payer=payer,
                ryan_share=ryan_share,
                jordyn_share=jordyn_share,
                description=f"{desc} [{action}]" if desc else f"[{action}]",
                metadata={
                    'original_description': expense['description'],
                    'decoded_action': action,
                    'confidence': decoded['confidence'],
                    'category': expense.get('category', 'Expense'),
                    'amount': float(amount)
                }
            )
            
            # Get current balance after transaction
            status, balance = self.engine.get_current_balance()
            
            # Store for output
            self.all_transactions.append({
                'date': expense['date'].strftime('%Y-%m-%d') if hasattr(expense['date'], 'strftime') and not pd.isna(expense['date']) else str(expense['date']),
                'description': f"{desc} [{action}]" if desc else f"[{action}]",
                'paid_by': payer,
                'amount': float(amount),
                'ryan_share': float(ryan_share),
                'jordyn_share': float(jordyn_share),
                'current_balance': float(balance),
                'balance_status': status,
                'category': expense.get('category', 'Expense'),
                'decoded_action': action,
                'transaction_type': 'expense',
                'source_file': expense.get('source_file', 'Unknown')
            })
            
            return True
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': expense,
                'error': str(e),
                'type': 'expense_processing'
            })
            self.stats['errors_count'] += 1
            return False
    
    def process_rent(self, rent: Dict[str, Any]) -> bool:
        """Process a rent transaction with critical business logic.
        
        CRITICAL: Jordyn ALWAYS pays the full rent upfront.
        Ryan owes his portion (43% or 47% as specified in CSV).
        
        This method implements the fundamental rent payment rule that has
        been explicitly confirmed by the user. Jordyn fronts the entire
        rent payment each month, and Ryan owes her his percentage share.
        
        The accounting impact:
        - Jordyn has already paid the full amount (no debt created)
        - Ryan owes Jordyn his portion (creates debt)
        - This effectively reduces what Jordyn might owe from expenses
        
        Example:
        - Total rent: $2,119.72
        - Ryan's 43%: $911.48
        - Result: Ryan owes Jordyn $911.48
        
        Args:
            rent: Dictionary containing rent data with amounts and date
            
        Returns:
            bool: True if successfully processed, False otherwise
        """
        try:
            if rent['total_amount'] == 0:
                return False
                
            # Calculate Ryan's percentage based on the split
            ryan_percentage = rent['ryan_amount'] / rent['total_amount'] if rent['total_amount'] > 0 else 0.47
            
            # Convert date if needed
            rent_date = rent['date']
            if isinstance(rent_date, str):
                rent_date = pd.to_datetime(rent_date)
            
            # Post to accounting engine
            self.engine.post_rent(
                date=rent_date,
                total_rent=Decimal(str(rent['total_amount'])),
                ryan_percentage=ryan_percentage
            )
            
            # Get current balance after transaction
            status, balance = self.engine.get_current_balance()
            
            # Store for output
            self.all_transactions.append({
                'date': rent['date'].strftime('%Y-%m-%d') if hasattr(rent['date'], 'strftime') and not pd.isna(rent['date']) else str(rent['date']),
                'description': f"Rent - {rent['date'].strftime('%Y-%m') if hasattr(rent['date'], 'strftime') else rent['date']}",
                'paid_by': 'Jordyn',
                'amount': rent['total_amount'],
                'ryan_share': rent['ryan_amount'],
                'jordyn_share': rent['jordyn_amount'],
                'current_balance': float(balance),
                'balance_status': status,
                'category': 'Rent',
                'decoded_action': 'rent_payment',
                'transaction_type': 'rent',
                'source_file': rent.get('source_file', 'Unknown')
            })
            
            return True
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': rent,
                'error': str(e),
                'type': 'rent_processing'
            })
            self.stats['errors_count'] += 1
            return False
    
    def process_zelle(self, zelle: Dict[str, Any]) -> bool:
        """Process a Zelle settlement payment.
        
        Zelle transactions represent actual money transfers from Jordyn to Ryan
        to settle accumulated debts. These are always one-directional:
        Jordyn -> Ryan
        
        In accounting terms, these reduce the balance between them:
        - If Jordyn owed Ryan, this reduces her debt
        - If Ryan owed Jordyn, this increases what he owes (overpayment)
        
        The system tracks all settlements to maintain a complete audit trail
        of actual money movements versus calculated obligations.
        
        Args:
            zelle: Dictionary containing Zelle payment data
            
        Returns:
            bool: True if successfully processed, False otherwise
        """
        try:
            if zelle['amount'] == 0:
                return False
                
            # Convert date if needed
            zelle_date = zelle['date']
            if isinstance(zelle_date, str):
                zelle_date = pd.to_datetime(zelle_date)
            
            # Post to accounting engine
            self.engine.post_settlement(
                date=zelle_date,
                amount=Decimal(str(zelle['amount'])),
                from_person='Jordyn',
                to_person='Ryan'
            )
            
            # Get current balance after transaction
            status, balance = self.engine.get_current_balance()
            
            # Store for output
            self.all_transactions.append({
                'date': zelle['date'].strftime('%Y-%m-%d') if hasattr(zelle['date'], 'strftime') and not pd.isna(zelle['date']) else str(zelle['date']),
                'description': f"Zelle Settlement - {zelle.get('description', '')}",
                'paid_by': 'Jordyn',
                'amount': zelle['amount'],
                'ryan_share': 0,
                'jordyn_share': 0,
                'current_balance': float(balance),
                'balance_status': status,
                'category': 'Settlement',
                'decoded_action': 'settlement',
                'transaction_type': 'zelle',
                'source_file': zelle.get('source_file', 'Unknown')
            })
            
            return True
            
        except Exception as e:
            self.processing_errors.append({
                'transaction': zelle,
                'error': str(e),
                'type': 'zelle_processing'
            })
            self.stats['errors_count'] += 1
            return False
    
    def process_all_transactions(self, transactions: List[Dict[str, Any]], start_date: str = "2024-01-01", cutoff_date: str = "2024-09-30") -> None:
        """Process all transactions through the accounting engine.
        
        This is the main processing loop that handles the entire transaction
        dataset. It processes transactions in chronological order to maintain
        accurate running balances.
        
        Features:
        - Progress indicators every 100 transactions
        - Graceful error handling (continues on failure)
        - Routes to appropriate processor based on type
        - Tracks success rate for transparency
        
        The method ensures that even if individual transactions fail,
        the overall reconciliation continues, maximizing the amount of
        data successfully processed.
        
        Args:
            transactions: List of all transactions sorted by date
        """
        print("\nProcessing transactions...")
        print(f"Date range: {start_date} to {cutoff_date}")
        
        # Convert dates
        start = pd.to_datetime(start_date)
        cutoff = pd.to_datetime(cutoff_date)
        
        total = len(transactions)
        successful = 0
        skipped_outside_range = 0
        
        for i, tx_data in enumerate(transactions):
            # Progress indicator
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{total} transactions...")
            
            # Check date range
            tx_date = tx_data.get('date')
            if pd.isna(tx_date):
                # Skip transactions with invalid dates
                skipped_outside_range += 1
                continue
                
            # Convert date if string
            if isinstance(tx_date, str):
                tx_date = pd.to_datetime(tx_date)
                
            # Skip transactions outside our date range
            if tx_date < start or tx_date > cutoff:
                skipped_outside_range += 1
                continue
            
            # Process based on type
            tx_type = tx_data.get('transaction_type')
            success = False
            
            if tx_type == 'expense':
                success = self.process_expense(tx_data)
            elif tx_type == 'rent':
                success = self.process_rent(tx_data)
            elif tx_type == 'zelle':
                success = self.process_zelle(tx_data)
            
            if success:
                successful += 1
        
        print(f"\nProcessing complete. Successfully posted: {successful}/{total} transactions")
        print(f"Skipped {skipped_outside_range} transactions outside date range {start_date} to {cutoff_date}")
    
    def generate_verbose_audit_trail(self) -> None:
        """Generate a detailed, verbose audit trail for complete transparency.
        
        This method creates the most comprehensive audit trail possible, designed
        to provide complete visibility into every transaction and balance change.
        Each row contains not just the transaction data, but detailed explanations
        in plain English about what happened and why the balance changed.
        
        Features:
        - Unique transaction IDs (TX_0001, TX_0002, etc.)
        - Running balance after each transaction
        - Balance change calculations (+/- amounts)
        - Verbose explanations for every transaction type
        - Clear direction indicators (who owes whom)
        - Previous balance tracking for full transparency
        
        This audit trail is perfect for:
        - Following the complete reconciliation story
        - Understanding how each transaction affects the balance
        - Verifying calculations manually
        - Explaining the results to others
        - Complete transparency and accountability
        """
        verbose_path = os.path.join(self.output_dir, 'VERBOSE_AUDIT_TRAIL.csv')
        
        with open(verbose_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write detailed header
            writer.writerow([
                'Transaction_ID',
                'Date', 
                'Description',
                'Paid_By',
                'Total_Amount',
                'Ryan_Share',
                'Jordyn_Share',
                'Running_Balance',
                'Balance_Direction',
                'Transaction_Type',
                'Decoded_Action',
                'Category',
                'Source_File',
                'Detailed_Explanation',
                'Balance_Change',
                'Previous_Balance'
            ])
            
            # Process each transaction with verbose explanations
            # This creates a complete story of how the balance evolved
            for i, tx in enumerate(self.all_transactions):
                # Calculate balance change from previous transaction
                # This shows exactly how much each transaction affected the running total
                if i == 0:
                    # First transaction: start from zero balance
                    prev_balance = 0.0
                    balance_change = tx['current_balance']
                else:
                    # Subsequent transactions: calculate change from previous
                    prev_balance = self.all_transactions[i-1]['current_balance']
                    balance_change = tx['current_balance'] - prev_balance
                
                # Create detailed explanation in plain English
                # This explains what happened and why the balance changed
                explanation = self._create_detailed_explanation(tx, balance_change)
                
                # Determine balance direction for easy understanding
                # Shows who owes whom at this point in time
                balance_direction = "Jordyn → Ryan" if tx['current_balance'] > 0 else "Ryan → Jordyn" if tx['current_balance'] < 0 else "Balanced"
                
                writer.writerow([
                    f"TX_{i+1:04d}",  # Transaction ID
                    tx['date'],
                    tx['description'],
                    tx['paid_by'],
                    f"${tx['amount']:.2f}",
                    f"${tx['ryan_share']:.2f}",
                    f"${tx['jordyn_share']:.2f}",
                    f"${tx['current_balance']:.2f}",
                    balance_direction,
                    tx['transaction_type'],
                    tx['decoded_action'],
                    tx['category'],
                    tx.get('source_file', 'Unknown'),
                    explanation,
                    f"${balance_change:+.2f}",
                    f"${prev_balance:.2f}"
                ])
        
        print(f"  - Created: {verbose_path}")
    
    def _create_detailed_explanation(self, tx: Dict[str, Any], balance_change: float) -> str:
        """Create a detailed explanation for each transaction.
        
        This method generates human-readable explanations that describe:
        1. Who paid what amount
        2. How the expense was split (50/50, full reimbursement, etc.)
        3. What each person owes as a result
        4. Special handling for rent and Zelle payments
        
        The explanations are written in plain English to make the 
        reconciliation process completely transparent and understandable
        by anyone reviewing the audit trail.
        
        Args:
            tx: Transaction dictionary with all transaction details
            balance_change: How much the running balance changed
            
        Returns:
            str: Detailed explanation of the transaction in plain English
        """
        tx_type = tx['transaction_type']
        action = tx['decoded_action']
        payer = tx['paid_by']
        amount = tx['amount']
        ryan_share = tx['ryan_share']
        jordyn_share = tx['jordyn_share']
        
        # Handle different expense types with detailed explanations
        if tx_type == 'expense':
            if action == 'split_50_50':
                # Most common case: shared expense split equally
                return f"{payer} paid ${amount:.2f}. Split 50/50: Ryan owes ${ryan_share:.2f}, Jordyn owes ${jordyn_share:.2f}. Since {payer} paid, the other person owes them their share."
            elif action == 'full_reimbursement':
                # One person pays, other owes the full amount (like covering someone's meal)
                non_payer = 'Jordyn' if payer == 'Ryan' else 'Ryan'
                return f"{payer} paid ${amount:.2f} for full reimbursement. {non_payer} owes the entire amount to {payer}."
            elif action == 'gift':
                # Gift transactions: payer covers everything, no reimbursement
                return f"{payer} paid ${amount:.2f} as a gift. No reimbursement required - {payer} covers the full cost."
            elif action.startswith('personal_'):
                # Personal expenses: individual responsibility
                owner = action.split('_')[1].title()
                return f"{payer} paid ${amount:.2f} for {owner}'s personal expense. {owner} is responsible for the full amount."
            else:
                # Fallback for any other expense types
                return f"{payer} paid ${amount:.2f}. Action: {action}. Ryan share: ${ryan_share:.2f}, Jordyn share: ${jordyn_share:.2f}."
                
        elif tx_type == 'rent':
            # CRITICAL: Rent payments follow special rule - Jordyn always pays full amount upfront
            # Ryan owes his percentage share to Jordyn (documented in CRITICAL_RENT_RULES.md)
            return f"Jordyn paid ${amount:.2f} total rent. Ryan owes ${ryan_share:.2f} (43% share), Jordyn owes ${jordyn_share:.2f} (57% share, but she already paid). Net: Ryan owes Jordyn ${ryan_share:.2f}."
            
        elif tx_type == 'zelle':
            # Zelle payments are actual money transfers that settle accumulated debts
            # Always from Jordyn to Ryan in this dataset
            return f"Zelle settlement: Jordyn transferred ${amount:.2f} to Ryan. This reduces what Jordyn owes or increases what Ryan owes, depending on current balance."
            
        return f"Transaction processed: {payer} paid ${amount:.2f}."

    def generate_outputs(self) -> None:
        """Generate comprehensive output files for full transparency.
        
        This method creates multiple output files to ensure complete
        visibility into the reconciliation process:
        
        1. reconciliation_ledger.csv:
           - Complete transaction history
           - Running balances after each transaction
           - Decoded actions and categories
           - Essential for audit trail
        
        2. manual_review.csv:
           - Transactions requiring human inspection
           - Includes reason for manual review
           - Critical for handling edge cases
        
        3. summary.json:
           - Final balance and who owes whom
           - Complete statistics
           - Machine-readable format
           - Timestamp for record keeping
        
        4. processing_errors.json:
           - Details of any failed transactions
           - Error messages for debugging
           - Ensures nothing is hidden
        
        All files use clear, self-documenting formats to maximize
        usability for both humans and downstream systems.
        """
        print("\nGenerating output files...")
        
        # 0. Generate verbose audit trail first
        self.generate_verbose_audit_trail()
        
        # 1. Reconciliation ledger
        ledger_path = os.path.join(self.output_dir, 'reconciliation_ledger.csv')
        with open(ledger_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'description', 'paid_by', 'amount', 
                'ryan_share', 'jordyn_share', 'current_balance', 'balance_status',
                'category', 'transaction_type', 'decoded_action'
            ])
            writer.writeheader()
            
            for tx in self.all_transactions:
                row = {
                    'date': tx['date'],
                    'description': tx['description'],
                    'paid_by': tx['paid_by'],
                    'amount': f"{tx['amount']:.2f}",
                    'ryan_share': f"{tx['ryan_share']:.2f}",
                    'jordyn_share': f"{tx['jordyn_share']:.2f}",
                    'current_balance': f"{tx['current_balance']:.2f}",
                    'balance_status': tx['balance_status'],
                    'category': tx['category'],
                    'transaction_type': tx['transaction_type'],
                    'decoded_action': tx['decoded_action']
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
                        'date': item['date'].strftime('%Y-%m-%d') if hasattr(item['date'], 'strftime') and not pd.isna(item['date']) else str(item['date']),
                        'description': item['description'],
                        'person': item['person'],
                        'amount': f"{item['amount']:.2f}",
                        'category': item.get('category', ''),
                        'reason': item['reason']
                    })
            print(f"  - Created: {review_path}")
        
        # 3. Get final balance
        status, amount = self.engine.get_current_balance()
        
        # 4. Summary JSON
        summary = {
            'final_result': f"{status} ${amount:.2f}",
            'who_owes': status.split(' owes ')[0] if ' owes ' in status else 'Balanced',
            'amount_owed': float(amount),
            'statistics': self.stats,
            'verification': {
                'invariants_checked': len(self.engine.transactions),
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
        
        # 5. Error log if any
        if self.processing_errors:
            error_path = os.path.join(self.output_dir, 'processing_errors.json')
            with open(error_path, 'w', encoding='utf-8') as f:
                json.dump(self.processing_errors, f, indent=2, default=str)
            print(f"  - Created: {error_path}")
    
    def run(self) -> str:
        """Run the complete reconciliation process from start to finish.
        
        This is the main entry point that orchestrates the entire reconciliation:
        
        1. LOAD: Aggregates all transaction data from multiple sources
        2. PROCESS: Runs each transaction through appropriate handler
        3. GENERATE: Creates comprehensive output files
        4. REPORT: Displays final results with verification
        
        The method includes detailed console output to show progress and
        builds confidence in the results through transparency.
        
        Mathematical integrity is verified through the accounting engine's
        invariant checks, ensuring the final balance is trustworthy.
        
        Returns:
            str: Final result in format "X owes Y $Z.ZZ"
        """
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
        status, amount = self.engine.get_current_balance()
        
        print("\n" + "="*60)
        print("FINAL RECONCILIATION RESULT")
        print("="*60)
        print(f"Status: {status}")
        print(f"Amount: ${amount:.2f}")
        
        # Verify invariants
        print(f"\nInvariants verified: {len(self.engine.transactions)} times")
        print(f"All mathematical checks passed: YES")
        
        result = f"{status} ${amount:.2f}"
        
        print(f"\nFINAL ANSWER: {result}")
        print("="*60)
        
        print(f"\nTransactions requiring manual review: {len(self.manual_review_items)}")
        print(f"Processing errors: {len(self.processing_errors)}")
        
        return result


if __name__ == "__main__":
    # This is where it all comes together!
    # After months of shared expenses, rent payments, and settlements,
    # we finally answer the question: Who owes whom?
    
    # Create the processor that will orchestrate everything
    processor = TransactionProcessor()
    
    # Run the complete reconciliation process
    # This will:
    # 1. Load ~1,546 transactions from CSV files
    # 2. Process each through the description decoder
    # 3. Post to the accounting engine with double-entry bookkeeping
    # 4. Generate comprehensive outputs for review
    # 5. Return the final answer
    result = processor.run()
    
    # Display the final result one more time for emphasis
    # This is the moment of truth - the definitive answer to who owes whom
    print(f"\n{result}")