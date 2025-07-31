# API Reference

## Overview

The Financial Reconciliation System provides a comprehensive Python API for programmatic access to all reconciliation, review, and accounting functionality. This reference covers all public classes, methods, and interfaces.

## Core Modules

### `src.core.accounting_engine`

The accounting engine implements double-entry bookkeeping with automatic balance validation.

#### `AccountingEngine`

Main accounting class that maintains account balances and transaction history.

```python
from src.core.accounting_engine import AccountingEngine, TransactionType
from decimal import Decimal
from datetime import datetime

# Initialize engine
engine = AccountingEngine()

# Post a shared expense
engine.post_expense(
    date=datetime(2024, 10, 15),
    payer="Jordyn",
    ryan_share=Decimal("50.00"),
    jordyn_share=Decimal("50.00"),
    description="Groceries at Whole Foods"
)

# Get current balance
balance_info = engine.get_current_balance()
# Returns: ('Ryan owes Jordyn', Decimal('50.00'))
```

**Methods:**

- `post_expense(date, payer, ryan_share, jordyn_share, description, metadata=None)`
  - Records a shared expense transaction
  - **Parameters:**
    - `date` (datetime): Transaction date
    - `payer` (str): Who paid ("Ryan" or "Jordyn")
    - `ryan_share` (Decimal): Ryan's portion
    - `jordyn_share` (Decimal): Jordyn's portion  
    - `description` (str): Transaction description
    - `metadata` (dict, optional): Additional transaction data
  - **Returns:** None
  - **Raises:** ValueError if payer invalid or amounts negative

- `post_rent(date, payer, ryan_share, jordyn_share, description, metadata=None)`
  - Records a rent payment transaction
  - **Parameters:** Same as post_expense
  - **Returns:** None

- `post_settlement(date, payer, amount, description, metadata=None)`
  - Records a settlement payment (Zelle/Venmo transfer)
  - **Parameters:**
    - `date` (datetime): Transfer date
    - `payer` (str): Who sent money
    - `amount` (Decimal): Transfer amount
    - `description` (str): Transfer description
    - `metadata` (dict, optional): Additional data
  - **Returns:** None

- `get_current_balance()`
  - Returns current balance between parties
  - **Returns:** Tuple[str, Decimal] - (who_owes_whom, amount)

- `get_account_summary()`
  - Returns detailed account summary
  - **Returns:** Dict with receivables, payables, and net positions

- `export_audit_trail()`
  - Exports complete transaction history
  - **Returns:** List[Dict] with all transactions and running balances

- `validate_invariant()`
  - Validates accounting invariants (double-entry rules)
  - **Returns:** None
  - **Raises:** ValueError if invariants violated

#### `Transaction`

Represents a single accounting transaction.

```python
from src.core.accounting_engine import Transaction, TransactionType
from decimal import Decimal
from datetime import datetime

# Create transaction
txn = Transaction(
    date=datetime(2024, 10, 15),
    transaction_type=TransactionType.EXPENSE,
    description="Shared dinner",
    ryan_debit=Decimal("25.00"),
    jordyn_credit=Decimal("25.00")
)
```

**Attributes:**
- `date` (datetime): Transaction date
- `transaction_type` (TransactionType): Type of transaction
- `description` (str): Human-readable description
- `ryan_debit` (Decimal): Debit to Ryan's account
- `ryan_credit` (Decimal): Credit to Ryan's account
- `jordyn_debit` (Decimal): Debit to Jordyn's account
- `jordyn_credit` (Decimal): Credit to Jordyn's account
- `metadata` (dict): Additional transaction data

#### `TransactionType`

Enumeration of supported transaction types.

```python
from src.core.accounting_engine import TransactionType

# Available types:
TransactionType.EXPENSE      # Shared expenses
TransactionType.RENT         # Monthly rent payments
TransactionType.SETTLEMENT   # Zelle/Venmo transfers
```

### `src.core.reconciliation_engine`

Main reconciliation engine for processing financial data.

#### `GoldStandardReconciler`

Primary reconciliation class with support for baseline and from-scratch modes.

```python
from src.core.reconciliation_engine import GoldStandardReconciler, ReconciliationMode
from decimal import Decimal
from datetime import datetime

# Initialize reconciler
reconciler = GoldStandardReconciler(
    mode=ReconciliationMode.FROM_BASELINE,
    baseline_date=datetime(2024, 9, 30),
    baseline_amount=Decimal('1577.08'),
    baseline_who_owes='Jordyn owes Ryan'
)

# Run reconciliation
reconciler.run_reconciliation(
    phase5_start=datetime(2024, 10, 1),
    phase5_end=datetime(2024, 12, 31)
)

# Get results
summary = reconciler.get_reconciliation_summary()
```

**Methods:**

