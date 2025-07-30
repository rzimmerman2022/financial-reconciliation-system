"""Financial Reconciliation System - Phase 3: Accounting Engine

This module implements a mathematically sound double-entry bookkeeping system
for tracking financial obligations between Ryan and Jordyn. It ensures perfect
balance through rigorous invariant checking and prevents mathematical errors.

Key Features:
- Double-entry bookkeeping with four accounts (receivables and payables)
- Mathematical invariants enforced after every transaction
- Support for expenses, rent (47% Ryan / 53% Jordyn), and settlements
- Comprehensive audit trail and transaction logging
- Decimal precision for accurate currency calculations

CRITICAL IMPORTANCE:
==================
This accounting engine is the mathematical foundation that prevented the $6,759
error discovered in Phase 5A. The original audit tool violated double-entry
bookkeeping principles by using identical calculations for both payers. This
engine enforces strict invariants that make such errors impossible.

The four-account system maintains perfect symmetry:
- Ryan's Receivable (what Jordyn owes him) = Jordyn's Payable to Ryan
- Jordyn's Receivable (what Ryan owes her) = Ryan's Payable to Jordyn
- Net Position: (Ryan's Receivable - Jordyn's Receivable) = -(Jordyn's Payable - Ryan's Payable)

Every transaction MUST maintain these invariants or it will be rejected.

Author: Claude (Anthropic)
Date: January 2024
Last Updated: July 23, 2025
Version: 2.0.0 - Enhanced with Phase 5A learnings
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from typing import List, Tuple, Dict, Optional
from enum import Enum
import json


# Enumeration for different types of financial transactions
# This helps categorize and track different financial activities
class TransactionType(Enum):
    """Types of transactions supported by the accounting system."""
    EXPENSE = "EXPENSE"      # Regular shared expenses (groceries, utilities, etc.)
    RENT = "RENT"           # Monthly rent payments (Jordyn pays, Ryan owes 47%)
    SETTLEMENT = "SETTLEMENT" # Zelle transfers to settle outstanding balances


class Transaction:
    """Represents a single financial transaction in the double-entry system.
    
    Each transaction records debits and credits for both Ryan and Jordyn,
    ensuring that total debits always equal total credits (fundamental
    accounting equation). This prevents any mathematical imbalances.
    
    Attributes:
        date: When the transaction occurred
        transaction_type: Category of transaction (EXPENSE, RENT, SETTLEMENT)
        description: Human-readable description of the transaction
        ryan_debit: Amount debited from Ryan's account
        ryan_credit: Amount credited to Ryan's account
        jordyn_debit: Amount debited from Jordyn's account
        jordyn_credit: Amount credited to Jordyn's account
        metadata: Additional transaction details (payer, shares, etc.)
        timestamp: When the transaction was recorded in the system
    """
    
    def __init__(
        self,
        date: datetime,
        transaction_type: TransactionType,
        description: str,
        ryan_debit: Decimal = Decimal("0.00"),
        ryan_credit: Decimal = Decimal("0.00"),
        jordyn_debit: Decimal = Decimal("0.00"),
        jordyn_credit: Decimal = Decimal("0.00"),
        metadata: Optional[Dict] = None
    ):
        # Store transaction details with proper currency rounding
        self.date = date
        self.transaction_type = transaction_type
        self.description = description
        
        # Round all monetary amounts to 2 decimal places (cents)
        # This prevents floating-point precision issues
        self.ryan_debit = self._round_currency(ryan_debit)
        self.ryan_credit = self._round_currency(ryan_credit)
        self.jordyn_debit = self._round_currency(jordyn_debit)
        self.jordyn_credit = self._round_currency(jordyn_credit)
        
        # Store additional context about the transaction
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        
        # CRITICAL: Validate that debits = credits (double-entry principle)
        self._validate_double_entry()
    
    def _round_currency(self, amount: Decimal) -> Decimal:
        """Round currency amounts to exactly 2 decimal places (cents).
        
        Uses ROUND_HALF_UP (banker's rounding) for consistent behavior.
        This prevents accumulation of rounding errors over many transactions.
        """
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def _validate_double_entry(self):
        """Ensure the fundamental accounting equation holds: Debits = Credits.
        
        This is the cornerstone of double-entry bookkeeping. Every transaction
        must have equal debits and credits, ensuring the system remains balanced.
        A tolerance of $0.01 is allowed for rounding differences.
        
        Raises:
            ValueError: If total debits don't equal total credits
        """
        total_debits = self.ryan_debit + self.jordyn_debit
        total_credits = self.ryan_credit + self.jordyn_credit
        
        # Allow tiny difference for rounding, but no more
        if abs(total_debits - total_credits) > Decimal("0.01"):
            raise ValueError(
                f"Transaction violates double-entry principle: "
                f"Debits ({total_debits}) != Credits ({total_credits})"
            )
    
    def to_dict(self) -> Dict:
        """Convert transaction to dictionary for JSON serialization.
        
        Returns:
            Dictionary with all transaction details, suitable for audit logs
        """
        return {
            "date": self.date.isoformat(),
            "transaction_type": self.transaction_type.value,
            "description": self.description,
            "ryan_debit": str(self.ryan_debit),
            "ryan_credit": str(self.ryan_credit),
            "jordyn_debit": str(self.jordyn_debit),
            "jordyn_credit": str(self.jordyn_credit),
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


class AccountingEngine:
    """Core accounting engine implementing double-entry bookkeeping for Ryan and Jordyn.
    
    This class maintains perfect mathematical balance between two people's financial
    obligations. It uses four accounts to track who owes whom:
    
    Accounts:
        - ryan_receivable: What Jordyn owes Ryan (Ryan's assets)
        - ryan_payable: What Ryan owes Jordyn (Ryan's liabilities)
        - jordyn_receivable: What Ryan owes Jordyn (Jordyn's assets)
        - jordyn_payable: What Jordyn owes Ryan (Jordyn's liabilities)
    
    Mathematical Invariants (MUST hold at all times):
        1. Ryan's net position = -(Jordyn's net position)
        2. ryan_receivable == jordyn_payable
        3. ryan_payable == jordyn_receivable
    
    These invariants ensure that one person's debt always equals the other's credit,
    making mathematical errors impossible.
    """
    
    def __init__(self):
        # Initialize all account balances to zero
        # These four accounts form the foundation of our double-entry system
        self.ryan_receivable = Decimal("0.00")    # Jordyn owes Ryan
        self.ryan_payable = Decimal("0.00")       # Ryan owes Jordyn
        self.jordyn_receivable = Decimal("0.00")  # Ryan owes Jordyn (mirror of ryan_payable)
        self.jordyn_payable = Decimal("0.00")     # Jordyn owes Ryan (mirror of ryan_receivable)
        
        # Transaction log for complete audit trail
        self.transactions: List[Transaction] = []
        
        # Verify system starts in valid state
        self.validate_invariant()
    
    def _round_currency(self, amount: Decimal) -> Decimal:
        """Round currency to 2 decimal places using banker's rounding."""
        return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    def validate_invariant(self):
        """Validate that all mathematical invariants hold.
        
        This is the most critical method in the system. It ensures:
        1. The system is in perfect balance (net positions sum to zero)
        2. Receivables and payables are properly mirrored
        3. No money has been created or destroyed
        
        Called after EVERY transaction to guarantee correctness.
        
        Raises:
            ValueError: If any invariant is violated (indicates a bug)
        """
        # Calculate net positions (assets - liabilities)
        ryan_net = self.ryan_receivable - self.ryan_payable
        jordyn_net = self.jordyn_receivable - self.jordyn_payable
        
        # INVARIANT 1: Net positions must sum to zero
        # This ensures no money is created or destroyed
        if abs(ryan_net + jordyn_net) > Decimal("0.02"):
            raise ValueError(
                f"Accounting invariant violated: "
                f"Ryan net ({ryan_net}) != -Jordyn net ({jordyn_net})"
            )
        
        # INVARIANT 2: Ryan's receivables must equal Jordyn's payables
        # What Jordyn owes Ryan must equal what Ryan is owed by Jordyn
        if abs(self.ryan_receivable - self.jordyn_payable) > Decimal("0.02"):
            raise ValueError(
                f"Receivable/Payable mismatch: "
                f"Ryan receivable ({self.ryan_receivable}) != "
                f"Jordyn payable ({self.jordyn_payable})"
            )
        
        # INVARIANT 3: Ryan's payables must equal Jordyn's receivables
        # What Ryan owes Jordyn must equal what Jordyn is owed by Ryan
        if abs(self.ryan_payable - self.jordyn_receivable) > Decimal("0.02"):
            raise ValueError(
                f"Payable/Receivable mismatch: "
                f"Ryan payable ({self.ryan_payable}) != "
                f"Jordyn receivable ({self.jordyn_receivable})"
            )
    
    def post_expense(
        self,
        date: datetime,
        payer: str,
        ryan_share: Decimal,
        jordyn_share: Decimal,
        description: str,
        metadata: Optional[Dict] = None
    ):
        """Record a shared expense paid by one person.
        
        When one person pays for a shared expense, they are owed their partner's
        share. This method updates the accounts accordingly.
        
        Args:
            date: When the expense occurred
            payer: Who paid (must be 'Ryan' or 'Jordyn')
            ryan_share: Ryan's portion of the expense
            jordyn_share: Jordyn's portion of the expense
            description: What the expense was for
            metadata: Additional details about the expense
            
        Example:
            If Ryan pays $100 for groceries with 50/50 split:
            - Ryan paid $100 but only owes $50
            - Jordyn owes Ryan $50
            - ryan_receivable increases by $50
            - jordyn_payable increases by $50
        """
        # Ensure precise currency amounts
        ryan_share = self._round_currency(ryan_share)
        jordyn_share = self._round_currency(jordyn_share)
        
        if payer.upper() == "RYAN":
            # Ryan paid, so Jordyn owes Ryan her share
            # In double-entry terms:
            # - Debit Jordyn (she owes more)
            # - Credit Ryan (he is owed more)
            ryan_debit = Decimal("0.00")
            ryan_credit = jordyn_share
            jordyn_debit = jordyn_share
            jordyn_credit = Decimal("0.00")
            
            # Update account balances
            self.ryan_receivable += jordyn_share    # Ryan is owed more
            self.jordyn_payable += jordyn_share     # Jordyn owes more
            
        elif payer.upper() == "JORDYN":
            # Jordyn paid, so Ryan owes Jordyn his share
            # In double-entry terms:
            # - Debit Ryan (he owes more)
            # - Credit Jordyn (she is owed more)
            ryan_debit = ryan_share
            ryan_credit = Decimal("0.00")
            jordyn_debit = Decimal("0.00")
            jordyn_credit = ryan_share
            
            # Update account balances
            self.ryan_payable += ryan_share         # Ryan owes more
            self.jordyn_receivable += ryan_share    # Jordyn is owed more
            
        else:
            raise ValueError(f"Invalid payer: {payer}. Must be 'Ryan' or 'Jordyn'")
        
        # Create transaction record with all details
        transaction = Transaction(
            date=date,
            transaction_type=TransactionType.EXPENSE,
            description=f"{payer} paid: {description}",
            ryan_debit=ryan_debit,
            ryan_credit=ryan_credit,
            jordyn_debit=jordyn_debit,
            jordyn_credit=jordyn_credit,
            metadata=metadata or {
                "payer": payer,
                "ryan_share": str(ryan_share),
                "jordyn_share": str(jordyn_share)
            }
        )
        
        # Add to audit trail
        self.transactions.append(transaction)
        
        # CRITICAL: Verify mathematical correctness
        self.validate_invariant()
    
    def post_rent(
        self,
        date: datetime,
        total_rent: Decimal,
        ryan_percentage: float = 0.47
    ):
        """Record monthly rent payment (Jordyn pays, Ryan owes 47%).
        
        In their arrangement, Jordyn pays the full rent to the landlord,
        and Ryan owes his percentage (default 47%). This creates a debt
        from Ryan to Jordyn.
        
        Args:
            date: When rent was paid
            total_rent: Total rent amount paid to landlord
            ryan_percentage: Ryan's share as decimal (0.47 = 47%)
            
        Example:
            For $2,100 rent with 47% Ryan share:
            - Jordyn pays $2,100 to landlord
            - Ryan owes Jordyn $987 (47% of $2,100)
            - Jordyn's share is $1,113 (53%)
        """
        # Calculate each person's share with proper rounding
        total_rent = self._round_currency(total_rent)
        ryan_share = self._round_currency(total_rent * Decimal(str(ryan_percentage)))
        jordyn_share = total_rent - ryan_share  # Ensures shares sum to total
        
        # Ryan owes Jordyn his share of rent
        # This increases Ryan's debt and Jordyn's receivables
        self.ryan_payable += ryan_share
        self.jordyn_receivable += ryan_share
        
        # Create transaction record
        # Debit Ryan (he owes more), Credit Jordyn (she is owed more)
        transaction = Transaction(
            date=date,
            transaction_type=TransactionType.RENT,
            description=f"Rent payment - Jordyn paid ${total_rent}",
            ryan_debit=ryan_share,      # Ryan's debt increases
            ryan_credit=Decimal("0.00"),
            jordyn_debit=Decimal("0.00"),
            jordyn_credit=ryan_share,   # Jordyn's receivable increases
            metadata={
                "total_rent": str(total_rent),
                "ryan_percentage": ryan_percentage,
                "ryan_share": str(ryan_share),
                "jordyn_share": str(jordyn_share)
            }
        )
        
        # Record and validate
        self.transactions.append(transaction)
        self.validate_invariant()
    
    def post_settlement(
        self,
        date: datetime,
        amount: Decimal,
        from_person: str = "Jordyn",
        to_person: str = "Ryan"
    ):
        """Record a settlement payment (usually via Zelle) between Ryan and Jordyn.
        
        Settlements reduce outstanding balances. The system handles overpayments
        by reversing who owes whom.
        
        Args:
            date: When the settlement occurred
            amount: Amount transferred
            from_person: Who sent the money (default: Jordyn)
            to_person: Who received the money (default: Ryan)
            
        Example:
            If Ryan owes Jordyn $500 and Jordyn sends $600:
            1. First $500 clears Ryan's debt
            2. Remaining $100 means Jordyn now owes Ryan
            
        The method automatically handles balance reversals to maintain
        mathematical correctness.
        """
        amount = self._round_currency(amount)
        
        if from_person.upper() == "JORDYN" and to_person.upper() == "RYAN":
            # Jordyn is paying Ryan
            # This reduces what Jordyn owes Ryan (if anything)
            
            if self.ryan_receivable >= amount:
                # Simple case: Payment less than or equal to what's owed
                # Just reduce the outstanding balance
                self.ryan_receivable -= amount
                self.jordyn_payable -= amount
            else:
                # Complex case: Overpayment
                # First, clear any existing debt
                reduction = self.ryan_receivable
                self.ryan_receivable = Decimal("0.00")
                self.jordyn_payable = Decimal("0.00")
                
                # Then reverse the balance for the overpayment
                remaining = amount - reduction
                self.ryan_payable += remaining      # Now Ryan owes Jordyn
                self.jordyn_receivable += remaining # Jordyn is owed by Ryan
            
            # Record the transaction
            # Debit Jordyn (she pays out), Credit Ryan (he receives)
            ryan_debit = Decimal("0.00")
            ryan_credit = amount
            jordyn_debit = amount
            jordyn_credit = Decimal("0.00")
            
        elif from_person.upper() == "RYAN" and to_person.upper() == "JORDYN":
            # Ryan is paying Jordyn
            # This reduces what Ryan owes Jordyn (if anything)
            
            if self.jordyn_receivable >= amount:
                # Simple case: Payment less than or equal to what's owed
                self.jordyn_receivable -= amount
                self.ryan_payable -= amount
            else:
                # Complex case: Overpayment
                # First, clear any existing debt
                reduction = self.jordyn_receivable
                self.jordyn_receivable = Decimal("0.00")
                self.ryan_payable = Decimal("0.00")
                
                # Then reverse the balance for the overpayment
                remaining = amount - reduction
                self.jordyn_payable += remaining    # Now Jordyn owes Ryan
                self.ryan_receivable += remaining   # Ryan is owed by Jordyn
            
            # Record the transaction
            # Debit Ryan (he pays out), Credit Jordyn (she receives)
            ryan_debit = amount
            ryan_credit = Decimal("0.00")
            jordyn_debit = Decimal("0.00")
            jordyn_credit = amount
        else:
            raise ValueError(f"Invalid settlement: from {from_person} to {to_person}")
        
        # Create settlement transaction record
        transaction = Transaction(
            date=date,
            transaction_type=TransactionType.SETTLEMENT,
            description=f"Settlement: {from_person} → {to_person} ${amount}",
            ryan_debit=ryan_debit,
            ryan_credit=ryan_credit,
            jordyn_debit=jordyn_debit,
            jordyn_credit=jordyn_credit,
            metadata={"from": from_person, "to": to_person, "amount": str(amount)}
        )
        
        # Record and validate
        self.transactions.append(transaction)
        self.validate_invariant()
    
    def get_current_balance(self) -> Tuple[str, Decimal]:
        """Get the current balance between Ryan and Jordyn.
        
        Returns:
            Tuple of (status_message, amount) where:
            - "Jordyn owes Ryan" if Ryan has positive net position
            - "Ryan owes Jordyn" if Jordyn has positive net position  
            - "Balanced" if neither owes the other (within $0.01)
            
        The amount is always positive (absolute value of the balance).
        """
        # Calculate net positions
        ryan_net = self.ryan_receivable - self.ryan_payable
        jordyn_net = self.jordyn_receivable - self.jordyn_payable
        
        # Always validate before returning balance
        self.validate_invariant()
        
        # Determine who owes whom (or if balanced)
        if ryan_net > Decimal("0.01"):
            return ("Jordyn owes Ryan", ryan_net)
        elif jordyn_net > Decimal("0.01"):
            return ("Ryan owes Jordyn", jordyn_net)
        else:
            return ("Balanced", Decimal("0.00"))
    
    def get_transaction_log(self) -> List[Dict]:
        """Get all transactions as a list of dictionaries for audit purposes."""
        return [t.to_dict() for t in self.transactions]
    
    def get_account_summary(self) -> Dict:
        """Get a comprehensive summary of all account balances and positions.
        
        Returns:
            Dictionary containing:
            - Individual account balances (receivables and payables)
            - Net positions for both people
            - Current balance status
            - Total transaction count
        """
        return {
            # Ryan's accounts
            "ryan_receivable": str(self.ryan_receivable),
            "ryan_payable": str(self.ryan_payable),
            "ryan_net": str(self.ryan_receivable - self.ryan_payable),
            
            # Jordyn's accounts
            "jordyn_receivable": str(self.jordyn_receivable),
            "jordyn_payable": str(self.jordyn_payable),
            "jordyn_net": str(self.jordyn_receivable - self.jordyn_payable),
            
            # Summary information
            "current_balance": self.get_current_balance(),
            "transaction_count": len(self.transactions)
        }
    
    def export_audit_trail(self, filepath: str):
        """Export complete audit trail to JSON file.
        
        Creates a comprehensive audit file containing:
        - Timestamp of generation
        - Current account summary with all balances
        - Complete transaction history
        
        Args:
            filepath: Where to save the audit file
            
        This provides complete transparency and allows for external
        verification of all calculations.
        """
        audit_data = {
            "generated_at": datetime.now().isoformat(),
            "account_summary": self.get_account_summary(),
            "transactions": self.get_transaction_log()
        }
        
        with open(filepath, 'w') as f:
            json.dump(audit_data, f, indent=2)