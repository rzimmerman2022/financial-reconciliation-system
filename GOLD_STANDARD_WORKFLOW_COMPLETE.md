# Gold Standard Financial Reconciliation System - Complete Workflow Documentation

## Table of Contents
1. [Executive Overview](#executive-overview)
2. [System Architecture](#system-architecture)
3. [Data Sources and Quality](#data-sources-and-quality)
4. [Complete Workflow](#complete-workflow)
5. [Audit Checks and Validations](#audit-checks-and-validations)
6. [Manual Review Process](#manual-review-process)
7. [Accounting Engine Details](#accounting-engine-details)
8. [Error Handling and Recovery](#error-handling-and-recovery)
9. [Output and Reporting](#output-and-reporting)
10. [Troubleshooting Guide](#troubleshooting-guide)

## Executive Overview

The Gold Standard Financial Reconciliation System is a production-ready solution for reconciling shared expenses between Ryan and Jordyn. It implements double-entry bookkeeping, comprehensive audit trails, and handles both historical manually-reviewed data (Phase 4) and new raw bank data (Phase 5+) requiring manual review.

### Key Achievements
- **Fixed Critical Bugs**: Resolved $6,759.16 double-counting error from previous systems
- **Proper Field Usage**: Correctly uses `allowed_amount` field for Phase 4 data
- **Manual Review Integration**: Seamless handling of Phase 5+ bank data
- **Complete Audit Trail**: Every transaction tracked with full history
- **Data Quality Handling**: Graceful management of encoding errors and missing data

### System Modes
1. **FROM_SCRATCH**: Processes all transactions from the beginning
2. **FROM_BASELINE**: Continues from Phase 4 ending balance ($1,577.08 as of Sept 30, 2024)

## System Architecture

### Core Components

```
gold_standard_reconciliation.py
├── GoldStandardReconciler (Main orchestrator)
│   ├── load_phase4_data()      # Historical data with allowed_amount
│   ├── load_bank_data()        # Raw bank CSVs (Phase 5+)
│   ├── process_transaction()   # Core processing logic
│   └── generate_reports()      # Output generation
│
├── accounting_engine.py
│   ├── AccountingEngine        # Double-entry bookkeeping
│   ├── post_transaction()      # Debit/credit posting
│   └── validate_invariants()   # Balance validation
│
├── description_decoder.py
│   ├── DescriptionDecoder      # Pattern recognition
│   └── decode_transaction()    # Special handling rules
│
├── manual_review_system.py
│   ├── ManualReviewSystem      # SQLite-based review tracking
│   ├── InteractiveReviewer     # User interface
│   └── ReviewDatabase          # Persistent storage
│
└── run_reconciliation_with_review.py
    └── ReconciliationWithReview # Orchestrates full workflow
```

### Data Flow Diagram

```
[Raw Data Sources]
    ├── Phase 4: Consolidated Expense History (with allowed_amount)
    │   └── [Direct Processing] → [Accounting Engine]
    │
    └── Phase 5+: Bank CSVs (raw data)
        └── [Manual Review Required] → [Review System] → [Accounting Engine]
                                            ↓
                                    [User Decision]
                                            ↓
                                    [Apply Reviews]
```

## Data Sources and Quality

### Phase 4 Data (Through September 30, 2024)
- **File**: `Consolidated_Expense_History_20250622.csv`
- **Key Fields**:
  - `allowed_amount`: Manually reviewed amount to use
  - `actual_amount`: Original transaction amount
  - `description`: Manual notes about the transaction
- **Quality**: Pre-validated with manual review decisions

### Phase 5+ Data (October 1, 2024 onwards)
- **Ryan's Sources**:
  - `Ryan_MonarchMoney_*.csv` (Primary)
  - `Ryan_RocketMoney_*.csv` (Secondary)
- **Jordyn's Sources**:
  - `Jordyn_Chase_*.csv` (Has encoding issues)
  - `Jordyn_WellsFargo_*.csv`
  - `Jordyn_Discover_*.csv`
- **Quality Issues**:
  - 156 transactions with missing amounts due to encoding errors
  - Unicode replacement characters (�) in Chase data
  - Missing data after March 13, 2025 for Chase

### Data Quality Tracking

```python
class DataQualityIssue(Enum):
    MISSING_AMOUNT = "missing_amount"
    INVALID_DATE = "invalid_date"
    ENCODING_ERROR = "encoding_error"
    SUSPICIOUS_AMOUNT = "suspicious_amount"
    DUPLICATE_TRANSACTION = "duplicate"
```

## Complete Workflow

### Phase 1: Initial Reconciliation

```bash
python gold_standard_reconciliation.py --mode from_baseline
```

#### Step 1.1: Initialize System
```python
reconciler = GoldStandardReconciler(
    mode=ReconciliationMode.FROM_BASELINE,
    baseline_date=datetime(2024, 9, 30),
    baseline_amount=Decimal('1577.08'),
    baseline_who_owes='Jordyn owes Ryan'
)
```

#### Step 1.2: Load Phase 4 Data
1. Read `Consolidated_Expense_History_20250622.csv`
2. Map columns: `allowed_amount` → `amount`
3. Detect personal expenses: `allowed_amount == "$ -"`
4. Flag manual adjustments: `allowed_amount != actual_amount`
5. Set `has_manual_review = True`

#### Step 1.3: Load Phase 5+ Bank Data
1. Read all bank CSV files with date filtering
2. Try multiple encodings: ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
3. Clean amount fields: Remove $, commas
4. Validate dates and amounts
5. Set `has_manual_review = False`
6. Flag for manual review

#### Step 1.4: Remove Duplicates
1. **Exact Duplicates**: Same date, amount, description, payer
2. **Near Duplicates**: Same date, amount, similar description (first 20 chars)
3. Hash-based detection using MD5

#### Step 1.5: Process Transactions
For each transaction:
```python
if has_manual_review:
    _process_reviewed_transaction()  # Phase 4
else:
    _process_unreviewed_transaction()  # Phase 5+
```

### Phase 2: Manual Review Process

```bash
python run_reconciliation_with_review.py
```

#### Step 2.1: Export for Review
1. Identify transactions needing review
2. Create entries in SQLite database
3. Generate review items with metadata

#### Step 2.2: Review Interface Options
1. **Spreadsheet Export**: For bulk review
2. **Web Interface**: Interactive browser-based
3. **Skip Review**: Use auto-categorization

#### Step 2.3: Review Decisions
For each transaction, user specifies:
- **Category**: rent, utilities, groceries, personal, etc.
- **Split Type**: 50/50, custom, full to one person
- **Allowed Amount**: Override transaction amount if needed
- **Is Personal**: Exclude from shared expenses
- **Notes**: Additional context

#### Step 2.4: Save Review Decisions
```sql
UPDATE manual_reviews SET
    status = 'completed',
    category = ?,
    split_type = ?,
    allowed_amount = ?,
    is_personal = ?,
    notes = ?,
    reviewed_by = ?,
    reviewed_date = ?
WHERE review_id = ?
```

### Phase 3: Final Reconciliation with Reviews

#### Step 3.1: Load Review Decisions
```python
completed_reviews = review_system.export_reviews(
    status=ReviewStatus.COMPLETED
)
```

#### Step 3.2: Apply Reviews to Transactions
1. Match transactions to review decisions
2. Override amounts with `allowed_amount`
3. Apply split logic based on `split_type`
4. Exclude personal expenses

#### Step 3.3: Re-run Reconciliation
Process all transactions with review decisions applied

## Audit Checks and Validations

### Transaction-Level Validations

#### 1. Date Validation
```python
df['date'] = pd.to_datetime(df['date'], errors='coerce')
invalid_dates = df['date'].isna().sum()
if invalid_dates > 0:
    record_data_quality_issue(DataQualityIssue.INVALID_DATE)
```

#### 2. Amount Validation
```python
# Check for missing amounts
missing_amounts = df['amount'].isna().sum()

# Flag suspicious amounts (>$10,000)
suspicious = df[df['amount'] > 10000]
for row in suspicious:
    record_data_quality_issue(DataQualityIssue.SUSPICIOUS_AMOUNT)
```

#### 3. Encoding Error Detection
```python
if encoding_fixes:
    for bad_char, replacement in encoding_fixes.items():
        df['amount'] = df['amount'].str.replace(bad_char, replacement)
```

### Accounting-Level Validations

#### 1. Double-Entry Invariants
```python
def validate_invariants(self):
    """Ensure accounting equation always balances"""
    # Assets = Liabilities + Equity
    ryan_net = self.accounts['ryan']['assets'] - self.accounts['ryan']['liabilities']
    jordyn_net = self.accounts['jordyn']['assets'] - self.accounts['jordyn']['liabilities']
    
    # Ryan's position must equal negative of Jordyn's position
    assert ryan_net == -jordyn_net, f"Invariant violated: {ryan_net} != -{jordyn_net}"
```

#### 2. Transaction Posting Validation
```python
def _post_transaction(self, date, description, debit_account, credit_account, amount):
    """Every debit must have an equal credit"""
    # Record debit
    self._record_entry(date, description, debit_account, 'debit', amount)
    
    # Record credit
    self._record_entry(date, description, credit_account, 'credit', amount)
    
    # Validate immediately
    self.validate_invariants()
```

#### 3. Balance Consistency Checks
- Running balance calculated after each transaction
- Balance changes match transaction amounts
- No transactions can create negative receivables

### Reconciliation-Level Validations

#### 1. Baseline Consistency
```python
if self.mode == ReconciliationMode.FROM_BASELINE:
    # Verify baseline matches expected
    assert self.baseline_amount == Decimal('1577.08')
    assert self.baseline_date == datetime(2024, 9, 30)
```

#### 2. Transaction Completeness
- All date ranges covered
- No gaps in transaction sequence
- All sources processed

#### 3. Manual Review Completeness
```python
pending_reviews = review_system.get_pending_reviews()
if not pending_reviews.empty:
    logger.warning(f"{len(pending_reviews)} transactions still pending review")
```

## Manual Review Process

### Auto-Categorization Rules

```python
def _categorize_transaction(self, row):
    """Auto-categorize based on patterns"""
    description = row['description'].lower()
    
    # Rent patterns
    if any(keyword in description for keyword in ['rent', 'san palmas', 'yardi']):
        return 'rent'
    
    # Utilities
    if any(keyword in description for keyword in ['edison', 'gas company', 'spectrum']):
        return 'utilities'
    
    # Groceries
    if any(keyword in description for keyword in ['vons', 'ralphs', 'trader joe']):
        return 'groceries'
    
    # Unknown - requires manual review
    return 'unknown'
```

### Review Database Schema

```sql
CREATE TABLE manual_reviews (
    review_id INTEGER PRIMARY KEY,
    transaction_hash TEXT UNIQUE NOT NULL,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    payer TEXT NOT NULL,
    source TEXT,
    status TEXT DEFAULT 'pending',
    category TEXT,
    split_type TEXT,
    ryan_share REAL,
    jordyn_share REAL,
    allowed_amount REAL,
    is_personal INTEGER DEFAULT 0,
    notes TEXT,
    reviewed_by TEXT,
    reviewed_date TEXT,
    created_date TEXT NOT NULL,
    updated_date TEXT
);

CREATE TABLE review_history (
    history_id INTEGER PRIMARY KEY,
    review_id INTEGER NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    changed_by TEXT NOT NULL,
    changed_date TEXT NOT NULL,
    FOREIGN KEY (review_id) REFERENCES manual_reviews(review_id)
);
```

### Review Workflow States

```
PENDING → IN_PROGRESS → COMPLETED
                    ↓
                DISPUTED → DEFERRED
```

## Accounting Engine Details

### Account Structure

```python
accounts = {
    'ryan': {
        'assets': Decimal('0'),      # Ryan's receivables
        'liabilities': Decimal('0')   # Ryan's payables
    },
    'jordyn': {
        'assets': Decimal('0'),      # Jordyn's receivables  
        'liabilities': Decimal('0')   # Jordyn's payables
    }
}
```

### Transaction Types

#### 1. Shared Expense (50/50 Split)
```python
# Ryan pays $100 for groceries
post_transaction(
    date, "Groceries",
    debit="jordyn_receivable",   # Jordyn owes Ryan $50
    credit="ryan_payable",       # Ryan owed by Jordyn $50
    amount=Decimal('50.00')
)
```

#### 2. Personal Expense
```python
# Ryan's personal expense - no accounting entry
balance_change = Decimal('0')
notes = "Personal expense for Ryan"
```

#### 3. Settlement Payment
```python
# Jordyn pays Ryan $500
post_transaction(
    date, "Zelle payment",
    debit="ryan_payable",        # Reduce Ryan's receivable
    credit="jordyn_receivable",  # Reduce Jordyn's payable
    amount=Decimal('500.00')
)
```

### Balance Calculation

```python
def get_current_balance(self):
    ryan_net = self.accounts['ryan']['assets'] - self.accounts['ryan']['liabilities']
    jordyn_net = self.accounts['jordyn']['assets'] - self.accounts['jordyn']['liabilities']
    
    if ryan_net > 0:
        return {
            'amount': ryan_net,
            'who_owes': 'Jordyn owes Ryan',
            'ryan_receivable': ryan_net,
            'jordyn_receivable': Decimal('0')
        }
    else:
        return {
            'amount': abs(ryan_net),
            'who_owes': 'Ryan owes Jordyn',
            'ryan_receivable': Decimal('0'),
            'jordyn_receivable': abs(ryan_net)
        }
```

## Error Handling and Recovery

### Encoding Error Recovery

```python
# Special handling for Chase encoding issues
CHASE_ENCODING_FIXES = {
    '\ufffd': '',  # Unicode replacement character
    '�': '',       # Common rendering of replacement character
}
```

### Missing Amount Recovery

```python
if pd.isna(row['amount']):
    # Add to manual review with context
    manual_review_items.append({
        'date': row['date'],
        'description': row['description'],
        'source': 'Jordyn_Chase',
        'issue': 'Missing amount - encoding error',
        'suggested_amount': estimate_from_description(row['description'])
    })
```

### Duplicate Transaction Handling

```python
# Generate hash for near-duplicate detection
tx_hash = hashlib.md5(
    f"{date}_{amount:.2f}_{description[:20]}".encode()
).hexdigest()

# Keep first occurrence only
df.drop_duplicates(subset=['tx_hash'], keep='first')
```

### Transaction Rollback

```python
try:
    engine.post_transaction(...)
    engine.validate_invariants()
except AssertionError as e:
    logger.error(f"Invariant violation: {e}")
    # Transaction not posted - system remains consistent
```

## Output and Reporting

### Directory Structure

```
output/
├── gold_standard/
│   ├── summary.json              # Machine-readable summary
│   ├── reconciliation_report.txt # Human-readable report
│   ├── audit_trail.csv          # Every transaction with balance
│   ├── accounting_ledger.csv    # Double-entry ledger
│   ├── manual_review_required.csv
│   └── data_quality_issues.csv
│
└── gold_standard_with_manual_review/
    └── [same structure after reviews applied]
```

### Summary JSON Format

```json
{
  "metadata": {
    "version": "GOLD STANDARD 1.0.0",
    "generated": "2025-07-29T15:12:56.035961",
    "mode": "from_baseline"
  },
  "final_balance": {
    "amount": 8595.87,
    "who_owes_whom": "Ryan owes Jordyn",
    "ryan_receivable": -1768.19,
    "jordyn_receivable": 6827.68
  },
  "statistics": {
    "transactions_processed": 283,
    "manual_review_required": 1,
    "data_quality_issues": 168,
    "duplicates_found": 2,
    "by_category": {
      "expense": 210,
      "income": 10,
      "personal": 59
    }
  }
}
```

### Audit Trail CSV Format

```csv
date,description,payer,amount,category,action,balance_change,running_balance,ryan_balance,jordyn_balance,notes
2024-10-01,Groceries,Ryan,50.00,expense,split_50_50,25.00,1602.08,1602.08,0.00,Ryan paid - 50/50 split
```

### Reconciliation Report Sections

1. **Executive Summary**
   - Final balance and direction
   - Transaction counts
   - Data quality summary

2. **Transaction Breakdown**
   - By category
   - By source
   - By payer

3. **Special Processing**
   - Personal expenses excluded
   - Manual adjustments applied
   - Duplicates removed

4. **Balance Details**
   - Current receivables
   - Net positions
   - Validation status

5. **Data Quality Report**
   - Missing amounts
   - Encoding errors
   - Suspicious transactions

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. Unicode/Encoding Errors

**Symptom**: 
```
UnicodeDecodeError: 'utf-8' codec can't decode byte...
```

**Solution**:
```python
# System automatically tries multiple encodings
encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252']
```

#### 2. Missing Amounts in Chase Data

**Symptom**:
```
Found 156 missing amounts in Jordyn_Chase
```

**Solution**:
1. Check `output/gold_standard/manual_review_required.csv`
2. Manually input amounts based on transaction descriptions
3. Use manual review system to set allowed amounts

#### 3. Balance Mismatch After Manual Review

**Symptom**:
```
AssertionError: Invariant violated: 1000.00 != -1000.00
```

**Solution**:
1. Check review decisions for data entry errors
2. Verify split percentages sum to 100%
3. Ensure settlement transactions have matching amounts

#### 4. Duplicate Transactions

**Symptom**:
```
Removed 45 near-duplicates
```

**Solution**:
- Review `audit_trail.csv` to verify correct duplicates removed
- Adjust duplicate detection threshold if needed

#### 5. Phase 4/5 Data Confusion

**Symptom**:
```
Processing historical data as new bank data
```

**Solution**:
- Verify date ranges:
  - Phase 4: Through Sept 30, 2024
  - Phase 5: Oct 1, 2024 onwards
- Check `has_manual_review` flag

### Performance Optimization

#### For Large Datasets

```python
# Process in batches
BATCH_SIZE = 1000
for i in range(0, len(df), BATCH_SIZE):
    batch = df.iloc[i:i+BATCH_SIZE]
    process_batch(batch)
```

#### Memory Management

```python
# Use iterators for large files
for chunk in pd.read_csv(file, chunksize=10000):
    process_chunk(chunk)
```

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('reconciliation_debug.log'),
        logging.StreamHandler()
    ]
)
```

## Best Practices

### 1. Always Run Validation
```bash
python test_gold_standard.py
```

### 2. Backup Before Major Operations
```bash
cp -r output/ output_backup_$(date +%Y%m%d_%H%M%S)/
cp phase5_manual_reviews.db phase5_manual_reviews_backup_$(date +%Y%m%d_%H%M%S).db
```

### 3. Review Audit Trail
- Check `audit_trail.csv` for unexpected patterns
- Verify running balances are monotonic
- Ensure all transactions have valid categories

### 4. Document Manual Decisions
- Always add notes when overriding amounts
- Explain why expenses are marked personal
- Document any unusual split arrangements

### 5. Regular Reconciliation
- Run monthly to catch issues early
- Complete manual reviews promptly
- Archive outputs for historical reference

## Conclusion

The Gold Standard Financial Reconciliation System provides a robust, auditable solution for shared expense tracking. With proper manual review of Phase 5+ data and attention to data quality issues, it produces accurate, defensible results with complete transparency.

For questions or issues, refer to:
- `AI_HANDOVER_CONTEXT.md` - Technical implementation details
- `CRITICAL_RENT_RULES.md` - Business logic for rent handling
- `test_gold_standard.py` - Unit tests demonstrating usage

---
Generated: July 30, 2025  
Version: GOLD STANDARD 1.0.0