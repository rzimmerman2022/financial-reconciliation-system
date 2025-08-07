# API Reference - v4.0.4

## Overview

The Financial Reconciliation System provides a comprehensive Python API for programmatic access to all reconciliation, review, and accounting functionality. This reference covers all public classes, methods, and interfaces.

**Last Updated**: 2025-08-07  
**Version**: 4.0.4

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
TransactionType.RENT         # Monthly rent
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

Manual review system for transaction decisions.

#### `ManualReviewSystem`

Database-backed system for storing and retrieving transaction review decisions.

```python
from src.review.manual_review_system import ManualReviewSystem
import pandas as pd

# Initialize review system
review_system = ManualReviewSystem("data/phase5_manual_reviews.db")

# Get pending reviews
pending = review_system.get_pending_reviews()
# Returns pandas DataFrame with pending transactions

# Save a decision
review_system.save_decision(
    review_id=1,
    decision="assign",
    payer="Ryan",
    notes="Personal expense"
)

# Get review statistics
stats = review_system.get_review_stats()
```

**Methods:**

- `add_for_review(transaction_dict, reason="Manual review required")`
  - Adds a transaction for manual review
  - **Parameters:**
    - `transaction_dict` (dict): Transaction data with date, description, amount, payer, source
    - `reason` (str): Reason for review
  - **Returns:** int - Review ID

- `get_pending_reviews()`
  - Gets all pending transactions as DataFrame
  - **Returns:** pandas.DataFrame with pending reviews

- `save_decision(review_id, decision, payer=None, notes="")`
  - Saves a review decision
  - **Parameters:**
    - `review_id` (int): ID of review
    - `decision` (str): "assign", "split", or "skip"
    - `payer` (str, optional): "Ryan" or "Jordyn" for assign decisions
    - `notes` (str): Optional notes
  - **Returns:** None

- `get_review_stats()`
  - Gets review statistics
  - **Returns:** Dict with counts by status

- `export_decisions(output_path)`
  - Exports all decisions to CSV
  - **Parameters:**
    - `output_path` (str): Path for CSV export
  - **Returns:** None

### `src.review.modern_visual_review_gui`

Modern Material Design GUI for transaction review.

#### `ModernTransactionReviewGUI`

Visual interface with keyboard shortcuts and auto-save.

```python
from src.review.modern_visual_review_gui import ModernTransactionReviewGUI

# Launch GUI
gui = ModernTransactionReviewGUI("data/phase5_manual_reviews.db")
gui.run()
```

**Features:**
- Material Design interface
- Keyboard shortcuts (1-4 for decisions)
- Auto-save functionality
- Progress tracking
- Session statistics
- Animation effects

**Methods:**

- `__init__(review_db_path="data/phase5_manual_reviews.db")`
  - Initializes GUI with database path
  
- `run()`
  - Starts the GUI event loop

### `src.loaders`

Data loaders for various bank formats.

#### Bank-Specific Loaders

```python
from src.loaders.chase_loader import ChaseLoader
from src.loaders.wellsfargo_loader import WellsFargoLoader
from src.loaders.apple_card_loader import AppleCardLoader
from src.loaders.monarch_loader import MonarchMoneyLoader

# Example usage
loader = ChaseLoader()
transactions = loader.load("data/chase_export.csv")
```

**Common Interface:**
- `load(file_path)` - Loads and parses bank export file
- Returns: pandas.DataFrame with standardized columns

**Supported Banks:**
- Chase Bank (handles encoding issues)
- Wells Fargo
- Apple Card
- MonarchMoney
- Wave Accounting

### `src.processors`

Data processing and report generation.

#### `ExcelReportGenerator`

Generates comprehensive Excel reports.

```python
from src.processors.excel_report_generator import ExcelReportGenerator

generator = ExcelReportGenerator()
generator.generate_comprehensive_report(
    reconciliation_results,
    manual_review_items,
    data_quality_issues,
    output_path="output/reports/reconciliation_report.xlsx"
)
```

**Features:**
- Multiple worksheets
- Conditional formatting
- Charts and visualizations
- Pivot tables
- Data quality reporting