- `run_reconciliation(phase4_start=None, phase4_end=None, phase5_start=None, phase5_end=None)`
  - Executes the reconciliation process
  - **Parameters:**
    - `phase4_start` (datetime, optional): Start date for Phase 4 data
    - `phase4_end` (datetime, optional): End date for Phase 4 data
    - `phase5_start` (datetime, optional): Start date for Phase 5+ data
    - `phase5_end` (datetime, optional): End date for Phase 5+ data
  - **Returns:** None

- `get_reconciliation_summary()`
  - Returns comprehensive reconciliation results
  - **Returns:** Dict with balance, transaction counts, processing statistics

- `export_results(output_dir='output/gold_standard')`
  - Exports all reconciliation results to files
  - **Parameters:**
    - `output_dir` (str): Directory for output files
  - **Returns:** None

#### `ReconciliationMode`

Enumeration of reconciliation modes.

```python
from src.core.reconciliation_engine import ReconciliationMode

# Available modes:
ReconciliationMode.FROM_BASELINE  # Start from known baseline date
ReconciliationMode.FROM_SCRATCH   # Process all historical data
```

### `src.review.manual_review_system`

Manual review system for categorizing transactions.

#### `ManualReviewSystem`

Database-backed system for storing and retrieving transaction review decisions.

```python
from src.review.manual_review_system import ManualReviewSystem, TransactionCategory
from decimal import Decimal
from datetime import datetime

# Initialize review system
review_system = ManualReviewSystem("data/phase5_manual_reviews.db")

# Add transaction for review
review_id = review_system.add_transaction_for_review(
    date=datetime(2024, 10, 15),
    description="APPLE STORE #R285",
    amount=Decimal("127.49"),
    payer="Jordyn",
    source="Chase Bank"
)

# Update review decision
review_system.update_review_decision(
    review_id=review_id,
    category=TransactionCategory.PERSONAL,
    allowed_amount=Decimal("0.00"),
    notes="Personal purchase - new laptop"
)
```

**Methods:**

- `add_transaction_for_review(date, description, amount, payer, source, category=None, allowed_amount=None, notes=None)`
  - Adds a transaction to the review database
  - **Returns:** int - Review ID

- `update_review_decision(review_id, category, allowed_amount, notes=None)`
  - Updates an existing review decision
  - **Returns:** None

- `get_pending_transactions(limit=None)`
  - Gets transactions awaiting review
  - **Returns:** List[Dict] of pending transactions

- `get_review_decision(review_id)`
  - Gets existing review decision
  - **Returns:** Dict with category, amount, notes, status

- `export_decisions()`
  - Exports all review decisions
  - **Returns:** List[Dict] of all decisions

#### `TransactionCategory`

Enumeration of transaction categories for review.

```python
from src.review.manual_review_system import TransactionCategory

# Available categories:
TransactionCategory.EXPENSE      # Shared expenses
TransactionCategory.RENT         # Monthly rent
TransactionCategory.SETTLEMENT   # Zelle/Venmo transfers
TransactionCategory.PERSONAL     # Individual purchases
```

#### `ReviewStatus`

Enumeration of review statuses.

```python
from src.review.manual_review_system import ReviewStatus

# Available statuses:
ReviewStatus.PENDING     # Awaiting review
ReviewStatus.REVIEWED    # Review completed
ReviewStatus.SKIPPED     # Review skipped
```

### `src.utils.data_loader`

Utilities for loading and processing CSV data files.

#### Functions

- `load_expense_history(file_path, encoding_override=None)`
  - Loads consolidated expense history CSV
  - **Parameters:**
    - `file_path` (str): Path to CSV file
    - `encoding_override` (str, optional): Force specific encoding
  - **Returns:** pandas.DataFrame with processed data
  - **Raises:** FileNotFoundError, UnicodeDecodeError

- `detect_encoding(file_path)`
  - Automatically detects file encoding
  - **Parameters:**
    - `file_path` (str): Path to file
  - **Returns:** str - Detected encoding

- `clean_currency_amount(amount_str)`
  - Converts currency string to Decimal
  - **Parameters:**
    - `amount_str` (str): Currency string (e.g., "$123.45")
  - **Returns:** Decimal - Cleaned amount

## GUI Classes

### `src.review.visual_review_gui`

Visual GUI application for transaction review.

#### `TransactionReviewGUI`

Main GUI application class.

```python
from src.review.visual_review_gui import TransactionReviewGUI

# Launch GUI
app = TransactionReviewGUI("data/phase5_manual_reviews.db")
app.run()
```

**Methods:**

- `__init__(review_db_path)`
  - Initializes GUI application
  - **Parameters:**
    - `review_db_path` (str): Path to review database

- `run()`
  - Starts the GUI main loop
  - **Returns:** None

