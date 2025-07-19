#!/usr/bin/env python3
"""
Master Financial Reconciliation Engine - Focused on 100% Accuracy

This engine implements accounting best practices with:
1. Double-entry validation
2. Manual review flagging for ambiguous cases
3. Comprehensive audit trail
4. Business rule externalization
5. Exception-based processing for edge cases
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import logging

# Configure logging for audit trail
# Note: This will create an 'output' directory for the log file
Path('output').mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('output/reconciliation_audit.log'),
        logging.StreamHandler()
    ]
)

@dataclass
class ReconciliationConfig:
    """Externalized business rules for reconciliation."""
    
    # Person allocation rules
    ryan_rent_percentage: Decimal = Decimal('0.43')
    jordyn_rent_percentage: Decimal = Decimal('0.57')
    expense_split_default: Decimal = Decimal('0.50')  # 50/50 split
    
    # Validation thresholds
    max_single_expense: Decimal = Decimal('5000.00')
    min_valid_amount: Decimal = Decimal('0.01')
    rounding_tolerance: Decimal = Decimal('0.01')
    
    # Manual review triggers
    manual_review_keywords: List[str] = None
    complex_calculation_patterns: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.manual_review_keywords is None:
            self.manual_review_keywords = [
                'discuss further', 'verify', 'check', 'lost', 
                'where is', '???', 'reassess', 'monitor'
            ]
        
        if self.complex_calculation_patterns is None:
            self.complex_calculation_patterns = {
                'double_charge': ['2x to calculate', '2 x to calculate', 'double to calculate'],
                'gift_adjustment': ['birthday present', 'gift', 'present portion'],
                'split_payment': ['split', 'ebt', 'credit card /'],
                'exclusion': ['remove', 'exclude', 'deduct', 'minus'],
                'percentage_allocation': [r'100%\s*(ryan|jordyn)', r'(\d+)%\s*(ryan|jordyn)']
            }

class FinancialAmount:
    """Handles all currency operations with proper decimal precision."""
    
    def __init__(self, value: Any):
        """Initialize with string, float, or Decimal value."""
        if pd.isna(value) or value == '' or str(value).strip() == '':
            self.value = Decimal('0.00')
            self.is_valid = False
        else:
            try:
                # Clean the value
                cleaned = str(value).strip()
                cleaned = re.sub(r'[$,\s]', '', cleaned)
                
                # Handle parentheses for negative
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    cleaned = '-' + cleaned[1:-1]
                
                # Handle quotes
                cleaned = cleaned.strip('"\'')
                
                # Convert to Decimal
                self.value = Decimal(cleaned).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                self.is_valid = True
                
            except Exception as e:
                logging.warning(f"Failed to parse amount '{value}': {e}")
                self.value = Decimal('0.00')
                self.is_valid = False
    
    def __add__(self, other):
        if isinstance(other, FinancialAmount):
            return FinancialAmount(str(self.value + other.value))
        return FinancialAmount(str(self.value + Decimal(str(other))))
    
    def __sub__(self, other):
        if isinstance(other, FinancialAmount):
            return FinancialAmount(str(self.value - other.value))
        return FinancialAmount(str(self.value - Decimal(str(other))))
    
    def __mul__(self, other):
        return FinancialAmount(str(self.value * Decimal(str(other))))
    
    def __truediv__(self, other):
        if Decimal(str(other)) == 0:
            return FinancialAmount('0.00')
        return FinancialAmount(str(self.value / Decimal(str(other))))
    
    def __str__(self):
        return f"${self.value:,.2f}"
    
    def __float__(self):
        return float(self.value)

@dataclass
class ReconciliationEntry:
    """Represents a single reconciliation entry with full audit trail."""
    
    entry_id: str
    source_file: str
    row_index: int
    entry_type: str  # 'expense', 'rent', 'zelle'
    date: datetime
    person: str
    amount: FinancialAmount
    description: str
    
    # Calculated fields
    allocated_to_ryan: FinancialAmount = None
    allocated_to_jordyn: FinancialAmount = None
    requires_manual_review: bool = False
    manual_review_reasons: List[str] = None
    calculation_notes: List[str] = None
    validation_status: str = 'pending'  # pending, validated, error
    validation_errors: List[str] = None
    
    # Audit fields
    processing_timestamp: datetime = None
    processing_version: str = "1.0"
    
    def __post_init__(self):
        if self.manual_review_reasons is None:
            self.manual_review_reasons = []
        if self.calculation_notes is None:
            self.calculation_notes = []
        if self.validation_errors is None:
            self.validation_errors = []
        if self.processing_timestamp is None:
            self.processing_timestamp = datetime.now()

class MasterReconciliationEngine:
    """Master engine for financial reconciliation with 100% accuracy focus."""
    
    def __init__(self, config: ReconciliationConfig = None):
        self.config = config or ReconciliationConfig()
        self.entries: List[ReconciliationEntry] = []
        self.manual_review_queue: List[ReconciliationEntry] = []
        self.audit_trail: List[Dict[str, Any]] = []
        
        # Pre-compile regex patterns for performance
        self.compiled_patterns = {}
        for pattern_type, patterns in self.config.complex_calculation_patterns.items():
            self.compiled_patterns[pattern_type] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]
    
    def process_expense_entry(self, row: pd.Series, row_index: int, source_file: str) -> ReconciliationEntry:
        """Process a single expense entry with full validation."""
        
        # Create base entry
        entry = ReconciliationEntry(
            entry_id=f"EXP_{row_index:06d}",
            source_file=source_file,
            row_index=row_index,
            entry_type='expense',
            date=self._parse_date(row.get('date')),
            person=self._normalize_person(row.get('person')),
            amount=FinancialAmount(row.get('actual_amount')),
            description=str(row.get('description', '')) + ' ' + str(row.get('merchant_description', ''))
        )
        
        # Check for complex calculations
        self._analyze_complex_calculations(entry)
        
        # Apply expense allocation rules
        self._apply_expense_allocation(entry)
        
        # Validate entry
        self._validate_entry(entry)
        
        return entry
    
    def process_rent_entry(self, row: pd.Series, row_index: int, source_file: str) -> ReconciliationEntry:
        """Process a rent allocation entry."""
        
        # For rent, we need to create two entries - one for each person
        entries = []
        
        # Ryan's portion
        ryan_entry = ReconciliationEntry(
            entry_id=f"RENT_RYAN_{row_index:06d}",
            source_file=source_file,
            row_index=row_index,
            entry_type='rent',
            date=self._parse_date(row.get('month')),
            person='Ryan',
            amount=FinancialAmount(row.get('ryan_amount')),
            description=f"Rent allocation for {row.get('month')}"
        )
        ryan_entry.allocated_to_ryan = ryan_entry.amount
        ryan_entry.allocated_to_jordyn = FinancialAmount('0.00')
        entries.append(ryan_entry)
        
        # Jordyn's portion
        jordyn_entry = ReconciliationEntry(
            entry_id=f"RENT_JORDYN_{row_index:06d}",
            source_file=source_file,
            row_index=row_index,
            entry_type='rent',
            date=self._parse_date(row.get('month')),
            person='Jordyn',
            amount=FinancialAmount(row.get('jordyn_amount')),
            description=f"Rent allocation for {row.get('month')}"
        )
        jordyn_entry.allocated_to_ryan = FinancialAmount('0.00')
        jordyn_entry.allocated_to_jordyn = jordyn_entry.amount
        entries.append(jordyn_entry)
        
        # Validate rent split
        total_rent = FinancialAmount(row.get('gross_total'))
        calculated_total = ryan_entry.amount + jordyn_entry.amount
        
        if abs(total_rent.value - calculated_total.value) > self.config.rounding_tolerance:
            for entry in entries:
                entry.validation_errors.append(
                    f"Rent split validation failed: {total_rent} != {calculated_total}"
                )
                entry.requires_manual_review = True
        
        return entries
    
    def process_zelle_entry(self, row: pd.Series, row_index: int, source_file: str) -> ReconciliationEntry:
        """Process a Zelle payment entry."""
        
        entry = ReconciliationEntry(
            entry_id=f"ZELLE_{row_index:06d}",
            source_file=source_file,
            row_index=row_index,
            entry_type='zelle',
            date=self._parse_date(row.get('date')),
            person='Jordyn',  # All Zelle payments are from Jordyn
            amount=FinancialAmount(row.get('amount')),
            description=row.get('original_statement', '')
        )
        
        # Zelle payments are credits from Jordyn to Ryan
        entry.allocated_to_ryan = entry.amount  # Ryan receives
        entry.allocated_to_jordyn = FinancialAmount(str(-entry.amount.value))  # Jordyn pays
        
        # Validate Zelle payment
        if 'JORDYN' not in str(row.get('original_statement', '')).upper():
            entry.validation_errors.append("Zelle payment missing Jordyn reference")
            entry.requires_manual_review = True
        
        return entry
    
    def _analyze_complex_calculations(self, entry: ReconciliationEntry):
        """Analyze entry for complex calculation patterns."""
        
        description = entry.description.lower()
        
        # Check for double charge pattern
        for pattern in self.compiled_patterns.get('double_charge', []):
            if pattern.search(description):
                entry.calculation_notes.append("Contains 2x calculation multiplier")
                entry.requires_manual_review = True
                entry.manual_review_reasons.append("Complex calculation: 2x multiplier")
                
                # If budgeted amount exists, check if it's actually 2x
                # This would need to be passed in from the row data
                
        # Check for gift adjustments
        for pattern in self.compiled_patterns.get('gift_adjustment', []):
            if pattern.search(description):
                entry.calculation_notes.append("Contains gift/present adjustment")
                entry.requires_manual_review = True
                entry.manual_review_reasons.append("Gift allocation requires review")
        
        # Check for split payments
        for pattern in self.compiled_patterns.get('split_payment', []):
            if pattern.search(description):
                entry.calculation_notes.append("Split payment detected")
                entry.requires_manual_review = True
                entry.manual_review_reasons.append("Split payment requires verification")
        
        # Check for manual review keywords
        for keyword in self.config.manual_review_keywords:
            if keyword in description:
                entry.requires_manual_review = True
                entry.manual_review_reasons.append(f"Contains review keyword: {keyword}")
    
    def _apply_expense_allocation(self, entry: ReconciliationEntry):
        """Apply expense allocation rules based on person and description."""
        
        # Check for explicit allocation in description
        description = entry.description.lower()
        
        # Look for 100% allocation patterns
        if '100% jordyn' in description:
            entry.allocated_to_jordyn = entry.amount
            entry.allocated_to_ryan = FinancialAmount('0.00')
            entry.calculation_notes.append("100% allocated to Jordyn per description")
            return
        
        if '100% ryan' in description:
            entry.allocated_to_ryan = entry.amount
            entry.allocated_to_jordyn = FinancialAmount('0.00')
            entry.calculation_notes.append("100% allocated to Ryan per description")
            return
        
        # Default 50/50 split for shared expenses
        if entry.person in ['Ryan', 'Jordyn']:
            split_amount = entry.amount * self.config.expense_split_default
            entry.allocated_to_ryan = split_amount
            entry.allocated_to_jordyn = split_amount
            entry.calculation_notes.append(f"Applied default {self.config.expense_split_default*100}% split")
        else:
            # Unknown person - flag for review
            entry.requires_manual_review = True
            entry.manual_review_reasons.append(f"Unknown person: {entry.person}")
    
    def _validate_entry(self, entry: ReconciliationEntry):
        """Validate entry against business rules."""
        
        # Amount validation
        if not entry.amount.is_valid:
            entry.validation_errors.append("Invalid amount format")
            entry.validation_status = 'error'
        elif entry.amount.value <= 0:
            entry.validation_errors.append("Non-positive amount")
            entry.requires_manual_review = True
        elif entry.amount.value > self.config.max_single_expense:
            entry.validation_errors.append(f"Amount exceeds maximum: {entry.amount}")
            entry.requires_manual_review = True
        
        # Date validation
        if not entry.date:
            entry.validation_errors.append("Invalid or missing date")
            entry.validation_status = 'error'
        
        # Person validation
        if entry.person not in ['Ryan', 'Jordyn']:
            entry.validation_errors.append(f"Invalid person: {entry.person}")
            entry.requires_manual_review = True
        
        # Set final validation status
        if entry.validation_errors:
            entry.validation_status = 'error' if any('Invalid' in e for e in entry.validation_errors) else 'warning'
        else:
            entry.validation_status = 'validated'
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date with multiple format support."""
        if pd.isna(date_value) or str(date_value).strip() == '':
            return None
        
        date_str = str(date_value).strip()
        
        # Try multiple date formats
        formats = [
            '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%m/%d/%y',
            '%b-%y', '%B-%y', '%Y-%m', '%m-%Y'
        ]
        
        for fmt in formats:
            try:
                # Handle month-only formats by adding day 1
                if fmt in ['%b-%y', '%B-%y', '%Y-%m', '%m-%Y']:
                    return datetime.strptime(date_str, fmt).replace(day=1)
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas parser
        try:
            return pd.to_datetime(date_str)
        except:
            logging.warning(f"Failed to parse date: {date_str}")
            return None
    
    def _normalize_person(self, person_value: Any) -> str:
        """Normalize person name."""
        if pd.isna(person_value) or str(person_value).strip() == '':
            return 'Unknown'
        
        person = str(person_value).strip().title()
        
        # Handle known variations
        if person in ['Jordyn ', 'Jordyn Expenses']:
            return 'Jordyn'
        
        return person
    
    def generate_reconciliation_report(self) -> Dict[str, Any]:
        """Generate comprehensive reconciliation report with double-entry bookkeeping."""
        
        report = {
            'metadata': {
                'generation_timestamp': datetime.now().isoformat(),
                'total_entries': len(self.entries),
                'manual_review_required': len(self.manual_review_queue),
                'validation_summary': {}
            },
            'account_balances': {
                'ryan': {
                    'debits': Decimal('0.00'),
                    'credits': Decimal('0.00'),
                    'net_balance': Decimal('0.00')
                },
                'jordyn': {
                    'debits': Decimal('0.00'),
                    'credits': Decimal('0.00'), 
                    'net_balance': Decimal('0.00')
                }
            },
            'monthly_summary': {},
            'validation_issues': [],
            'manual_review_items': []
        }
        
        # Process all entries
        for entry in self.entries:
            # Skip invalid entries
            if entry.validation_status == 'error':
                report['validation_issues'].append({
                    'entry_id': entry.entry_id,
                    'errors': entry.validation_errors
                })
                continue
            
            # Add to manual review if needed
            if entry.requires_manual_review:
                report['manual_review_items'].append({
                    'entry_id': entry.entry_id,
                    'date': entry.date.isoformat() if entry.date else None,
                    'amount': str(entry.amount),
                    'description': entry.description,
                    'reasons': entry.manual_review_reasons,
                    'calculation_notes': entry.calculation_notes
                })
            
            # Update account balances (double-entry)
            if entry.allocated_to_ryan:
                if entry.allocated_to_ryan.value > 0:
                    report['account_balances']['ryan']['debits'] += entry.allocated_to_ryan.value
                else:
                    report['account_balances']['ryan']['credits'] += abs(entry.allocated_to_ryan.value)
            
            if entry.allocated_to_jordyn:
                if entry.allocated_to_jordyn.value > 0:
                    report['account_balances']['jordyn']['debits'] += entry.allocated_to_jordyn.value
                else:
                    report['account_balances']['jordyn']['credits'] += abs(entry.allocated_to_jordyn.value)
        
        # Calculate net balances
        for person in ['ryan', 'jordyn']:
            balance = report['account_balances'][person]
            balance['net_balance'] = balance['debits'] - balance['credits']
        
        # Determine who owes whom
        ryan_net = report['account_balances']['ryan']['net_balance']
        jordyn_net = report['account_balances']['jordyn']['net_balance']
        
        # In a balanced system, ryan_net + jordyn_net should equal 0
        imbalance = ryan_net + jordyn_net
        
        report['reconciliation_summary'] = {
            'ryan_net_position': float(ryan_net),
            'jordyn_net_position': float(jordyn_net),
            'system_imbalance': float(imbalance),
            'who_owes_whom': 'Jordyn owes Ryan' if jordyn_net < 0 else 'Ryan owes Jordyn' if ryan_net < 0 else 'Balanced',
            'amount_owed': float(abs(ryan_net))
        }
        
        return report
    
    def save_results(self, output_dir: Path):
        """Save all results with comprehensive audit trail."""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save entries as CSV
        entries_df = pd.DataFrame([
            {
                'entry_id': e.entry_id,
                'source_file': e.source_file,
                'entry_type': e.entry_type,
                'date': e.date.isoformat() if e.date else None,
                'person': e.person,
                'amount': float(e.amount.value),
                'description': e.description,
                'allocated_to_ryan': float(e.allocated_to_ryan.value) if e.allocated_to_ryan else None,
                'allocated_to_jordyn': float(e.allocated_to_jordyn.value) if e.allocated_to_jordyn else None,
                'requires_manual_review': e.requires_manual_review,
                'validation_status': e.validation_status,
                'manual_review_reasons': '; '.join(e.manual_review_reasons),
                'calculation_notes': '; '.join(e.calculation_notes),
                'validation_errors': '; '.join(e.validation_errors)
            }
            for e in self.entries
        ])
        
        entries_df.to_csv(output_dir / 'reconciliation_entries.csv', index=False)
        logging.info(f"Saved {len(entries_df)} entries to reconciliation_entries.csv")
        
        # Save manual review queue
        if self.manual_review_queue:
            review_df = pd.DataFrame([
                {
                    'entry_id': e.entry_id,
                    'date': e.date.isoformat() if e.date else None,
                    'person': e.person,
                    'amount': float(e.amount.value),
                    'description': e.description,
                    'review_reasons': '; '.join(e.manual_review_reasons),
                    'calculation_notes': '; '.join(e.calculation_notes)
                }
                for e in self.manual_review_queue
            ])
            review_df.to_csv(output_dir / 'manual_review_required.csv', index=False)
            logging.info(f"Saved {len(review_df)} entries requiring manual review")
        
        # Generate and save report
        report = self.generate_reconciliation_report()
        with open(output_dir / 'reconciliation_report.json', 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        # Save human-readable summary
        with open(output_dir / 'reconciliation_summary.txt', 'w') as f:
            f.write("FINANCIAL RECONCILIATION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Generated: {report['metadata']['generation_timestamp']}\n")
            f.write(f"Total Entries: {report['metadata']['total_entries']}\n")
            f.write(f"Manual Review Required: {report['metadata']['manual_review_required']}\n\n")
            
            f.write("ACCOUNT BALANCES:\n")
            f.write(f"Ryan Net Position: ${report['reconciliation_summary']['ryan_net_position']:,.2f}\n")
            f.write(f"Jordyn Net Position: ${report['reconciliation_summary']['jordyn_net_position']:,.2f}\n\n")
            
            f.write("RECONCILIATION RESULT:\n")
            f.write(f"{report['reconciliation_summary']['who_owes_whom']}: ")
            f.write(f"${report['reconciliation_summary']['amount_owed']:,.2f}\n\n")
            
            if abs(report['reconciliation_summary']['system_imbalance']) > 0.01:
                f.write(f"WARNING: System imbalance detected: ${report['reconciliation_summary']['system_imbalance']:,.2f}\n")
                f.write("This indicates missing or incorrect entries.\n")

# Example usage function
def process_all_data():
    """Process all normalized CSV files."""
    
    engine = MasterReconciliationEngine()
    
    # Create dummy data directories if they don't exist
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    
    # Load normalized expense data
    expense_file = Path("data/processed/expense_history_normalized.csv")
    if expense_file.exists():
        expenses_df = pd.read_csv(expense_file)
        logging.info(f"Processing {len(expenses_df)} expense entries")
        
        for idx, row in expenses_df.iterrows():
            entry = engine.process_expense_entry(row, idx, str(expense_file))
            engine.entries.append(entry)
            
            if entry.requires_manual_review:
                engine.manual_review_queue.append(entry)
    
    # Load normalized rent data
    rent_file = Path("data/processed/rent_allocation_normalized.csv")
    if rent_file.exists():
        rent_df = pd.read_csv(rent_file)
        logging.info(f"Processing {len(rent_df)} rent entries")
        
        for idx, row in rent_df.iterrows():
            entries = engine.process_rent_entry(row, idx, str(rent_file))
            engine.entries.extend(entries)
            
            for entry in entries:
                if entry.requires_manual_review:
                    engine.manual_review_queue.append(entry)
    
    # Load normalized Zelle data
    zelle_file = Path("data/processed/zelle_payments_normalized.csv")
    if zelle_file.exists():
        zelle_df = pd.read_csv(zelle_file)
        logging.info(f"Processing {len(zelle_df)} Zelle entries")
        
        for idx, row in zelle_df.iterrows():
            entry = engine.process_zelle_entry(row, idx, str(zelle_file))
            engine.entries.append(entry)
            
            if entry.requires_manual_review:
                engine.manual_review_queue.append(entry)
    
    # Save results
    engine.save_results(Path("output/master_reconciliation"))
    
    # Generate report
    report = engine.generate_reconciliation_report()
    
    logging.info("=" * 60)
    logging.info("RECONCILIATION COMPLETE")
    logging.info(f"Total entries processed: {len(engine.entries)}")
    logging.info(f"Entries requiring manual review: {len(engine.manual_review_queue)}")
    logging.info(f"Final balance: {report['reconciliation_summary']['who_owes_whom']} "
                 f"${report['reconciliation_summary']['amount_owed']:,.2f}")
    
    return engine

if __name__ == "__main__":
    process_all_data()
