# Getting Started Guide

## Prerequisites

Before running the Financial Reconciliation System, ensure you have:

1. **Python 3.8 or higher** installed
2. **pip** package manager
3. **Git** for cloning the repository
4. **Excel or Google Sheets** (optional, for manual review)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourorg/financial-reconciliation.git
cd financial-reconciliation
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## First Run

### 1. Prepare Your Data

Place your data files in the appropriate directories:

- **Legacy Data (Phase 4)**: Copy to `test-data/legacy/`
  - Consolidated_Expense_History_*.csv
  - Consolidated_Rent_Allocation_*.csv
  - Zelle_From_Jordyn_Final.csv

- **Bank Exports (Phase 5+)**: Copy to `test-data/bank-exports/`
  - BALANCE_*.csv files
  - Bank statement exports

### 2. Run Reconciliation

For your first run, use the baseline mode (recommended):

```bash
python bin/run-with-review --mode from_baseline
```

This will:
1. Load historical data through Sept 30, 2024
2. Process Phase 5+ bank data from Oct 1, 2024 onwards
3. Flag transactions needing manual review
4. Generate comprehensive reports

### 3. Review Flagged Transactions

If transactions need manual review, you'll see a menu:

```
156 transactions need manual review.
Options:
1. Launch Visual GUI Review (Recommended)
2. Run command-line review interface
3. Skip manual review (use defaults)
4. Exit

Select option (1-4):
```

Choose your preferred review method:
- **1**: Visual GUI with keyboard shortcuts (Recommended)
- **2**: Interactive command-line review
- **3**: Skip review and use defaults
- **4**: Exit to handle manually later

## Review Methods

### Visual GUI Review (Recommended)

The Visual GUI provides an intuitive interface with:

- **Transaction Details**: Clear display of date, description, amount, payer
- **Category Buttons**: Quick selection with keyboard shortcuts (E, R, S, P)
- **Amount Adjustment**: Easy editing with quick-set buttons (Full, Half, Zero)
- **Notes Field**: Add detailed comments for each transaction
- **Progress Tracking**: Visual progress bar and session statistics
- **Keyboard Shortcuts**: Efficient review with hotkeys

**Key Shortcuts:**
- E: Expense, R: Rent, S: Settlement, P: Personal
- D: Save & Next, A: Previous, Shift+S: Skip
- F1: Help

Launch directly: `python bin/review-gui`

### Command-Line Review

When you choose command-line review, you'll see each transaction:

```
Transaction 1/156
Date: 2024-10-15
Description: APPLE STORE #R285
Amount: $127.49
Payer: Jordyn

Category? (expense/rent/settlement/personal/skip):
```

### Spreadsheet Review

For bulk review, export to CSV:

```bash
python bin/run-with-review --export-review
```

This creates a CSV file you can edit in Excel:
1. Open the exported CSV
2. Fill in the `category` column
3. Save the file
4. Import back into the system

## Understanding the Output

After reconciliation completes, check the `output/gold_standard/` directory:

### Key Files

1. **summary.json** - Machine-readable results
   - Current balance
   - Transaction counts
   - Processing statistics

2. **reconciliation_report.txt** - Human-readable report
   - Detailed balance calculation
   - Transaction summaries
   - Data quality notes

3. **audit_trail.csv** - Complete transaction log
   - Every transaction processed
   - Running balances
   - Categorization details

4. **manual_review_required.csv** - Transactions needing attention
   - Missing categories
   - Data quality issues
   - Ambiguous descriptions

## Common Tasks

### Process New Bank Data

When you receive new bank statements:

1. Copy CSV files to `test-data/bank-exports/`
2. Run reconciliation:
   ```bash
   python bin/run-with-review --mode from_baseline
   ```
3. Review any new transactions flagged

### Check Current Balance

For a quick balance check:

```bash
python bin/financial-reconciliation --mode from_baseline --summary-only
```

### Export All Data

To export everything for external analysis:

```bash
python bin/run-with-review --export-all
```

## Troubleshooting

### "File not found" Error

Ensure your data files are in the correct directories:
- Legacy data → `test-data/legacy/`
- Bank exports → `test-data/bank-exports/`

### "Database locked" Error

The review database may be in use. Close any other instances of the program.

### Encoding Errors

The system automatically handles various encodings. If issues persist:
1. Check `output/gold_standard/data_quality_issues.csv`
2. Verify your CSV files aren't corrupted

### Balance Mismatch

If balances don't match expectations:
1. Review `output/gold_standard/audit_trail.csv`
2. Check manual review decisions in the database
3. Verify no transactions were skipped

## Next Steps

Once comfortable with basic usage:

1. **Set up automated runs** - Schedule regular reconciliation
2. **Learn pattern matching** - Speed up manual review
3. **Explore the web interface** - Browser-based review option
4. **Create custom reports** - Extend the reporting system

For advanced usage, see the [Advanced Guide](ADVANCED_USAGE.md).

---

**Need Help?** Check the [FAQ](FAQ.md) or open an issue on GitHub.