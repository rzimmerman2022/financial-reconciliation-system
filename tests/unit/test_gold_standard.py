#!/usr/bin/env python3
"""
Comprehensive Test Suite for Gold Standard Reconciliation System
================================================================

This test suite ensures the reconciliation system meets the highest
standards of accuracy, reliability, and compliance with accounting principles.

Test Categories:
1. Unit tests for individual components
2. Integration tests for full workflows
3. Edge case handling
4. Data quality validation
5. Accounting invariant verification
6. Performance benchmarks

Author: Claude (Anthropic)
Date: July 29, 2025
Version: 1.0.0
"""

import unittest
from decimal import Decimal
from datetime import datetime
import pandas as pd
import tempfile
import json
from pathlib import Path

from gold_standard_reconciliation import (
    GoldStandardReconciler, ReconciliationMode, DataQualityIssue
)
from src.accounting_engine import AccountingEngine, TransactionType


class TestAccountingInvariants(unittest.TestCase):
    """Test that accounting invariants are maintained."""
    
    def setUp(self):
        self.engine = AccountingEngine()
    
    def test_initial_state(self):
        """Test engine starts in valid state."""
        self.assertEqual(self.engine.ryan_receivable, Decimal('0'))
        self.assertEqual(self.engine.ryan_payable, Decimal('0'))
        self.assertEqual(self.engine.jordyn_receivable, Decimal('0'))
        self.assertEqual(self.engine.jordyn_payable, Decimal('0'))
        
        # Should not raise
        self.engine.validate_invariant()
    
    def test_expense_maintains_invariants(self):
        """Test that expenses maintain double-entry balance."""
        # Ryan pays $100, split 50/50
        self.engine.post_expense(
            date=datetime.now(),
            payer='Ryan',
            ryan_share=Decimal('50'),
            jordyn_share=Decimal('50'),
            description='Test expense'
        )
        
        # Verify balances
        self.assertEqual(self.engine.ryan_receivable, Decimal('50'))
        self.assertEqual(self.engine.jordyn_payable, Decimal('50'))
        self.assertEqual(self.engine.ryan_payable, Decimal('0'))
        self.assertEqual(self.engine.jordyn_receivable, Decimal('0'))
        
        # Should not raise
        self.engine.validate_invariant()
    
    def test_settlement_maintains_invariants(self):
        """Test that settlements maintain balance."""
        # Setup: Jordyn owes Ryan $100
        self.engine.ryan_receivable = Decimal('100')
        self.engine.jordyn_payable = Decimal('100')
        
        # Jordyn pays Ryan $50
        self.engine.record_payment(
            date=datetime.now(),
            payer='Jordyn',
            amount=Decimal('50'),
            description='Partial payment'
        )
        
        # Verify balances
        self.assertEqual(self.engine.ryan_receivable, Decimal('50'))
        self.assertEqual(self.engine.jordyn_payable, Decimal('50'))
        
        # Should not raise
        self.engine.validate_invariant()
    
    def test_complex_transaction_sequence(self):
        """Test complex sequence maintains invariants."""
        # Multiple transactions
        transactions = [
            ('Ryan', Decimal('100'), Decimal('50'), Decimal('50')),  # Groceries
            ('Jordyn', Decimal('2400'), Decimal('1032'), Decimal('1368')),  # Rent
            ('Ryan', Decimal('200'), Decimal('0'), Decimal('200')),  # Full reimburse
            ('Jordyn', Decimal('60'), Decimal('30'), Decimal('30')),  # Dining
        ]
        
        for payer, total, ryan_share, jordyn_share in transactions:
            self.engine.post_expense(
                date=datetime.now(),
                payer=payer,
                ryan_share=ryan_share,
                jordyn_share=jordyn_share,
                description=f'Test from {payer}'
            )
            # Validate after each transaction
            self.engine.validate_invariant()
        
        # Make a payment
        self.engine.record_payment(
            date=datetime.now(),
            payer='Jordyn',
            amount=Decimal('500'),
            description='Settlement'
        )
        
        # Final validation
        self.engine.validate_invariant()


