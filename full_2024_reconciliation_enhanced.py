#!/usr/bin/env python3
"""
Enhanced Full 2024 Financial Reconciliation System
=================================================

This enhanced version properly handles the two-phase data structure:
1. Phase 4 (Jan 1 - Sept 30, 2024): Uses consolidated expense history with manual annotations
2. Phase 5 (Oct 1 - Oct 31, 2024): Uses raw bank data with interactive classification

Key Improvements:
- Correctly processes "2x to calculate" and other manual annotations
- Implements classification mechanism for post-baseline transactions
- Maintains continuity from the Phase 4 baseline of $1,577.08

Author: Claude (Anthropic)
Date: July 23, 2025
Version: 2.0.0
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
import data_loader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Critical baseline from Phase 4
PHASE_4_ENDING_BALANCE = Decimal('1577.08')  # Jordyn owes Ryan
BASELINE_DATE = datetime(2024, 9, 30)


class EnhancedFull2024Reconciler:
    """
    Enhanced reconciliation system that properly handles both:
    1. Manually annotated consolidated expense history (pre-baseline)
    2. Raw bank data requiring classification (post-baseline)
    """
    
    def __init__(self):
        # Core components
        self.engine = AccountingEngine()
        self.decoder = DescriptionDecoder()
        
        # Date ranges
        self.phase4_start = datetime(2024, 1, 1)
        self.phase4_end = datetime(2024, 9, 30)
        self.phase5_start = datetime(2024, 10, 1)
        self.phase5_end = datetime(2024, 10, 31)
        
        # Starting balance from Phase 4
        self.starting_balance = PHASE_4_ENDING_BALANCE
        
        # Data storage
        self.phase4_transactions = []
        self.phase5_transactions = []
        self.all_transactions = []
        self.audit_entries = []
        self.manual_review = []
        
        # Classification cache for post-baseline transactions
        self.classification_cache = {}
        
        # Statistics
        self.statistics = {
            'phase4': {'total': 0, 'by_category': {}},
            'phase5': {'total': 0, 'by_category': {}, 'manual_classified': 0},
            'special_annotations': {
                '2x_to_calculate': 0,
                'gifts': 0,
                'personal_100': 0,
                'exclusions': 0
            }
        }
        
    def load_phase4_data(self):
        """Load Phase 4 data from consolidated expense history with manual annotations."""
        logger.info("Loading Phase 4 data (Jan 1 - Sept 30, 2024) from consolidated expense history...")
        
        # Load the manually reviewed data
        file_path = "data/raw/Consolidated_Expense_History_20250622.csv"
        df = data_loader.load_expense_history(file_path)
        
        if df is None or df.empty:
            logger.error("Failed to load consolidated expense history!")
            return pd.DataFrame()
            
        # Filter to Phase 4 date range
        df['date_of_purchase'] = pd.to_datetime(df['date_of_purchase'], errors='coerce')
        mask = (df['date_of_purchase'] >= self.phase4_start) & (df['date_of_purchase'] <= self.phase4_end)
        phase4_df = df[mask].copy()
        
        # Standardize columns for processing
        phase4_df = phase4_df.rename(columns={
            'date_of_purchase': 'date',
            'name': 'payer',
            'merchant': 'description',
            'allowed_amount': 'amount',  # CRITICAL: Use allowed_amount, not actual_amount!
            'description': 'manual_notes',  # This contains the critical annotations!
            'merchant_description': 'merchant_desc'  # Additional merchant info
        })
        
        # Clean payer column - ensure it's a string and valid
        phase4_df['payer'] = phase4_df['payer'].apply(lambda x: str(x).strip() if pd.notna(x) else 'Unknown')
        
        # Filter out invalid payers
        valid_payers = ['Ryan', 'Jordyn']
        phase4_df = phase4_df[phase4_df['payer'].isin(valid_payers)].copy()
        
        # CRITICAL: Handle allowed_amount properly
        # Convert "$ -" to 0 to indicate personal expense
        phase4_df['amount'] = phase4_df['amount'].apply(lambda x: 
            0 if (pd.isna(x) or str(x).strip() in ['$ -', '$-', '-']) 
            else float(x)
        )
        
        # Add source
        phase4_df['source'] = 'Consolidated_Expense_History'
        phase4_df['has_manual_annotation'] = phase4_df['manual_notes'].notna()
        
        self.phase4_transactions = phase4_df
        logger.info(f"Loaded {len(phase4_df)} Phase 4 transactions")
        logger.info(f"Transactions with manual annotations: {phase4_df['has_manual_annotation'].sum()}")
        
        # Log some examples of manual annotations
        annotated = phase4_df[phase4_df['has_manual_annotation']]
        if not annotated.empty:
            logger.info("\nExamples of manual annotations found:")
            for idx, row in annotated.head(5).iterrows():
                logger.info(f"  - {row['description']}: {row['manual_notes']}")
                
        return phase4_df
        
    def load_phase5_data(self):
        """Load Phase 5 data from raw bank sources (post-baseline)."""
        logger.info("\nLoading Phase 5 data (Oct 1-31, 2024) from bank sources...")
        
        all_dfs = []
        
        # Load Ryan's data
        ryan_df = self._load_ryan_bank_data()
        if not ryan_df.empty:
            all_dfs.append(ryan_df)
            
        # Load Jordyn's data
        jordyn_df = self._load_jordyn_bank_data()
        if not jordyn_df.empty:
            all_dfs.append(jordyn_df)
            
        if all_dfs:
            # Combine all Phase 5 data
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Filter to Phase 5 date range
            mask = (combined_df['date'] >= self.phase5_start) & (combined_df['date'] <= self.phase5_end)
            phase5_df = combined_df[mask].copy()
            
            # Add flag for needing classification
            phase5_df['needs_classification'] = True
            phase5_df['manual_notes'] = ''
            
            self.phase5_transactions = phase5_df
            logger.info(f"Loaded {len(phase5_df)} Phase 5 transactions requiring classification")
            
            return phase5_df
        else:
            return pd.DataFrame()
            
    def _load_ryan_bank_data(self):
        """Load Ryan's bank data from Monarch Money."""
        file_path = "new_raw/BALANCE_RZ_MonarchMoney_Ledger_20220918-20250718.csv"
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df = df.rename(columns={
                'Date': 'date',
                'Merchant': 'description',
                'Amount': 'amount'
            })
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['payer'] = 'Ryan'
            df['source'] = 'Ryan_MonarchMoney'
            df['amount'] = pd.to_numeric(df['amount'].replace('[\\$,]', '', regex=True), errors='coerce')
            
            return df[['date', 'payer', 'description', 'amount', 'source']]
            
        except Exception as e:
            logger.error(f"Error loading Ryan's bank data: {e}")
            return pd.DataFrame()
            
    def _load_jordyn_bank_data(self):
        """Load Jordyn's bank data from multiple sources."""
        all_dfs = []
        
        # Chase
        chase_df = self._load_chase_data()
        if not chase_df.empty:
            all_dfs.append(chase_df)
            
        # Wells Fargo
        wells_df = self._load_wells_fargo_data()
        if not wells_df.empty:
            all_dfs.append(wells_df)
            
        if all_dfs:
            return pd.concat(all_dfs, ignore_index=True)
        else:
            return pd.DataFrame()
            
    def _load_chase_data(self):
        """Load Jordyn's Chase data."""
        file_path = "new_raw/BALANCE_JG_Chase_6173_Ledger_20231215-20250313.csv"
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df = df.rename(columns={
                'Trans. Date': 'date',
                'Description': 'description',
                'Amount': 'amount'
            })
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['payer'] = 'Jordyn'
            df['source'] = 'Jordyn_Chase'
            
            # Handle encoding issues
            df['amount'] = df['amount'].replace('[\\$,�]', '', regex=True)
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            df['amount'] = df['amount'].abs()
            
            return df[['date', 'payer', 'description', 'amount', 'source']]
            
        except Exception as e:
            logger.error(f"Error loading Jordyn's Chase data: {e}")
            return pd.DataFrame()
            
    def _load_wells_fargo_data(self):
        """Load Jordyn's Wells Fargo data."""
        file_path = "new_raw/BALANCE_JG_WellsFargo_4296_Transactions_20240417-20251231.csv"
        
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            df = df.rename(columns={
                'Trans. Date': 'date',
                'Description': 'description',
                'Amount': 'amount'
            })
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            df['payer'] = 'Jordyn'
            df['source'] = 'Jordyn_WellsFargo'
            df['amount'] = pd.to_numeric(df['amount'].replace('[\\$,]', '', regex=True), errors='coerce').abs()
            
            return df[['date', 'payer', 'description', 'amount', 'source']]
            
        except Exception as e:
            logger.error(f"Error loading Jordyn's Wells Fargo data: {e}")
            return pd.DataFrame()
            
    def classify_phase5_transaction(self, row):
        """
        Classify a Phase 5 transaction that doesn't have manual annotations.
        
        This implements the critical mechanism for post-baseline classification.
        In a real system, this would be interactive or use a rules engine.
        """
        desc_lower = row['description'].lower() if pd.notna(row['description']) else ''
        
        # Check classification cache first
        cache_key = f"{row['date']}_{row['description']}_{row['amount']}"
        if cache_key in self.classification_cache:
            return self.classification_cache[cache_key]
            
        # Auto-classify obvious categories
        # Rent
        if any(keyword in desc_lower for keyword in ['rent', 'san palmas', '7755 e thomas']):
            classification = {
                'category': 'rent',
                'action': 'shared',
                'notes': 'Auto-classified as rent'
            }
            
        # Zelle settlements
        elif 'zelle' in desc_lower and ('to ryan' in desc_lower or 'from jordyn' in desc_lower):
            classification = {
                'category': 'zelle',
                'action': 'settlement',
                'notes': 'Zelle settlement between Ryan and Jordyn'
            }
            
        # Personal expenses (credit card payments, etc.)
        elif any(keyword in desc_lower for keyword in [
            'autopay', 'payment thank you', 'credit card', 'apple card',
            'spotify', 'netflix', 'hulu', 'gym membership'
        ]):
            classification = {
                'category': 'personal',
                'action': 'personal',
                'notes': 'Auto-classified as personal expense'
            }
            
        # Income
        elif any(keyword in desc_lower for keyword in [
            'direct deposit', 'payroll', 'interest', 'dividend', 'refund'
        ]):
            classification = {
                'category': 'income',
                'action': 'income',
                'notes': 'Auto-classified as income'
            }
            
        # Default: shared expense needing review
        else:
            # In a real system, this would prompt for user input
            # For now, we'll mark as shared expense but flag for review
            classification = {
                'category': 'expense',
                'action': 'shared',
                'notes': 'Requires manual classification - defaulted to shared expense',
                'needs_review': True
            }
            self.statistics['phase5']['manual_classified'] += 1
            
        # Cache the classification
        self.classification_cache[cache_key] = classification
        return classification
        
    def process_phase4_transaction(self, idx, row):
        """Process a Phase 4 transaction with manual annotations."""
        audit_id = len(self.audit_entries) + 1
        
        # Skip if no amount (but handle 0 as personal expense below)
        if pd.isna(row['amount']):
            return
            
        # CRITICAL: Handle allowed_amount = 0 as personal expense
        if row['amount'] == 0:
            # This is a personal expense (allowed_amount was "$ -")
            entry = {
                'audit_id': audit_id,
                'date': row['date'].strftime('%Y-%m-%d'),
                'source': row.get('source', 'Unknown'),
                'payer': row['payer'],
                'description': row['description'],
                'amount': 0,  # No shared amount
                'manual_notes': row.get('manual_notes', 'Personal expense (allowed = $ -)'),
                'phase': 'phase4',
                'category': 'personal',
                'action': f'personal_{row["payer"].lower()}',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'notes': f'Personal expense for {row["payer"]} (allowed_amount = $ -)'
            }
            self.audit_entries.append(entry)
            self.statistics['phase4']['by_category']['personal'] = \
                self.statistics['phase4']['by_category'].get('personal', 0) + 1
            self.statistics['phase4']['total'] += 1
            return
            
        # Get manual notes if available
        manual_notes = row.get('manual_notes', '')
        if pd.isna(manual_notes):
            manual_notes = ''
        else:
            manual_notes = str(manual_notes)
        
        # Use description decoder with BOTH description and manual notes
        # The decoder will prioritize manual notes for special patterns
        description = str(row['description']) if pd.notna(row['description']) else ''
        combined_description = f"{description} {manual_notes}".strip() if manual_notes else description
        
        # Decode the transaction
        result = self.decoder.decode_transaction(
            combined_description,
            Decimal(str(row['amount'])),
            row['payer']
        )
        
        # Track special annotations
        if manual_notes:
            if '2x to calculate' in manual_notes.lower():
                self.statistics['special_annotations']['2x_to_calculate'] += 1
            if any(word in manual_notes.lower() for word in ['gift', 'birthday', 'christmas']):
                self.statistics['special_annotations']['gifts'] += 1
            if '100%' in manual_notes:
                self.statistics['special_annotations']['personal_100'] += 1
            if any(word in manual_notes.lower() for word in ['remove', 'exclude', 'deduct']):
                self.statistics['special_annotations']['exclusions'] += 1
                
        # Process based on decoder result
        self._process_decoded_transaction(row, result, audit_id, 'phase4')
        
    def process_phase5_transaction(self, idx, row):
        """Process a Phase 5 transaction requiring classification."""
        audit_id = len(self.audit_entries) + 1
        
        # Skip if no amount
        if pd.isna(row['amount']) or row['amount'] == 0:
            return
            
        # Get classification for this transaction
        classification = self.classify_phase5_transaction(row)
        
        # Create a decoder-compatible result based on classification
        if classification['action'] == 'settlement':
            # Zelle settlement
            self._process_settlement(row, audit_id)
        elif classification['action'] == 'personal':
            # Personal expense
            result = {
                'action': f"personal_{row['payer'].lower()}",
                'reason': classification['notes']
            }
            self._process_decoded_transaction(row, result, audit_id, 'phase5')
        elif classification['action'] == 'income':
            # Income
            result = {
                'action': 'personal_' + row['payer'].lower(),
                'reason': 'Income - not shared'
            }
            self._process_decoded_transaction(row, result, audit_id, 'phase5')
        else:
            # Shared expense (default 50/50)
            result = {
                'action': 'split',
                'payer_share': row['amount'] / 2,
                'other_share': row['amount'] / 2,
                'reason': classification['notes']
            }
            self._process_decoded_transaction(row, result, audit_id, 'phase5')
            
        # Mark for review if needed
        if classification.get('needs_review', False):
            self.manual_review.append({
                'audit_id': audit_id,
                'date': row['date'],
                'description': row['description'],
                'amount': row['amount'],
                'classification': classification,
                'reason': 'Needs manual classification confirmation'
            })
            
    def _process_decoded_transaction(self, row, result, audit_id, phase):
        """Process a transaction based on decoder result."""
        entry = {
            'audit_id': audit_id,
            'date': row['date'].strftime('%Y-%m-%d'),
            'source': row.get('source', 'Unknown'),
            'payer': row['payer'],
            'description': row['description'],
            'amount': float(row['amount']),
            'manual_notes': row.get('manual_notes', ''),
            'phase': phase
        }
        
        action = result['action']
        
        # Update statistics
        self.statistics[phase]['by_category'][action] = \
            self.statistics[phase]['by_category'].get(action, 0) + 1
        self.statistics[phase]['total'] += 1
        
        # Process based on action
        if action == 'manual_review':
            entry.update({
                'category': 'manual_review',
                'action': 'manual_review',
                'ryan_share': 0.0,
                'jordyn_share': 0.0,
                'balance_change': 0.0,
                'notes': f"Manual review required: {result.get('reason', 'Unknown')}"
            })
            self.manual_review.append(entry)
            
        elif action == 'gift':
            # Gifts - payer covers all
            entry.update({
                'category': 'gift',
                'action': 'gift',
                'ryan_share': float(row['amount']) if row['payer'] == 'Ryan' else 0.0,
                'jordyn_share': float(row['amount']) if row['payer'] == 'Jordyn' else 0.0,
                'balance_change': 0.0,
                'notes': f"Gift expense - {row['payer']} covers all"
            })
            
        elif action in ['personal_ryan', 'personal_jordyn']:
            # Personal expenses
            person = 'Ryan' if 'ryan' in action else 'Jordyn'
            entry.update({
                'category': 'personal',
                'action': action,
                'ryan_share': float(row['amount']) if person == 'Ryan' else 0.0,
                'jordyn_share': float(row['amount']) if person == 'Jordyn' else 0.0,
                'balance_change': 0.0,
                'notes': f"Personal expense for {person}"
            })
            
        elif action == 'full_reimbursement':
            # Full reimbursement (2x to calculate pattern)
            if row['payer'] == 'Ryan':
                # Ryan paid, Jordyn owes full
                self.engine.post_expense(
                    date=row['date'],
                    payer='Ryan',
                    ryan_share=Decimal('0'),
                    jordyn_share=Decimal(str(row['amount'])),
                    description=row['description']
                )
                balance_change = -float(row['amount'])
                entry.update({
                    'category': 'expense',
                    'action': 'full_reimbursement',
                    'ryan_share': 0.0,
                    'jordyn_share': float(row['amount']),
                    'balance_change': balance_change,
                    'notes': 'Full reimbursement - Ryan paid, Jordyn owes 100%'
                })
            else:
                # Jordyn paid, Ryan owes full
                self.engine.post_expense(
                    date=row['date'],
                    payer='Jordyn',
                    ryan_share=Decimal(str(row['amount'])),
                    jordyn_share=Decimal('0'),
                    description=row['description']
                )
                balance_change = float(row['amount'])
                entry.update({
                    'category': 'expense',
                    'action': 'full_reimbursement',
                    'ryan_share': float(row['amount']),
                    'jordyn_share': 0.0,
                    'balance_change': balance_change,
                    'notes': 'Full reimbursement - Jordyn paid, Ryan owes 100%'
                })
                
        else:
            # Split expense (default or custom split)
            if 'payer_share' in result and 'other_share' in result:
                if row['payer'] == 'Ryan':
                    ryan_share = Decimal(str(result['payer_share']))
                    jordyn_share = Decimal(str(result['other_share']))
                else:
                    ryan_share = Decimal(str(result['other_share']))
                    jordyn_share = Decimal(str(result['payer_share']))
            else:
                # Default 50/50
                ryan_share = Decimal(str(row['amount'])) / 2
                jordyn_share = Decimal(str(row['amount'])) / 2
                
            self.engine.post_expense(
                date=row['date'],
                payer=row['payer'],
                ryan_share=ryan_share,
                jordyn_share=jordyn_share,
                description=row['description']
            )
            
            # Calculate balance change
            if row['payer'] == 'Ryan':
                balance_change = -float(jordyn_share)
            else:
                balance_change = float(ryan_share)
                
            entry.update({
                'category': 'expense',
                'action': 'split',
                'ryan_share': float(ryan_share),
                'jordyn_share': float(jordyn_share),
                'balance_change': balance_change,
                'notes': f"Split expense - {result.get('reason', 'Default 50/50 split')}"
            })
            
        # Get current balance
        current_status, current_balance = self.get_current_balance()
        entry['running_balance'] = float(current_balance)
        entry['who_owes_whom'] = current_status
        
        self.audit_entries.append(entry)
        
    def _process_settlement(self, row, audit_id):
        """Process a Zelle settlement."""
        # Zelle from Jordyn to Ryan
        self.engine.post_settlement(
            date=row['date'],
            from_person='Jordyn',
            to_person='Ryan',
            amount=Decimal(str(row['amount']))
        )
        
        entry = {
            'audit_id': audit_id,
            'date': row['date'].strftime('%Y-%m-%d'),
            'source': row.get('source', 'Unknown'),
            'payer': row['payer'],
            'description': row['description'],
            'amount': float(row['amount']),
            'category': 'settlement',
            'action': 'settlement',
            'ryan_share': 0.0,
            'jordyn_share': float(row['amount']),
            'balance_change': float(row['amount']),
            'notes': 'Zelle settlement from Jordyn to Ryan',
            'phase': 'phase5'
        }
        
        current_status, current_balance = self.get_current_balance()
        entry['running_balance'] = float(current_balance)
        entry['who_owes_whom'] = current_status
        
        self.audit_entries.append(entry)
        self.statistics['phase5']['total'] += 1
        
    def get_current_balance(self) -> Tuple[str, Decimal]:
        """Get current balance status."""
        net_position = self.engine.ryan_receivable - self.engine.jordyn_receivable
        
        if net_position > 0:
            return "Jordyn owes Ryan", abs(net_position)
        elif net_position < 0:
            return "Ryan owes Jordyn", abs(net_position)
        else:
            return "Balanced", Decimal('0.00')
            
    def initialize_with_baseline(self):
        """Initialize the accounting engine with Phase 4 ending balance."""
        logger.info(f"\nInitializing with Phase 4 baseline...")
        logger.info(f"Starting balance: ${self.starting_balance} (Jordyn owes Ryan)")
        
        # Set up the baseline in the accounting engine
        self.engine.ryan_receivable = self.starting_balance
        self.engine.jordyn_payable = self.starting_balance
        
        # Add baseline entry to audit trail
        self.audit_entries.append({
            'audit_id': 0,
            'date': BASELINE_DATE.strftime('%Y-%m-%d'),
            'source': 'Phase 4 Baseline',
            'payer': 'Initial Balance',
            'description': 'Phase 4 ending balance (manually reconciled through Sept 30)',
            'amount': float(self.starting_balance),
            'category': 'baseline',
            'action': 'baseline',
            'ryan_share': float(self.starting_balance),
            'jordyn_share': 0.0,
            'balance_change': 0.0,
            'running_balance': float(self.starting_balance),
            'who_owes_whom': 'Jordyn owes Ryan',
            'notes': 'Baseline from consolidated expense history with manual annotations',
            'phase': 'baseline'
        })
        
    def generate_reports(self):
        """Generate comprehensive reports."""
        logger.info("\nGenerating enhanced reconciliation reports...")
        
        # Create output directory
        output_dir = Path("output/full_2024_enhanced")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save audit trail
        audit_df = pd.DataFrame(self.audit_entries)
        audit_file = output_dir / "enhanced_audit_trail.csv"
        audit_df.to_csv(audit_file, index=False)
        logger.info(f"Saved audit trail: {audit_file}")
        
        # Generate summary
        final_status, final_balance = self.get_current_balance()
        summary = {
            'reconciliation_info': {
                'version': '2.0.0 - Enhanced with manual annotations',
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'phase4': {
                'period': f"{self.phase4_start.strftime('%Y-%m-%d')} to {self.phase4_end.strftime('%Y-%m-%d')}",
                'source': 'Consolidated Expense History (with manual annotations)',
                'transactions': self.statistics['phase4']['total'],
                'categories': self.statistics['phase4']['by_category']
            },
            'phase5': {
                'period': f"{self.phase5_start.strftime('%Y-%m-%d')} to {self.phase5_end.strftime('%Y-%m-%d')}",
                'source': 'Raw bank data (classified)',
                'transactions': self.statistics['phase5']['total'],
                'manual_classifications': self.statistics['phase5']['manual_classified'],
                'categories': self.statistics['phase5']['by_category']
            },
            'special_annotations_processed': self.statistics['special_annotations'],
            'baseline': {
                'date': BASELINE_DATE.strftime('%Y-%m-%d'),
                'amount': float(PHASE_4_ENDING_BALANCE),
                'status': 'Jordyn owes Ryan'
            },
            'final_balance': {
                'amount': float(final_balance),
                'status': final_status
            },
            'manual_review_needed': len(self.manual_review)
        }
        
        summary_file = output_dir / "enhanced_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Saved summary: {summary_file}")
        
        # Generate human-readable report
        report_file = output_dir / "enhanced_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("ENHANCED FULL 2024 FINANCIAL RECONCILIATION REPORT\n")
            f.write("="*80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Version: 2.0.0 - With Manual Annotations\n")
            f.write("="*80 + "\n\n")
            
            f.write("RECONCILIATION APPROACH\n")
            f.write("-"*40 + "\n")
            f.write("Phase 4 (Jan 1 - Sept 30): Consolidated expense history with manual annotations\n")
            f.write("Phase 5 (Oct 1 - Oct 31): Raw bank data with classification mechanism\n\n")
            
            f.write("BASELINE\n")
            f.write("-"*40 + "\n")
            f.write(f"Date: {BASELINE_DATE.strftime('%B %d, %Y')}\n")
            f.write(f"Amount: ${PHASE_4_ENDING_BALANCE:.2f}\n")
            f.write("Status: Jordyn owes Ryan\n")
            f.write("Source: Manually reconciled Google Sheets data\n\n")
            
            f.write("SPECIAL ANNOTATIONS PROCESSED\n")
            f.write("-"*40 + "\n")
            f.write(f"'2x to calculate' patterns: {self.statistics['special_annotations']['2x_to_calculate']}\n")
            f.write(f"Gift transactions: {self.statistics['special_annotations']['gifts']}\n")
            f.write(f"100% personal expenses: {self.statistics['special_annotations']['personal_100']}\n")
            f.write(f"Exclusion patterns: {self.statistics['special_annotations']['exclusions']}\n\n")
            
            f.write("PHASE 4 SUMMARY (Pre-baseline)\n")
            f.write("-"*40 + "\n")
            f.write(f"Transactions: {self.statistics['phase4']['total']}\n")
            f.write("Categories:\n")
            for cat, count in sorted(self.statistics['phase4']['by_category'].items()):
                f.write(f"  {cat}: {count}\n")
            f.write("\n")
            
            f.write("PHASE 5 SUMMARY (Post-baseline)\n")
            f.write("-"*40 + "\n")
            f.write(f"Transactions: {self.statistics['phase5']['total']}\n")
            f.write(f"Required manual classification: {self.statistics['phase5']['manual_classified']}\n")
            f.write("Categories:\n")
            for cat, count in sorted(self.statistics['phase5']['by_category'].items()):
                f.write(f"  {cat}: {count}\n")
            f.write("\n")
            
            f.write("FINAL BALANCE\n")
            f.write("-"*40 + "\n")
            f.write(f"Amount: ${final_balance:.2f}\n")
            f.write(f"Status: {final_status}\n\n")
            
            if self.manual_review:
                f.write("ITEMS REQUIRING REVIEW\n")
                f.write("-"*40 + "\n")
                for item in self.manual_review[:5]:
                    f.write(f"\n{item['date']} - {item['description']}")
                    f.write(f"\n  Amount: ${item['amount']:.2f}")
                    f.write(f"\n  Reason: {item.get('reason', 'Unknown')}\n")
                if len(self.manual_review) > 5:
                    f.write(f"\n... and {len(self.manual_review) - 5} more items\n")
                    
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
            
        logger.info(f"Saved report: {report_file}")
        
        # Save manual review items
        if self.manual_review:
            review_df = pd.DataFrame(self.manual_review)
            review_file = output_dir / "manual_review_items.csv"
            review_df.to_csv(review_file, index=False)
            logger.info(f"Saved manual review items: {review_file}")
            
    def run_reconciliation(self):
        """Execute the enhanced reconciliation."""
        logger.info("="*80)
        logger.info("STARTING ENHANCED FULL 2024 RECONCILIATION")
        logger.info("="*80)
        
        # Initialize with baseline
        self.initialize_with_baseline()
        
        # Process Phase 4 (with manual annotations)
        phase4_data = self.load_phase4_data()
        if not phase4_data.empty:
            logger.info("\nProcessing Phase 4 transactions...")
            for idx, row in phase4_data.iterrows():
                if idx % 50 == 0 and idx > 0:
                    logger.info(f"  Processed {idx} Phase 4 transactions...")
                self.process_phase4_transaction(idx, row)
                
        # Get Phase 4 ending balance
        phase4_status, phase4_balance = self.get_current_balance()
        logger.info(f"\nPhase 4 complete!")
        logger.info(f"Calculated ending balance: ${phase4_balance:.2f} ({phase4_status})")
        logger.info(f"Expected ending balance: ${PHASE_4_ENDING_BALANCE:.2f}")
        
        if abs(phase4_balance - PHASE_4_ENDING_BALANCE) > Decimal('0.01'):
            logger.warning(f"WARNING: Phase 4 balance mismatch! Difference: ${abs(phase4_balance - PHASE_4_ENDING_BALANCE):.2f}")
            
        # Process Phase 5 (raw bank data)
        phase5_data = self.load_phase5_data()
        if not phase5_data.empty:
            logger.info("\nProcessing Phase 5 transactions...")
            for idx, row in phase5_data.iterrows():
                if idx % 20 == 0 and idx > 0:
                    logger.info(f"  Processed {idx} Phase 5 transactions...")
                self.process_phase5_transaction(idx, row)
                
        # Generate reports
        self.generate_reports()
        
        # Final summary
        final_status, final_balance = self.get_current_balance()
        logger.info("\n" + "="*80)
        logger.info("RECONCILIATION COMPLETE")
        logger.info("="*80)
        logger.info(f"Phase 4 Transactions: {self.statistics['phase4']['total']}")
        logger.info(f"Phase 5 Transactions: {self.statistics['phase5']['total']}")
        logger.info(f"Special Annotations Processed:")
        for key, count in self.statistics['special_annotations'].items():
            if count > 0:
                logger.info(f"  - {key}: {count}")
        logger.info(f"Final Balance: ${final_balance:.2f}")
        logger.info(f"Status: {final_status}")
        logger.info("="*80)


def main():
    """Execute enhanced reconciliation."""
    reconciler = EnhancedFull2024Reconciler()
    reconciler.run_reconciliation()


if __name__ == "__main__":
    main()