## Web API

### Flask REST API

RESTful API for web access.

```python
from src.web.app import create_app

app = create_app()
app.run(host='0.0.0.0', port=5000)
```

### Endpoints

#### `GET /api/status`
System health check.

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "last_reconciliation": "2025-07-31T14:16:55"
}
```

#### `POST /api/reconcile`
Trigger reconciliation.

**Request:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "mode": "from_baseline"
}
```

#### `GET /api/reviews/pending`
Get pending reviews.

**Response:**
```json
{
  "count": 2,
  "reviews": [
    {
      "id": 1,
      "date": "2024-10-31",
      "description": "Large transfer",
      "amount": 8000.00,
      "payer": "Ryan",
      "source": "MonarchMoney"
    }
  ]
}
```

#### `POST /api/reviews/{id}/decision`
Save review decision.

**Request:**
```json
{
  "decision": "assign",
  "payer": "Ryan",
  "notes": "Personal expense"
}
```

## Utilities

### Data Quality

```python
from src.utils.data_quality import DataQualityChecker

checker = DataQualityChecker()
issues = checker.check_transactions(df)
# Returns list of quality issues
```

### Date Handling

```python
from src.utils.date_utils import parse_flexible_date, normalize_date_range

# Parse various date formats
date = parse_flexible_date("2024-01-15")
date = parse_flexible_date("01/15/2024")
date = parse_flexible_date("15/01/2024")

# Normalize date ranges
start, end = normalize_date_range(start_date, end_date)
```

## Error Handling

### Exception Hierarchy

```python
# Base exception
class ReconciliationError(Exception):
    pass

# Specific exceptions
class DataLoadError(ReconciliationError):
    pass

class ValidationError(ReconciliationError):
    pass

class AccountingError(ReconciliationError):
    pass
```

### Error Recovery

```python
try:
    engine.run_reconciliation()
except DataLoadError as e:
    logger.error(f"Failed to load data: {e}")
    # Handle missing or corrupt data
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    # Handle invalid transactions
except AccountingError as e:
    logger.error(f"Accounting invariant violated: {e}")
    # Critical error - investigate immediately
```

## Configuration

### Loading Configuration

```python
import yaml

with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Access settings
batch_size = config['processing']['batch_size']
tolerance = config['reconciliation']['amount_tolerance']
```

### Environment Variables

```python
import os

# Override with environment variables
db_path = os.getenv('RECON_DB_PATH', 'data/reconciliation.db')
debug = os.getenv('RECON_DEBUG', 'false').lower() == 'true'
```

## Best Practices

### Transaction Processing

```python
from decimal import Decimal

# Always use Decimal for money
amount = Decimal('123.45')  # Not float

# Validate before processing
if amount <= 0:
    raise ValueError("Amount must be positive")

# Use consistent date handling
from datetime import datetime
date = datetime.strptime(date_str, '%Y-%m-%d')
```

### Database Operations

```python
# Use context managers
with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

# Always use parameterized queries
cursor.execute(
    "INSERT INTO reviews (date, amount) VALUES (?, ?)",
    (date, amount)
)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log at appropriate levels
logger.debug("Processing transaction: %s", txn_id)
logger.info("Reconciliation started")
logger.warning("Missing amount for transaction: %s", desc)
logger.error("Failed to load file: %s", file_path)
```

## Examples

### Complete Workflow

```python
# 1. Run reconciliation
from src.core.reconciliation_engine import GoldStandardReconciler
reconciler = GoldStandardReconciler()
reconciler.run_reconciliation()

# 2. Check for manual reviews
if reconciler.manual_review_count > 0:
    # Launch GUI
    from src.review.modern_visual_review_gui import ModernTransactionReviewGUI
    gui = ModernTransactionReviewGUI()
    gui.run()

# 3. Generate reports
from src.processors.excel_report_generator import ExcelReportGenerator
generator = ExcelReportGenerator()
generator.generate_comprehensive_report(
    reconciler.get_results(),
    "output/final_report.xlsx"
)
```

---

**Last Updated:** July 31, 2025  
**Version:** 2.0.0