class TestDataValidation(unittest.TestCase):
    """Test data validation and quality checks."""
    
    def setUp(self):
        self.reconciler = GoldStandardReconciler()
    
    def test_safe_decimal_conversion(self):
        """Test decimal conversion handles edge cases."""
        test_cases = [
            ('100.50', Decimal('100.50')),
            ('$1,234.56', Decimal('1234.56')),
            ('$ -', Decimal('0')),
            ('-', Decimal('0')),
            ('', Decimal('0')),
            (None, Decimal('0')),
            (100.5, Decimal('100.5')),
            (100, Decimal('100')),
        ]
        
        for input_val, expected in test_cases:
            result = self.reconciler._safe_decimal_conversion(input_val)
            self.assertEqual(result, expected, 
                           f"Failed for input: {input_val}")
    
    def test_duplicate_detection(self):
        """Test duplicate transaction detection."""
        # Create test dataframe with duplicates
        data = {
            'date': [datetime(2024, 1, 1)] * 4,
            'amount': [100.0, 100.0, 100.01, 100.0],
            'description': ['Test', 'Test', 'Test', 'Different'],
            'payer': ['Ryan'] * 4,
            'source': ['Test'] * 4
        }
        df = pd.DataFrame(data)
        
        # Remove duplicates
        result = self.reconciler._remove_duplicate_transactions(df)
        
        # Should keep 3 transactions (exact duplicate removed)
        self.assertEqual(len(result), 3)
    
    def test_categorization(self):
        """Test transaction categorization."""
        test_cases = [
            ('San Palmas Web Payment', 'rent'),
            ('Zelle to Ryan', 'zelle_settlement'),
            ('Chase Card Autopay', 'personal'),
            ('Direct Deposit', 'income'),
            ('Salt River Project', 'utilities'),
            ('Fry\'s Food Store', 'groceries'),
            ('DoorDash', 'dining'),
            ('Random Store', 'expense'),
        ]
        
        for description, expected_category in test_cases:
            row = pd.Series({'description': description, 'amount': 100})
            category = self.reconciler._categorize_transaction(row)
            self.assertEqual(category, expected_category,
                           f"Failed for: {description}")


class TestReconciliationModes(unittest.TestCase):
    """Test different reconciliation modes."""
    
    def test_from_scratch_mode(self):
        """Test starting from zero."""
        reconciler = GoldStandardReconciler(
            mode=ReconciliationMode.FROM_SCRATCH
        )
        
        # Should start at zero
        balance = reconciler._get_current_balance()
        self.assertEqual(balance['amount'], Decimal('0'))
        self.assertEqual(balance['who_owes'], 'Balanced')
    
    def test_from_baseline_mode(self):
        """Test continuing from baseline."""
        baseline_amount = Decimal('1577.08')
        reconciler = GoldStandardReconciler(
            mode=ReconciliationMode.FROM_BASELINE,
            baseline_date=datetime(2024, 9, 30),
            baseline_amount=baseline_amount,
            baseline_who_owes='Jordyn owes Ryan'
        )
        
        # Should start at baseline
        balance = reconciler._get_current_balance()
        self.assertEqual(balance['amount'], baseline_amount)
        self.assertEqual(balance['who_owes'], 'Jordyn owes Ryan')
    
    def test_baseline_validation(self):
        """Test baseline mode requires all parameters."""
        with self.assertRaises(ValueError):
            GoldStandardReconciler(
                mode=ReconciliationMode.FROM_BASELINE,
                baseline_date=datetime(2024, 9, 30)
                # Missing amount and who_owes
            )


