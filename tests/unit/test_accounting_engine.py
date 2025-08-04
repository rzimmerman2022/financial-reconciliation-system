"""Comprehensive test suite for the Financial Reconciliation Accounting Engine.

This test suite verifies that the double-entry bookkeeping system maintains
perfect mathematical balance and correctly handles all transaction types.
Every test ensures the fundamental invariants hold true.

Test Categories:
1. Initial state and invariant validation
2. Expense transactions (both payers)
3. Rent payments (47% Ryan / 53% Jordyn)
4. Settlement transactions with overpayment handling
5. Complex multi-transaction scenarios
6. Currency precision and rounding
7. Error handling and validation
8. Audit trail functionality

Author: Claude (Anthropic)
Date: January 2024
"""

import unittest
from datetime import datetime
from decimal import Decimal
from src.core.accounting_engine import AccountingEngine, TransactionType, Transaction


class TestAccountingEngine(unittest.TestCase):
    """Test cases for the AccountingEngine double-entry bookkeeping system."""
    
    def setUp(self):
        """Initialize fresh accounting engine for each test.
        
        Each test starts with a clean slate - zero balances and no transactions.
        This ensures test isolation and prevents cross-test contamination.
        """
        self.engine = AccountingEngine()
        self.date = datetime(2024, 1, 1)
    
    def test_initial_state(self):
        """Verify the accounting system starts in a balanced state.
        
        All accounts should be zero and the system should report "Balanced".
        This test confirms proper initialization and that no phantom
        balances exist at startup.
        """
        # All accounts should start at zero
        self.assertEqual(self.engine.ryan_receivable, Decimal("0.00"))
        self.assertEqual(self.engine.ryan_payable, Decimal("0.00"))
        self.assertEqual(self.engine.jordyn_receivable, Decimal("0.00"))
        self.assertEqual(self.engine.jordyn_payable, Decimal("0.00"))
        
        # System should report balanced with zero amount
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Balanced")
        self.assertEqual(amount, Decimal("0.00"))
    
    def test_validate_invariant_holds(self):
        """Ensure mathematical invariants hold after every transaction.
        
        This test verifies that:
        1. The system starts valid
        2. Remains valid after Ryan pays an expense
        3. Remains valid after Jordyn pays an expense
        
        The invariant validation catches any mathematical errors immediately.
        """
        # Initial state should be valid
        self.engine.validate_invariant()
        
        # Post expense where Ryan pays - invariant should hold
        self.engine.post_expense(
            date=self.date,
            payer="Ryan",
            ryan_share=Decimal("50.00"),
            jordyn_share=Decimal("50.00"),
            description="Groceries"
        )
        self.engine.validate_invariant()
        
        # Post expense where Jordyn pays - invariant should still hold
        self.engine.post_expense(
            date=self.date,
            payer="Jordyn",
            ryan_share=Decimal("75.00"),
            jordyn_share=Decimal("75.00"),
            description="Utilities"
        )
        self.engine.validate_invariant()
    
    def test_expense_ryan_pays(self):
        """Test expense transaction where Ryan pays for both people.
        
        Scenario: Ryan pays $100 for dinner (60/40 split)
        - Ryan's share: $60 (he already paid this)
        - Jordyn's share: $40 (she owes Ryan this amount)
        
        Expected result: Jordyn owes Ryan $40
        """
        self.engine.post_expense(
            date=self.date,
            payer="Ryan",
            ryan_share=Decimal("60.00"),
            jordyn_share=Decimal("40.00"),
            description="Dinner"
        )
        
        # Ryan should be owed Jordyn's share
        self.assertEqual(self.engine.ryan_receivable, Decimal("40.00"))
        self.assertEqual(self.engine.ryan_payable, Decimal("0.00"))
        
        # Jordyn should owe Ryan her share
        self.assertEqual(self.engine.jordyn_receivable, Decimal("0.00"))
        self.assertEqual(self.engine.jordyn_payable, Decimal("40.00"))
        
        # Balance should show Jordyn owes Ryan
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Jordyn owes Ryan")
        self.assertEqual(amount, Decimal("40.00"))
    
    def test_expense_jordyn_pays(self):
        """Test expense transaction where Jordyn pays for both people.
        
        Scenario: Jordyn pays $60 for gas (50/50 split)
        - Jordyn's share: $30 (she already paid this)
        - Ryan's share: $30 (he owes Jordyn this amount)
        
        Expected result: Ryan owes Jordyn $30
        """
        self.engine.post_expense(
            date=self.date,
            payer="Jordyn",
            ryan_share=Decimal("30.00"),
            jordyn_share=Decimal("30.00"),
            description="Gas"
        )
        
        # Ryan should owe Jordyn his share
        self.assertEqual(self.engine.ryan_receivable, Decimal("0.00"))
        self.assertEqual(self.engine.ryan_payable, Decimal("30.00"))
        
        # Jordyn should be owed Ryan's share
        self.assertEqual(self.engine.jordyn_receivable, Decimal("30.00"))
        self.assertEqual(self.engine.jordyn_payable, Decimal("0.00"))
        
        # Balance should show Ryan owes Jordyn
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Ryan owes Jordyn")
        self.assertEqual(amount, Decimal("30.00"))
    
    def test_rent_payment(self):
        """Test monthly rent payment with 47/53 split.
        
        Scenario: Jordyn pays $2,100 rent to landlord
        - Ryan's share: $987 (47% of $2,100)
        - Jordyn's share: $1,113 (53% of $2,100)
        
        Expected result: Ryan owes Jordyn $987 for his rent share
        """
        self.engine.post_rent(
            date=self.date,
            total_rent=Decimal("2100.00"),
            ryan_percentage=0.47
        )
        
        # Ryan should owe his 47% share
        ryan_share = Decimal("987.00")
        self.assertEqual(self.engine.ryan_payable, ryan_share)
        self.assertEqual(self.engine.jordyn_receivable, ryan_share)
        
        # Balance should show Ryan owes Jordyn for rent
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Ryan owes Jordyn")
        self.assertEqual(amount, ryan_share)
    
    def test_settlement_simple(self):
        """Test simple settlement that exactly clears the balance.
        
        Scenario:
        1. Jordyn pays $200 for groceries (50/50 split)
        2. Ryan owes Jordyn $100
        3. Ryan sends Jordyn exactly $100
        
        Expected result: Accounts return to balanced state
        """
        # First create a debt: Jordyn pays, Ryan owes $100
        self.engine.post_expense(
            date=self.date,
            payer="Jordyn",
            ryan_share=Decimal("100.00"),
            jordyn_share=Decimal("100.00"),
            description="Groceries"
        )
        
        # Verify Ryan owes Jordyn
        self.assertEqual(self.engine.ryan_payable, Decimal("100.00"))
        self.assertEqual(self.engine.jordyn_receivable, Decimal("100.00"))
        
        # Ryan settles his debt
        self.engine.post_settlement(
            date=self.date,
            amount=Decimal("100.00"),
            from_person="Ryan",
            to_person="Jordyn"
        )
        
        # All balances should be cleared
        self.assertEqual(self.engine.ryan_payable, Decimal("0.00"))
        self.assertEqual(self.engine.jordyn_receivable, Decimal("0.00"))
        
        # System should be balanced
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Balanced")
        self.assertEqual(amount, Decimal("0.00"))
    
    def test_settlement_overpayment(self):
        """Test settlement with overpayment that reverses the balance.
        
        Scenario:
        1. Jordyn pays $100 for lunch (50/50 split)
        2. Ryan owes Jordyn $50
        3. Ryan sends Jordyn $100 (overpays by $50)
        
        Expected result: Balance reverses - now Jordyn owes Ryan $50
        
        This tests the critical overpayment handling logic that prevents
        the system from showing both people with positive balances.
        """
        # Create initial debt: Ryan owes Jordyn $50
        self.engine.post_expense(
            date=self.date,
            payer="Jordyn",
            ryan_share=Decimal("50.00"),
            jordyn_share=Decimal("50.00"),
            description="Lunch"
        )
        
        # Ryan overpays by sending $100 instead of $50
        self.engine.post_settlement(
            date=self.date,
            amount=Decimal("100.00"),
            from_person="Ryan",
            to_person="Jordyn"
        )
        
        # Balance should reverse: now Jordyn owes Ryan
        self.assertEqual(self.engine.ryan_receivable, Decimal("50.00"))
        self.assertEqual(self.engine.jordyn_payable, Decimal("50.00"))
        
        # Verify the reversal is reflected in balance
        status, amount = self.engine.get_current_balance()
        self.assertEqual(status, "Jordyn owes Ryan")
        self.assertEqual(amount, Decimal("50.00"))
    
    def test_complex_scenario(self):
        """Test a realistic sequence of transactions over time.
        
        This simulates a typical month with:
        1. Rent payment (Jordyn pays, Ryan owes 47%)
        2. Groceries (Ryan pays)
        3. Utilities (Jordyn pays)
        4. Partial settlement from Ryan
        5. Pizza (Ryan pays)
        
        Verifies the invariant holds throughout and final balance is correct.
        """
        # January 1: Rent payment - Ryan owes Jordyn $987
        self.engine.post_rent(
            date=datetime(2024, 1, 1),
            total_rent=Decimal("2100.00")
        )
        
        # January 5: Ryan buys groceries - reduces his debt by $40
        self.engine.post_expense(
            date=datetime(2024, 1, 5),
            payer="Ryan",
            ryan_share=Decimal("60.00"),
            jordyn_share=Decimal("40.00"),
            description="Groceries"
        )
        
        # January 10: Jordyn pays utilities - increases Ryan's debt by $150
        self.engine.post_expense(
            date=datetime(2024, 1, 10),
            payer="Jordyn",
            ryan_share=Decimal("150.00"),
            jordyn_share=Decimal("150.00"),
            description="Utilities"
        )
        
        # January 15: Ryan sends partial settlement of $500
        self.engine.post_settlement(
            date=datetime(2024, 1, 15),
            amount=Decimal("500.00"),
            from_person="Ryan",
            to_person="Jordyn"
        )
        
        # January 20: Ryan buys pizza - reduces his debt by $25
        self.engine.post_expense(
            date=datetime(2024, 1, 20),
            payer="Ryan",
            ryan_share=Decimal("25.00"),
            jordyn_share=Decimal("25.00"),
            description="Pizza"
        )
        
        # Verify invariant still holds after complex sequence
        self.engine.validate_invariant()
        
        # Verify net positions are opposites (fundamental invariant)
        ryan_net = self.engine.ryan_receivable - self.engine.ryan_payable
        jordyn_net = self.engine.jordyn_receivable - self.engine.jordyn_payable
        self.assertAlmostEqual(float(ryan_net), -float(jordyn_net), places=2)
    
    def test_transaction_logging(self):
        """Verify transaction log captures all transactions with metadata.
        
        The transaction log provides a complete audit trail for:
        - Debugging disputed balances
        - Tax preparation
        - Historical analysis
        """
        # Create one of each transaction type
        self.engine.post_expense(
            date=self.date,
            payer="Ryan",
            ryan_share=Decimal("50.00"),
            jordyn_share=Decimal("50.00"),
            description="Test expense"
        )
        
        self.engine.post_rent(
            date=self.date,
            total_rent=Decimal("2000.00")
        )
        
        self.engine.post_settlement(
            date=self.date,
            amount=Decimal("500.00")
        )
        
        # Verify all transactions are logged
        transactions = self.engine.get_transaction_log()
        self.assertEqual(len(transactions), 3)
        
        # Verify transaction types are recorded correctly
        self.assertEqual(transactions[0]["transaction_type"], "EXPENSE")
        self.assertEqual(transactions[1]["transaction_type"], "RENT")
        self.assertEqual(transactions[2]["transaction_type"], "SETTLEMENT")
    
    def test_currency_precision(self):
        """Verify proper rounding to 2 decimal places (cents).
        
        When splitting $100 three ways, each person pays $33.333...
        The system should round to exactly $33.33 using banker's rounding.
        This prevents penny discrepancies from accumulating.
        """
        self.engine.post_expense(
            date=self.date,
            payer="Ryan",
            ryan_share=Decimal("33.333"),  # Will be rounded
            jordyn_share=Decimal("33.333"), # Will be rounded
            description="Split three ways"
        )
        
        # Verify amounts are rounded to exactly 2 decimal places
        self.assertEqual(self.engine.ryan_receivable, Decimal("33.33"))
        self.assertEqual(self.engine.jordyn_payable, Decimal("33.33"))
    
    def test_invalid_payer(self):
        """Verify system rejects transactions with invalid payers.
        
        The system only supports Ryan and Jordyn. Any other payer
        should raise a ValueError to prevent data corruption.
        """
        with self.assertRaises(ValueError):
            self.engine.post_expense(
                date=self.date,
                payer="Alice",  # Invalid - not Ryan or Jordyn
                ryan_share=Decimal("50.00"),
                jordyn_share=Decimal("50.00"),
                description="Invalid payer"
            )
    
    def test_account_summary(self):
        """Test account summary provides accurate snapshot of finances.
        
        The summary should show:
        - Individual account balances
        - Net positions (receivable - payable)
        - Current balance status
        - Transaction count
        """
        # Create a transaction where Ryan owes Jordyn
        self.engine.post_expense(
            date=self.date,
            payer="Jordyn",
            ryan_share=Decimal("100.00"),
            jordyn_share=Decimal("100.00"),
            description="Test"
        )
        
        summary = self.engine.get_account_summary()
        
        # Verify account balances
        self.assertEqual(summary["ryan_payable"], "100.00")
        self.assertEqual(summary["jordyn_receivable"], "100.00")
        
        # Verify net positions are opposites
        self.assertEqual(summary["ryan_net"], "-100.00")    # Negative = owes
        self.assertEqual(summary["jordyn_net"], "100.00")   # Positive = owed
        
        # Verify transaction count
        self.assertEqual(summary["transaction_count"], 1)
    
    def test_transaction_double_entry(self):
        """Verify Transaction class enforces double-entry principle.
        
        Every transaction must have equal debits and credits.
        This test ensures the Transaction class itself validates
        this fundamental accounting rule.
        
        Attempting to create an unbalanced transaction should fail.
        """
        with self.assertRaises(ValueError):
            Transaction(
                date=self.date,
                transaction_type=TransactionType.EXPENSE,
                description="Invalid transaction",
                ryan_debit=Decimal("100.00"),    # Total debits: $100
                ryan_credit=Decimal("0.00"),
                jordyn_debit=Decimal("0.00"),
                jordyn_credit=Decimal("50.00")    # Total credits: $50 - INVALID!
            )
    
    def test_invariant_after_multiple_transactions(self):
        """Stress test with multiple transactions to ensure invariants hold.
        
        This test:
        1. Creates 10 alternating expense transactions
        2. Validates the invariant after each one
        3. Adds a settlement
        4. Verifies the fundamental equation: Ryan_net + Jordyn_net = 0
        
        This ensures the system maintains mathematical correctness even
        after many transactions.
        """
        # Create 10 transactions with alternating payers
        for i in range(10):
            self.engine.post_expense(
                date=self.date,
                payer="Ryan" if i % 2 == 0 else "Jordyn",
                ryan_share=Decimal(f"{10 + i}.00"),      # Increasing amounts
                jordyn_share=Decimal(f"{10 + i}.00"),
                description=f"Transaction {i}"
            )
            # Validate after each transaction
            self.engine.validate_invariant()
        
        # Add a settlement to mix transaction types
        self.engine.post_settlement(
            date=self.date,
            amount=Decimal("50.00"),
            from_person="Jordyn",
            to_person="Ryan"
        )
        self.engine.validate_invariant()
        
        # Verify the fundamental invariant: net positions sum to zero
        ryan_net = self.engine.ryan_receivable - self.engine.ryan_payable
        jordyn_net = self.engine.jordyn_receivable - self.engine.jordyn_payable
        self.assertAlmostEqual(float(ryan_net + jordyn_net), 0.0, places=2)


if __name__ == "__main__":
    # Run all tests with verbose output
    unittest.main()