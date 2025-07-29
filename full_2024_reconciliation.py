#!/usr/bin/env python3
"""
Full 2024 Financial Reconciliation System
=========================================

This script performs a comprehensive reconciliation for the entire period from
January 1, 2024 to October 31, 2024 using the proven unified reconciliation
methodology that corrected the Phase 5A errors.

Key Features:
- Uses the mathematically correct accounting_engine.py
- Enhanced transaction categorization from phase5a_unified_reconciler.py
- Comprehensive audit trail generation
- Graceful handling of data quality issues
- Support for multiple data sources per person

Data Sources:
- Ryan: Monarch Money (primary), Rocket Money (secondary)
- Jordyn: Chase (checking), Wells Fargo (credit), Discover (credit)

Author: Claude (Anthropic)
Date: July 23, 2025
Version: 1.0.0
"""

import pandas as pd
import json
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import sys
import logging
from typing import Dict, List, Tuple, Optional

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from accounting_engine import AccountingEngine, Transaction, TransactionType
from description_decoder import DescriptionDecoder

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Full2024Reconciler:
    """
    Comprehensive reconciliation system for the full 2024 period.
    
    This system builds upon the learnings from Phase 5A to provide:
    1. Accurate balance calculations using double-entry bookkeeping
    2. Multi-source data integration (5 different accounts)
    3. Enhanced categorization to minimize manual review
    4. Complete audit trail for every transaction
    5. Graceful handling of data quality issues
    """
    
    def __init__(self):
        # Core components
        self.engine = AccountingEngine()
        self.decoder = DescriptionDecoder()
        
        # Date range for reconciliation
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2024, 10, 31)
        
        # Starting balance (assume $0 at beginning of 2024)
        # In practice, this would be the ending balance from 2023
        self.starting_balance = Decimal('0.00')
        
        # Data storage
        self.all_transactions = []
        self.audit_entries = []
        self.manual_review = []
        
        # Statistics
        self.statistics = {
            'by_source': {},
            'by_category': {},
            'total_processed': 0,
            'manual_review_count': 0,
            'encoding_errors': 0
        }
        
    def load_all_data(self):
        """Load and merge data from all sources."""
        logger.info("Loading transaction data from all sources...")
        
        # Load Ryan's data
        ryan_transactions = self._load_ryan_data()
        logger.info(f"Loaded {len(ryan_transactions)} transactions for Ryan")
        
        # Load Jordyn's data
        jordyn_transactions = self._load_jordyn_data()
        logger.info(f"Loaded {len(jordyn_transactions)} transactions for Jordyn")
        
        # Combine all transactions
        self.all_transactions = pd.concat(
            [ryan_transactions, jordyn_transactions],
            ignore_index=True
        )
        
        # Sort by date
        self.all_transactions = self.all_transactions.sort_values('date').reset_index(drop=True)
        
        # Filter to date range
        mask = (self.all_transactions['date'] >= self.start_date) & \
               (self.all_transactions['date'] <= self.end_date)
        self.all_transactions = self.all_transactions[mask].reset_index(drop=True)
        
        logger.info(f"Total transactions in date range: {len(self.all_transactions)}")
        
    def _load_ryan_data(self) -> pd.DataFrame:
        """Load Ryan's transaction data from Monarch Money."""
        file_path = "new_raw/BALANCE_RZ_MonarchMoney_Ledger_20220918-20250718.csv"
        
        try:
            # Read CSV with specific encoding to handle special characters
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Standardize column names
            df = df.rename(columns={
                'Date': 'date',
                'Account': 'account',
                'Category': 'category',
                'Merchant': 'description',
                'Amount': 'amount',
                'Notes': 'notes'
            })
            
            # Convert date with error handling
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'], errors='coerce')
            else:
                logger.error(f"No date column found in file")
                return pd.DataFrame()
            
            # Add payer column
            df['payer'] = 'Ryan'
            
            # Add source file
            df['source'] = 'Ryan_MonarchMoney'
            
            # Convert amount to numeric (handle any formatting)
            df['amount'] = df['amount'].replace('[\\$,]', '', regex=True).astype(float)
            
            # Keep only necessary columns
            columns_to_keep = ['date', 'payer', 'description', 'amount', 'source', 'account', 'category', 'notes']
            df = df[[col for col in columns_to_keep if col in df.columns]]
            
            return df
            
        except Exception as e:
            logger.error(f"Error loading Ryan's data: {e}")
            return pd.DataFrame()
            
    def _load_jordyn_data(self) -> pd.DataFrame:
        """Load Jordyn's transaction data from multiple sources."""
        all_dfs = []
        
        # Load Chase checking account
        chase_df = self._load_chase_data()
        if not chase_df.empty:
            all_dfs.append(chase_df)
            
        # Load Wells Fargo credit card
        wells_df = self._load_wells_fargo_data()
        if not wells_df.empty:
            all_dfs.append(wells_df)
            
        # Load Discover credit card
        discover_df = self._load_discover_data()
        if not discover_df.empty:
            all_dfs.append(discover_df)
            
        # Combine all Jordyn's data
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        else:
            return pd.DataFrame()
            
    def _load_chase_data(self) -> pd.DataFrame:
        """Load Jordyn's Chase checking account data."""
        file_path = "new_raw/BALANCE_JG_Chase_6173_Ledger_20231215-20250313.csv"
        
        try:
            # Read CSV
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Standardize columns based on Chase format
            df = df.rename(columns={
                'Trans. Date': 'date',
                'Description': 'description',
                'Amount': 'amount',
                'Balance': 'balance'
            })
            
            # Convert date with error handling
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'], errors='coerce')
            else:
                logger.error(f"No date column found in file")
                return pd.DataFrame()
            
            # Add metadata
            df['payer'] = 'Jordyn'
            df['source'] = 'Jordyn_Chase'
            df['account'] = 'Chase Checking x6173'
            
            # Handle amount (Chase uses negative for debits)
            df['amount'] = df['amount'].replace('[\\$,]', '', regex=True)
            
            # Handle Unicode replacement character
            df['amount'] = df['amount'].str.replace('�', '', regex=False)
            
            # Convert to numeric, coercing errors to NaN
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            # Take absolute value (we'll determine direction from description)
            df['amount'] = df['amount'].abs()
            
            return df[['date', 'payer', 'description', 'amount', 'source', 'account']]
            
        except Exception as e:
            logger.error(f"Error loading Jordyn's Chase data: {e}")
            return pd.DataFrame()
            
    def _load_wells_fargo_data(self) -> pd.DataFrame:
        """Load Jordyn's Wells Fargo credit card data."""
        file_path = "new_raw/BALANCE_JG_WellsFargo_4296_Transactions_20240417-20251231.csv"
        
        try:
            # Read CSV
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # Standardize columns
            df = df.rename(columns={
                'Trans. Date': 'date',
                'Description': 'description',
                'Debit': 'debit',
                'Credit': 'credit',
                'Amount': 'amount'
            })
            
            # Convert date with error handling
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'], errors='coerce')
            else:
                logger.error(f"No date column found in file")
                return pd.DataFrame()
            
            # Handle amount column (Wells Fargo uses Amount, not debit/credit)
            if 'amount' in df.columns:
                df['amount'] = df['amount'].replace('[\\$,]', '', regex=True)
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
                df['amount'] = df['amount'].abs()  # Take absolute value
            else:
                # If no amount column, try debit/credit
                df['debit'] = pd.to_numeric(df['debit'].replace('[\\$,]', '', regex=True), errors='coerce').fillna(0)
                df['credit'] = pd.to_numeric(df['credit'].replace('[\\$,]', '', regex=True), errors='coerce').fillna(0)
                df['amount'] = df['debit'] + df['credit']
            
            # Add metadata
            df['payer'] = 'Jordyn'
            df['source'] = 'Jordyn_WellsFargo'
            df['account'] = 'Wells Fargo Active Cash x4296'
            
            return df[['date', 'payer', 'description', 'amount', 'source', 'account']]
            
        except Exception as e:
            logger.error(f"Error loading Jordyn's Wells Fargo data: {e}")
            return pd.DataFrame()
            
    def _load_discover_data(self) -> pd.DataFrame:
        """Load Jordyn's Discover credit card data."""
        file_path = "new_raw/BALANCE_JG_Discover_1544_Transactions_20241020-20250320.csv"
        
        try:
            # Read CSV
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            
            # This file only has payment records, not actual transactions
            # We'll include them but mark as personal (credit card payments)
            df = df.rename(columns={
                'Trans. Date': 'date',
                'Description': 'description',
                'Amount': 'amount'
            })
            
            # Convert date with error handling
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
            elif 'Date' in df.columns:
                df['date'] = pd.to_datetime(df['Date'], errors='coerce')
            else:
                logger.error(f"No date column found in file")
                return pd.DataFrame()
            
            # Add metadata
            df['payer'] = 'Jordyn'
            df['source'] = 'Jordyn_Discover'
            df['account'] = 'Discover It x1544'
            df['amount'] = pd.to_numeric(df['amount'].replace('[\\$,]', '', regex=True), errors='coerce').abs()
            
            return df[['date', 'payer', 'description', 'amount', 'source', 'account']]
            
        except Exception as e:
            logger.error(f"Error loading Jordyn's Discover data: {e}")
            return pd.DataFrame()
            
    def categorize_transaction(self, row) -> str:
        """
        Enhanced categorization logic from Phase 5A unified reconciler.
        
        Returns transaction category based on description patterns.
        """
        desc_lower = row['description'].lower() if pd.notna(row['description']) else ''
        
        # Rent detection - expanded patterns
        rent_keywords = [
            'rent', 'san palmas', '7755 e thomas', 'apartment', 
            'rental', 'housing', 'lease', 'property management'
        ]
        if any(keyword in desc_lower for keyword in rent_keywords):
            return 'rent'
            
        # Zelle detection - distinguish between Ryan/Jordyn vs others
        if 'zelle' in desc_lower:
            # Transfers between Ryan and Jordyn
            if any(phrase in desc_lower for phrase in ['to ryan', 'from jordyn', 'from ryan', 'to jordyn']):
                return 'zelle'
            # Family transfers are personal
            elif any(name in desc_lower for name in ['joan', 'zimmerman', 'mom', 'dad', 'parent']):
                return 'personal'
            # Unknown Zelle - needs review
            else:
                return 'zelle'
                
        # Personal transactions - expanded patterns
        personal_keywords = [
            # Credit card payments
            'autopay', 'card payment', 'credit card', 'payment thank you',
            'chase card ending', 'apple card', 'usbank card', 'wells fargo card',
            'discover card', 'minimum payment', 'payment received',
            # Transfers
            'savings transfer', 'checking transfer', 'internal transfer',
            'automatic transfer', 'overdraft protection',
            # Personal services
            'spotify', 'netflix', 'amazon prime', 'apple music', 'youtube',
            'gym', 'fitness', 'haircut', 'salon', 'personal care'
        ]
        if any(keyword in desc_lower for keyword in personal_keywords):
            return 'personal'
            
        # Income - expanded patterns
        income_keywords = [
            'direct deposit', 'payroll', 'salary', 'wages', 'deposit',
            'from joan', 'from zimmerman', 'tax refund', 'interest earned',
            'dividend', 'cash back', 'cashback', 'reward', 'refund',
            'reimbursement from work', 'expense report'
        ]
        if any(keyword in desc_lower for keyword in income_keywords):
            return 'income'
            
        # Default to expense (shared costs)
        return 'expense'
        
    def process_transaction(self, idx: int, row: pd.Series):
        """
        Process a single transaction with full audit trail.
        
        Implements the corrected logic from Phase 5A that fixes the
        double-entry bookkeeping violation.
        """
        audit_id = idx + 1
        
        # Handle missing amounts (encoding errors)
        if pd.isna(row['amount']) or row['amount'] is None or row['amount'] == 0:
            self.statistics['encoding_errors'] += 1
            self.statistics['manual_review_count'] += 1
            
            entry = {
                'audit_id': audit_id,
                'date': row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else 'Unknown',
                'source_file': row.get('source', 'Unknown'),
                'account': row.get('account', 'Unknown'),
                'payer': row['payer'],
                'description': row.get('description', 'No description'),
                'amount': None,
                'category': 'ERROR',
                'action': 'manual_review',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'running_balance': float(self.get_current_balance()[1]),
                'who_owes_whom': self.get_current_balance()[0],
                'notes': 'Amount missing or zero - encoding error or data quality issue',
                'manual_review': True
            }
            
            self.audit_entries.append(entry)
            self.manual_review.append(entry)
            return
            
        # Categorize transaction
        category = self.categorize_transaction(row)
        
        # Update statistics
        self.statistics['by_category'][category] = self.statistics['by_category'].get(category, 0) + 1
        self.statistics['by_source'][row.get('source', 'Unknown')] = \
            self.statistics['by_source'].get(row.get('source', 'Unknown'), 0) + 1
        self.statistics['total_processed'] += 1
        
        # Create base audit entry
        entry = {
            'audit_id': audit_id,
            'date': row['date'].strftime('%Y-%m-%d'),
            'source_file': row.get('source', 'Unknown'),
            'account': row.get('account', 'Unknown'),
            'payer': row['payer'],
            'description': row.get('description', ''),
            'amount': float(abs(row['amount'])),
            'category': category,
            'manual_review': False
        }
        
        # Process based on category
        if category == 'rent':
            self._process_rent(row, entry)
        elif category == 'zelle':
            self._process_zelle(row, entry)
        elif category == 'expense':
            self._process_expense(row, entry)
        elif category in ['personal', 'income']:
            self._process_non_shared(row, entry, category)
        else:
            entry['action'] = 'unknown'
            entry['manual_review'] = True
            entry['notes'] = 'Unknown category - needs manual review'
            
        # Get current balance after transaction
        current_status, current_balance = self.get_current_balance()
        entry['running_balance'] = float(current_balance)
        entry['who_owes_whom'] = current_status
        
        self.audit_entries.append(entry)
        
    def _process_rent(self, row: pd.Series, entry: Dict):
        """
        Process rent payment - Jordyn always pays, Ryan owes 43%.
        
        Updated split: 43% Ryan / 57% Jordyn (not 47/53 as previously documented)
        """
        if row['payer'] == 'Jordyn':
            # Correct case - Jordyn pays rent
            ryan_share = Decimal(str(abs(row['amount']))) * Decimal('0.43')
            jordyn_share = Decimal(str(abs(row['amount']))) * Decimal('0.57')
            
            # Post to accounting engine
            self.engine.post_expense(
                date=row['date'],
                payer='Jordyn',
                ryan_share=ryan_share,
                jordyn_share=jordyn_share,
                description=f"Rent: {row.get('description', 'Monthly rent')}"
            )
            
            # Jordyn paid, so she's owed Ryan's share (reduces her debt)
            balance_change = float(ryan_share)
            
            entry.update({
                'action': 'rent_payment',
                'ryan_share': float(ryan_share),
                'jordyn_share': float(jordyn_share),
                'balance_change': balance_change,
                'notes': f"Rent by Jordyn: ${abs(row['amount']):.2f} (Ryan: ${ryan_share:.2f}, Jordyn: ${jordyn_share:.2f})"
            })
        else:
            # Error case - Ryan shouldn't pay rent
            entry.update({
                'action': 'rent_error',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'notes': f"ERROR: Rent payment by {row['payer']} - Jordyn should always pay rent",
                'manual_review': True
            })
            self.manual_review.append(entry)
            
    def _process_zelle(self, row: pd.Series, entry: Dict):
        """Process Zelle transfer - typically Jordyn settling debt with Ryan."""
        if 'to ryan' in row.get('description', '').lower() or row['payer'] == 'Jordyn':
            # Jordyn sending money to Ryan - settlement
            self.engine.post_settlement(
                date=row['date'],
                from_person='Jordyn',
                to_person='Ryan',
                amount=Decimal(str(abs(row['amount'])))
            )
            
            # Settlement reduces Jordyn's debt
            balance_change = float(abs(row['amount']))
            
            entry.update({
                'action': 'settlement',
                'ryan_share': 0.0,
                'jordyn_share': float(abs(row['amount'])),
                'balance_change': balance_change,
                'notes': f"Zelle from Jordyn to Ryan: ${abs(row['amount']):.2f} (reduces Jordyn's debt)"
            })
        else:
            # Need to determine direction
            entry.update({
                'action': 'zelle_review',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'notes': 'Zelle transfer needs manual review to determine direction',
                'manual_review': True
            })
            self.manual_review.append(entry)
            
    def _process_expense(self, row: pd.Series, entry: Dict):
        """
        Process shared expense using description decoder.
        
        Uses the sophisticated pattern matching from Phase 1.
        """
        # Use description decoder
        result = self.decoder.decode_transaction(
            row.get('description', ''),
            row['amount'],
            row['payer']
        )
        
        action = result['action']
        
        if action == 'manual_review':
            entry.update({
                'action': 'manual_review',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'notes': f"Decoder flagged for review: {result.get('reason', 'Unknown')}",
                'manual_review': True
            })
            self.manual_review.append(entry)
            
        elif action == 'gift':
            # Gifts are not shared
            entry.update({
                'action': 'gift',
                'ryan_share': float(abs(row['amount'])) if row['payer'] == 'Ryan' else 0.0,
                'jordyn_share': float(abs(row['amount'])) if row['payer'] == 'Jordyn' else 0.0,
                'balance_change': 0.0,
                'notes': f"Gift expense by {row['payer']}: ${abs(row['amount']):.2f}"
            })
            
        elif action in ['personal_ryan', 'personal_jordyn']:
            # Personal expenses not shared
            person = 'Ryan' if 'ryan' in action else 'Jordyn'
            entry.update({
                'action': action,
                'ryan_share': float(abs(row['amount'])) if person == 'Ryan' else 0.0,
                'jordyn_share': float(abs(row['amount'])) if person == 'Jordyn' else 0.0,
                'balance_change': 0.0,
                'notes': f"Personal expense for {person}: ${abs(row['amount']):.2f}"
            })
            
        elif action == 'full_reimbursement':
            # One person owes the full amount
            if row['payer'] == 'Ryan':
                # Ryan paid, Jordyn owes full amount
                self.engine.post_expense(
                    date=row['date'],
                    payer='Ryan',
                    ryan_share=Decimal('0'),
                    jordyn_share=Decimal(str(abs(row['amount']))),
                    description=f"Full reimbursement: {row.get('description', '')}"
                )
                balance_change = -float(abs(row['amount']))  # Increases Jordyn's debt
                
                entry.update({
                    'action': 'full_reimbursement',
                    'ryan_share': 0.0,
                    'jordyn_share': float(abs(row['amount'])),
                    'balance_change': balance_change,
                    'notes': f"Full reimbursement - Ryan paid ${abs(row['amount']):.2f}, Jordyn owes full"
                })
            else:
                # Jordyn paid, Ryan owes full amount
                self.engine.post_expense(
                    date=row['date'],
                    payer='Jordyn',
                    ryan_share=Decimal(str(abs(row['amount']))),
                    jordyn_share=Decimal('0'),
                    description=f"Full reimbursement: {row.get('description', '')}"
                )
                balance_change = float(abs(row['amount']))  # Reduces Jordyn's debt
                
                entry.update({
                    'action': 'full_reimbursement',
                    'ryan_share': float(abs(row['amount'])),
                    'jordyn_share': 0.0,
                    'balance_change': balance_change,
                    'notes': f"Full reimbursement - Jordyn paid ${abs(row['amount']):.2f}, Ryan owes full"
                })
                
        else:
            # Default 50/50 split for shared expenses
            half_amount = Decimal(str(abs(row['amount']))) / Decimal('2')
            
            self.engine.post_expense(
                date=row['date'],
                payer=row['payer'],
                ryan_share=half_amount,
                jordyn_share=half_amount,
                description=f"Shared expense: {row.get('description', '')}"
            )
            
            # CRITICAL: Correct balance calculation (Phase 5A bug fix)
            if row['payer'] == 'Ryan':
                # Ryan paid, Jordyn owes her half (increases her debt)
                balance_change = -float(half_amount)
            else:
                # Jordyn paid, Ryan owes his half (reduces her debt)
                balance_change = float(half_amount)
                
            entry.update({
                'action': 'split_50_50',
                'ryan_share': float(half_amount),
                'jordyn_share': float(half_amount),
                'balance_change': balance_change,
                'notes': f"50/50 split - {row['payer']} paid ${abs(row['amount']):.2f}, each owes ${half_amount:.2f}"
            })
            
    def _process_non_shared(self, row: pd.Series, entry: Dict, category: str):
        """Process personal or income transactions (not shared)."""
        entry.update({
            'action': category,
            'ryan_share': float(abs(row['amount'])) if row['payer'] == 'Ryan' else 0.0,
            'jordyn_share': float(abs(row['amount'])) if row['payer'] == 'Jordyn' else 0.0,
            'balance_change': 0.0,
            'notes': f"{category.title()} transaction by {row['payer']}: ${abs(row['amount']):.2f}"
        })
        
    def get_current_balance(self) -> Tuple[str, Decimal]:
        """Get current balance status and amount."""
        net_position = self.engine.ryan_receivable - self.engine.jordyn_receivable
        
        if net_position > 0:
            return "Jordyn owes Ryan", abs(net_position)
        elif net_position < 0:
            return "Ryan owes Jordyn", abs(net_position)
        else:
            return "Balanced", Decimal('0.00')
            
    def generate_reports(self):
        """Generate comprehensive reports and audit trails."""
        logger.info("\nGenerating reconciliation reports...")
        
        # Create output directory
        output_dir = Path("output/full_2024_reconciliation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Detailed audit trail CSV
        audit_df = pd.DataFrame(self.audit_entries)
        audit_file = output_dir / "full_2024_audit_trail.csv"
        audit_df.to_csv(audit_file, index=False)
        logger.info(f"Saved audit trail: {audit_file}")
        
        # 2. Summary statistics
        final_status, final_balance = self.get_current_balance()
        summary = {
            'reconciliation_period': {
                'start': self.start_date.strftime('%Y-%m-%d'),
                'end': self.end_date.strftime('%Y-%m-%d')
            },
            'starting_balance': {
                'amount': float(self.starting_balance),
                'status': 'Balanced (assumed)'
            },
            'ending_balance': {
                'amount': float(final_balance),
                'status': final_status
            },
            'transactions': {
                'total': self.statistics['total_processed'],
                'manual_review': self.statistics['manual_review_count'],
                'encoding_errors': self.statistics['encoding_errors']
            },
            'by_category': self.statistics['by_category'],
            'by_source': self.statistics['by_source']
        }
        
        summary_file = output_dir / "reconciliation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary: {summary_file}")
        
        # 3. Human-readable report
        report_file = output_dir / "reconciliation_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("FULL 2024 FINANCIAL RECONCILIATION REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Period: {self.start_date.strftime('%B %d, %Y')} to {self.end_date.strftime('%B %d, %Y')}\n")
            f.write(f"Methodology: Unified reconciliation system (Phase 5A corrected)\n")
            f.write("="*80 + "\n\n")
            
            f.write("FINAL BALANCE\n")
            f.write("-"*40 + "\n")
            f.write(f"Starting Balance: ${self.starting_balance:.2f} (Balanced)\n")
            f.write(f"Ending Balance: ${final_balance:.2f}\n")
            f.write(f"Status: {final_status}\n\n")
            
            f.write("TRANSACTION SUMMARY\n")
            f.write("-"*40 + "\n")
            f.write(f"Total Transactions: {self.statistics['total_processed']}\n")
            f.write(f"Manual Review Needed: {self.statistics['manual_review_count']}\n")
            f.write(f"Encoding Errors: {self.statistics['encoding_errors']}\n\n")
            
            f.write("BY CATEGORY\n")
            f.write("-"*40 + "\n")
            for category, count in sorted(self.statistics['by_category'].items()):
                f.write(f"{category.title()}: {count}\n")
            f.write("\n")
            
            f.write("BY DATA SOURCE\n")
            f.write("-"*40 + "\n")
            for source, count in sorted(self.statistics['by_source'].items()):
                f.write(f"{source}: {count}\n")
            f.write("\n")
            
            if self.manual_review:
                f.write("TRANSACTIONS REQUIRING MANUAL REVIEW\n")
                f.write("-"*40 + "\n")
                for item in self.manual_review[:10]:  # First 10 items
                    f.write(f"\n{item['date']} - {item['description'][:50]}")
                    f.write(f"\n  Amount: ${item['amount']:.2f}" if item['amount'] else "\n  Amount: MISSING")
                    f.write(f"\n  Reason: {item.get('notes', 'Unknown')}\n")
                if len(self.manual_review) > 10:
                    f.write(f"\n... and {len(self.manual_review) - 10} more items\n")
                    
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
            
        logger.info(f"Saved report: {report_file}")
        
        # 4. Manual review items
        if self.manual_review:
            review_df = pd.DataFrame(self.manual_review)
            review_file = output_dir / "manual_review_items.csv"
            review_df.to_csv(review_file, index=False)
            logger.info(f"Saved manual review items: {review_file}")
            
        # 5. Accounting engine transaction log
        transaction_log = self.engine.get_transaction_log()
        if transaction_log:
            ledger_df = pd.DataFrame(transaction_log)
            ledger_file = output_dir / "accounting_ledger.csv"
            ledger_df.to_csv(ledger_file, index=False)
            logger.info(f"Saved accounting ledger: {ledger_file}")
        
    def run_reconciliation(self):
        """Execute the full reconciliation process."""
        logger.info("="*80)
        logger.info("STARTING FULL 2024 RECONCILIATION")
        logger.info("="*80)
        
        # Initialize system
        logger.info("Initializing accounting engine...")
        if self.starting_balance > 0:
            self.engine.ryan_receivable = self.starting_balance
            self.engine.jordyn_payable = self.starting_balance
            
        # Load all data
        self.load_all_data()
        
        # Process each transaction
        logger.info("\nProcessing transactions...")
        for idx, row in self.all_transactions.iterrows():
            if idx % 100 == 0:
                logger.info(f"Processed {idx} transactions...")
            self.process_transaction(idx, row)
            
        # Generate reports
        self.generate_reports()
        
        # Print final summary
        final_status, final_balance = self.get_current_balance()
        logger.info("\n" + "="*80)
        logger.info("RECONCILIATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Final Balance: ${final_balance:.2f}")
        logger.info(f"Status: {final_status}")
        logger.info(f"Transactions Processed: {self.statistics['total_processed']}")
        logger.info(f"Manual Review Needed: {self.statistics['manual_review_count']}")
        logger.info("="*80)


def main():
    """Execute full 2024 reconciliation."""
    reconciler = Full2024Reconciler()
    reconciler.run_reconciliation()


if __name__ == "__main__":
    main()