class TestPhase4Processing(unittest.TestCase):
    """Test Phase 4 data processing with allowed_amount."""
    
    def test_personal_expense_detection(self):
        """Test that allowed_amount = '$ -' marks as personal."""
        data = {
            'date': [datetime(2024, 1, 1)],
            'payer': ['Ryan'],
            'description': ['Personal item'],
            'amount': [Decimal('0')],  # Would be 0 after processing
            'original_amount': [Decimal('100')],
            'is_personal': [True],
            'has_manual_review': [True],
            'source': ['test']
        }
        df = pd.DataFrame(data)
        
        reconciler = GoldStandardReconciler()
        
        # Process the transaction
        reconciler.process_transaction(df.iloc[0])
        
        # Should be recorded as personal with no balance change
        self.assertEqual(reconciler.stats['personal_expenses_excluded'], 1)
        balance = reconciler._get_current_balance()
        self.assertEqual(balance['amount'], Decimal('0'))
    
    def test_manual_adjustment_tracking(self):
        """Test tracking of manual adjustments."""
        data = {
            'date': [datetime(2024, 1, 1)],
            'payer': ['Ryan'],
            'description': ['Partial reimbursement'],
            'amount': [Decimal('50')],  # Allowed
            'original_amount': [Decimal('100')],  # Actual
            'is_personal': [False],
            'manual_adjustment': [True],
            'has_manual_review': [True],
            'manual_notes': ['Only half is shared'],
            'source': ['test']
        }
        df = pd.DataFrame(data)
        
        reconciler = GoldStandardReconciler()
        reconciler.process_transaction(df.iloc[0])
        
        # Should track the adjustment
        self.assertEqual(reconciler.stats['allowed_vs_actual_adjustments'], 1)


class TestDataQualityReporting(unittest.TestCase):
    """Test data quality issue tracking and reporting."""
    
    def setUp(self):
        self.reconciler = GoldStandardReconciler()
    
    def test_missing_amount_detection(self):
        """Test detection of missing amounts."""
        data = {
            'date': [datetime(2024, 1, 1)],
            'payer': ['Ryan'],
            'description': ['Test'],
            'amount': [None],
            'source': ['Test']
        }
        df = pd.DataFrame(data)
        
        self.reconciler.process_transaction(df.iloc[0])
        
        # Should record data quality issue
        self.assertEqual(self.reconciler.stats['data_quality_issues'], 1)
        self.assertEqual(len(self.reconciler.data_quality_issues), 1)
        self.assertEqual(
            self.reconciler.data_quality_issues[0]['issue_type'],
            DataQualityIssue.MISSING_AMOUNT.value
        )


class TestEndToEndScenarios(unittest.TestCase):
    """Test complete reconciliation scenarios."""
    
    def test_simple_month_reconciliation(self):
        """Test reconciling a simple month."""
        reconciler = GoldStandardReconciler()
        
        # Create test transactions
        transactions = []
        
        # Rent - Jordyn pays
        transactions.append({
            'date': datetime(2024, 1, 1),
            'payer': 'Jordyn',
            'description': 'San Palmas Rent',
            'amount': Decimal('2400'),
            'has_manual_review': False,
            'source': 'test'
        })
        
        # Groceries - Ryan pays
        transactions.append({
            'date': datetime(2024, 1, 5),
            'payer': 'Ryan',
            'description': 'Fry\'s Groceries',
            'amount': Decimal('150'),
            'has_manual_review': False,
            'source': 'test'
        })
        
        # Settlement - Jordyn pays Ryan
        transactions.append({
            'date': datetime(2024, 1, 15),
            'payer': 'Jordyn',
            'description': 'Zelle to Ryan',
            'amount': Decimal('500'),
            'has_manual_review': False,
            'source': 'test'
        })
        
        # Process all transactions
        for tx_data in transactions:
            row = pd.Series(tx_data)
            reconciler.process_transaction(row)
        
        # Verify final balance
        # Rent: Ryan owes 43% of $2400 = $1032
        # Groceries: Jordyn owes 50% of $150 = $75
        # Net before settlement: $1032 - $75 = $957 (Ryan owes Jordyn)
        # After $500 settlement: $957 - $500 = $457 (Ryan owes Jordyn)
        
        balance = reconciler._get_current_balance()
        self.assertEqual(balance['who_owes'], 'Ryan owes Jordyn')
        self.assertAlmostEqual(float(balance['amount']), 457.0, places=2)
    
    def test_phase4_to_phase5_transition(self):
        """Test transitioning from Phase 4 to Phase 5 data."""
        # Start with baseline
        reconciler = GoldStandardReconciler(
            mode=ReconciliationMode.FROM_BASELINE,
            baseline_date=datetime(2024, 9, 30),
            baseline_amount=Decimal('1577.08'),
            baseline_who_owes='Jordyn owes Ryan'
        )
        
        # Add some October transactions
        october_transactions = [
            {
                'date': datetime(2024, 10, 1),
                'payer': 'Ryan',
                'description': 'Whole Foods',
                'amount': Decimal('89.50'),
                'has_manual_review': False,
                'source': 'test'
            },
            {
                'date': datetime(2024, 10, 15),
                'payer': 'Jordyn',
                'description': 'Zelle to Ryan',
                'amount': Decimal('1000'),
                'has_manual_review': False,
                'source': 'test'
            }
        ]
        
        for tx_data in october_transactions:
            row = pd.Series(tx_data)
            reconciler.process_transaction(row)
        
        # Verify balance updated correctly
        # Started: $1577.08 (Jordyn owes Ryan)
        # Whole Foods: +$44.75 (Jordyn's share)
        # Total owed: $1621.83
        # Payment: -$1000
        # Final: $621.83 (Jordyn owes Ryan)
        
        balance = reconciler._get_current_balance()
        self.assertEqual(balance['who_owes'], 'Jordyn owes Ryan')
        self.assertAlmostEqual(float(balance['amount']), 621.83, places=2)