- `load_pending_transactions()`
  - Loads transactions needing review
  - **Returns:** None

## Error Handling

### Common Exceptions

- `ValueError`: Invalid parameters or accounting invariant violations
- `FileNotFoundError`: Missing data files or database
- `UnicodeDecodeError`: File encoding issues
- `sqlite3.DatabaseError`: Database access problems

### Error Recovery

```python
try:
    reconciler.run_reconciliation()
except ValueError as e:
    print(f"Validation error: {e}")
    # Handle invalid data
except FileNotFoundError as e:
    print(f"Missing file: {e}")
    # Handle missing files
```

## Best Practices

### Database Management

```python
# Always use absolute paths for databases
db_path = os.path.abspath("data/phase5_manual_reviews.db")
review_system = ManualReviewSystem(db_path)

# Close connections when done
review_system.close()  # If implemented
```

### Transaction Processing

```python
# Validate amounts before processing
if amount <= 0:
    raise ValueError("Amount must be positive")

# Use Decimal for currency calculations
from decimal import Decimal
amount = Decimal("123.45")  # Not float(123.45)

# Handle timezone-aware dates
from datetime import datetime, timezone
date = datetime.now(timezone.utc)
```

### Error Handling

```python
# Always validate data before processing
def safe_process_transaction(data):
    try:
        # Validate required fields
        required = ['date', 'amount', 'description', 'payer']
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Process transaction
        engine.post_expense(**data)
        
    except Exception as e:
        logger.error(f"Transaction processing failed: {e}")
        raise
```

## Examples

### Complete Reconciliation Workflow

```python
from src.core.reconciliation_engine import GoldStandardReconciler, ReconciliationMode
from src.review.manual_review_system import ManualReviewSystem
from decimal import Decimal
from datetime import datetime

# 1. Initialize reconciler
reconciler = GoldStandardReconciler(
    mode=ReconciliationMode.FROM_BASELINE,
    baseline_date=datetime(2024, 9, 30),
    baseline_amount=Decimal('1577.08'),
    baseline_who_owes='Jordyn owes Ryan'
)

# 2. Run reconciliation
reconciler.run_reconciliation(
    phase5_start=datetime(2024, 10, 1),
    phase5_end=datetime(2024, 12, 31)
)

# 3. Handle manual reviews if needed
if reconciler.manual_review_items:
    review_system = ManualReviewSystem("data/phase5_manual_reviews.db")
    
    for item in reconciler.manual_review_items:
        review_system.add_transaction_for_review(
            date=item['date'],
            description=item['description'],
            amount=item['amount'],
            payer=item['payer'],
            source=item['source']
        )
    
    print(f"Added {len(reconciler.manual_review_items)} items for review")

# 4. Export results
reconciler.export_results()
print("Reconciliation complete - check output/gold_standard/")
```

### Custom Transaction Processing

```python
from src.core.accounting_engine import AccountingEngine
from decimal import Decimal
from datetime import datetime

# Initialize engine
engine = AccountingEngine()

# Process various transaction types
transactions = [
    {
        'type': 'expense',
        'date': datetime(2024, 10, 15),
        'payer': 'Jordyn',
        'ryan_share': Decimal('25.00'),
        'jordyn_share': Decimal('25.00'),
        'description': 'Shared dinner'
    },
    {
        'type': 'rent',
        'date': datetime(2024, 10, 1),
        'payer': 'Jordyn',
        'ryan_share': Decimal('1000.00'),
        'jordyn_share': Decimal('1000.00'),
        'description': 'October rent'
    },
    {
        'type': 'settlement',
        'date': datetime(2024, 10, 20),
        'payer': 'Ryan',
        'amount': Decimal('500.00'),
        'description': 'Zelle payment'
    }
]

# Process transactions
for txn in transactions:
    if txn['type'] == 'expense':
        engine.post_expense(
            date=txn['date'],
            payer=txn['payer'],
            ryan_share=txn['ryan_share'],
            jordyn_share=txn['jordyn_share'],
            description=txn['description']
        )
    elif txn['type'] == 'rent':
        engine.post_rent(
            date=txn['date'],
            payer=txn['payer'],
            ryan_share=txn['ryan_share'],
            jordyn_share=txn['jordyn_share'],
            description=txn['description']
        )
    elif txn['type'] == 'settlement':
        engine.post_settlement(
            date=txn['date'],
            payer=txn['payer'],
            amount=txn['amount'],
            description=txn['description']
        )

# Get final balance
balance = engine.get_current_balance()
print(f"Final balance: {balance[0]} ${balance[1]}")

# Export audit trail
audit_trail = engine.export_audit_trail()
print(f"Processed {len(audit_trail)} transactions")
```

---

**Last Updated:** July 31, 2025  
**Version:** 1.0.0