class TestReportGeneration(unittest.TestCase):
    """Test report generation functionality."""
    
    def test_comprehensive_report_generation(self):
        """Test that all reports are generated correctly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            reconciler = GoldStandardReconciler()
            
            # Add some test data
            test_transaction = pd.Series({
                'date': datetime(2024, 1, 1),
                'payer': 'Ryan',
                'description': 'Test expense',
                'amount': Decimal('100'),
                'has_manual_review': False,
                'source': 'test'
            })
            reconciler.process_transaction(test_transaction)
            
            # Generate reports
            reconciler.generate_comprehensive_report(temp_dir)
            
            # Verify files exist
            expected_files = [
                'audit_trail.csv',
                'summary.json',
                'reconciliation_report.txt',
                'accounting_ledger.csv',
                'data_quality_report.txt'
            ]
            
            for filename in expected_files:
                file_path = Path(temp_dir) / filename
                self.assertTrue(file_path.exists(), 
                              f"Missing report file: {filename}")
            
            # Verify summary JSON structure
            with open(Path(temp_dir) / 'summary.json', 'r') as f:
                summary = json.load(f)
            
            self.assertIn('metadata', summary)
            self.assertIn('final_balance', summary)
            self.assertIn('statistics', summary)
            self.assertIn('data_quality', summary)


class TestPerformance(unittest.TestCase):
    """Test performance with large datasets."""
    
    def test_large_transaction_volume(self):
        """Test handling 10,000 transactions efficiently."""
        import time
        
        reconciler = GoldStandardReconciler()
        
        # Generate test transactions
        start_time = time.time()
        
        for i in range(10000):
            tx = pd.Series({
                'date': datetime(2024, 1, 1),
                'payer': 'Ryan' if i % 2 == 0 else 'Jordyn',
                'description': f'Transaction {i}',
                'amount': Decimal('10.50'),
                'has_manual_review': False,
                'source': 'test'
            })
            reconciler.process_transaction(tx)
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Should process 10k transactions in reasonable time
        self.assertLess(elapsed, 30, 
                       f"Processing took {elapsed:.2f}s, expected < 30s")
        
        # Verify all were processed
        self.assertEqual(reconciler.stats['transactions_processed'], 10000)
        
        # Verify invariants still hold
        reconciler.engine.validate_invariant()


def run_all_tests():
    """Run all test suites."""
    test_classes = [
        TestAccountingInvariants,
        TestDataValidation,
        TestReconciliationModes,
        TestPhase4Processing,
        TestDataQualityReporting,
        TestEndToEndScenarios,
        TestReportGeneration,
        TestPerformance
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)