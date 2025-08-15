# Troubleshooting Guide

This guide covers common issues, error messages, and solutions for the Financial Reconciliation System.

## Quick Diagnostics

### Health Check Commands

```bash
# 1. Verify Python and dependencies
python --version                    # Should be 3.8+
python -c "import tkinter; print('GUI available')"

# 2. Test core imports
python -c "from src.core.accounting_engine import AccountingEngine; print('Core engine OK')"
python -c "from src.review.manual_review_system import ManualReviewSystem; print('Review system OK')"

# 3. Check file structure
ls bin/                            # Should show executables
ls test-data/                      # Should show data directories
ls output/gold_standard/           # Should show output files

# 4. Database connectivity
python -c "
import sqlite3
conn = sqlite3.connect('data/phase5_manual_reviews.db')
print('Tables:', [row[0] for row in conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')])
conn.close()
"
```

## Common Issues

### Installation and Setup

#### Issue: `ModuleNotFoundError: No module named 'src'`

**Cause:** Python path not configured correctly.

**Solutions:**
```bash
# Option 1: Run from project root
cd /path/to/financial-reconciliation
python bin/run-with-review

# Option 2: Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/financial-reconciliation"

# Option 3: Install in development mode
python tools/setup.py develop
```

#### Issue: `ImportError: No module named 'tkinter'`

**Cause:** tkinter not installed (common on Linux).

**Solutions:**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter

# macOS (if using Homebrew Python)
brew install python-tk

# Verify installation
python -c "import tkinter; print('tkinter available')"
```

#### Issue: Virtual environment activation fails

**Cause:** Virtual environment not created properly.

**Solutions:**
```bash
# Remove corrupted venv
rm -rf venv

# Create new virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Verify activation
which python    # Should point to venv/bin/python
pip list        # Should show minimal packages
```

### Data Loading Issues

#### Issue: `FileNotFoundError: [Errno 2] No such file or directory: 'test-data/bank-exports/...'`

**Cause:** Data files not in correct location.

**Solutions:**
```bash
# 1. Check current directory structure
ls -la test-data/

# 2. Create missing directories
mkdir -p test-data/bank-exports
mkdir -p test-data/legacy
mkdir -p test-data/processed

# 3. Move data files to correct locations
# Bank exports (Phase 5+) → test-data/bank-exports/
# Legacy data (Phase 4) → test-data/legacy/

# 4. Verify file placement
ls test-data/bank-exports/
ls test-data/legacy/
```

#### Issue: `UnicodeDecodeError: 'utf-8' codec can't decode byte`

**Cause:** CSV file has unexpected encoding.

**Solutions:**
```python
# 1. Detect file encoding
python -c "
import chardet
with open('your_file.csv', 'rb') as f:
    result = chardet.detect(f.read())
    print('Detected encoding:', result['encoding'])
"

# 2. Convert file encoding
# Using iconv (Linux/macOS)
iconv -f windows-1252 -t utf-8 input.csv > output.csv

# Using Python
python -c "
with open('input.csv', 'r', encoding='windows-1252') as f:
    content = f.read()
with open('output.csv', 'w', encoding='utf-8') as f:
    f.write(content)
"
```

#### Issue: `pandas.errors.EmptyDataError: No columns to parse from file`

**Cause:** CSV file is empty or malformed.

**Solutions:**
```bash
# 1. Check file contents
head -5 your_file.csv
wc -l your_file.csv

# 2. Verify CSV structure
python -c "
import pandas as pd
df = pd.read_csv('your_file.csv', nrows=5)
print('Columns:', df.columns.tolist())
print('Shape:', df.shape)
print(df.head())
"

# 3. Fix common CSV issues
# Remove BOM (Byte Order Mark)
sed -i '1s/^\xEF\xBB\xBF//' your_file.csv

# Fix line endings
dos2unix your_file.csv
```

### Database Issues

#### Issue: `sqlite3.OperationalError: database is locked`

**Cause:** Another process is using the database.

**Solutions:**
```bash
# 1. Check for running processes
ps aux | grep python
ps aux | grep financial-reconciliation

# 2. Kill conflicting processes
pkill -f "financial-reconciliation"
pkill -f "review-gui"

# 3. Check for database locks
ls -la data/phase5_manual_reviews.db*
# Remove .db-wal and .db-shm files if present
rm -f data/phase5_manual_reviews.db-wal
rm -f data/phase5_manual_reviews.db-shm

# 4. Test database access
sqlite3 data/phase5_manual_reviews.db "SELECT count(*) FROM transactions;"
```

#### Issue: `sqlite3.OperationalError: no such table: transactions`

**Cause:** Database not initialized properly.

**Solutions:**
```python
# Initialize database manually
python -c "
from src.review.manual_review_system import ManualReviewSystem
review_system = ManualReviewSystem('data/phase5_manual_reviews.db')
print('Database initialized')
"

# Verify tables created
sqlite3 data/phase5_manual_reviews.db ".tables"
```

#### Issue: Database corruption

**Cause:** System crash or disk issues.

**Solutions:**
```bash
# 1. Check database integrity
sqlite3 data/phase5_manual_reviews.db "PRAGMA integrity_check;"

# 2. Backup existing database
cp data/phase5_manual_reviews.db data/phase5_manual_reviews.db.backup

# 3. Repair database
sqlite3 data/phase5_manual_reviews.db "VACUUM;"

# 4. If corruption severe, rebuild from backup
# (Manual review decisions may be lost)
rm data/phase5_manual_reviews.db
python bin/run-with-review --mode from_baseline
```

### GUI Issues

#### Issue: GUI won't start - `tkinter.TclError: no display name`

**Cause:** Running on headless system without display.

**Solutions:**
```bash
# Option 1: Use X11 forwarding (SSH)
ssh -X username@hostname
python bin/review-gui

# Option 2: Use virtual display (Linux)
sudo apt-get install xvfb
xvfb-run -a python bin/review-gui

# Option 3: Use web interface instead
python -m src.review.web_interface

If browser doesn’t open:
- Manually open http://localhost:5000
- Health check: http://localhost:5000/healthz → ok
```

#### Issue: GUI appears but buttons don't work

**Cause:** Event handling or focus issues.

**Solutions:**
```bash
# 1. Check for errors in console
python bin/review-gui 2>&1 | tee gui.log

# 2. Test with minimal transaction set
# Reduce database to few transactions for testing

# 3. Reset GUI settings
rm -rf ~/.config/financial-reconciliation/  # If settings exist

# 4. Use keyboard shortcuts instead of mouse
# E=Expense, R=Rent, S=Settlement, P=Personal, D=Save&Next
```

#### Issue: GUI freezes during large data loading

**Cause:** Processing too many transactions at once.

**Solutions:**
```python
# 1. Process in smaller batches
# Limit review to recent transactions first

# 2. Use command-line interface for large datasets
python bin/run-with-review --mode from_baseline
# Choose option 2 (command-line) instead of GUI

# 3. Optimize database queries
# Check if database needs indexing
sqlite3 data/phase5_manual_reviews.db "
CREATE INDEX IF NOT EXISTS idx_status ON transactions(status);
CREATE INDEX IF NOT EXISTS idx_date ON transactions(date);
"
```

### Reconciliation Issues

#### Issue: Balance doesn't match expected amount

**Cause:** Transaction processing errors or data quality issues.

**Debugging Steps:**
```bash
# 1. Check audit trail
cat output/gold_standard/audit_trail.csv | tail -20

# 2. Verify manual review decisions
sqlite3 data/phase5_manual_reviews.db "
SELECT category, count(*), sum(allowed_amount) 
FROM transactions 
WHERE status = 'REVIEWED' 
GROUP BY category;
"

# 3. Look for data quality issues
cat output/gold_standard/data_quality_issues.csv

# 4. Check for duplicate transactions
python -c "
import pandas as pd
df = pd.read_csv('output/gold_standard/audit_trail.csv')
duplicates = df[df.duplicated(['date', 'description', 'amount'])]
print(f'Found {len(duplicates)} potential duplicates')
print(duplicates[['date', 'description', 'amount']])
"

# 5. Manual balance verification
python -c "
from src.core.accounting_engine import AccountingEngine
engine = AccountingEngine()
# Manually add known transactions to verify calculation
"
```

#### Issue: Transactions missing from reconciliation

**Cause:** Date range filters or file loading issues.

**Solutions:**
```bash
# 1. Check date ranges in input files
python -c "
import pandas as pd
df = pd.read_csv('test-data/bank-exports/BALANCE_*.csv')
print('Date range:', df['date'].min(), 'to', df['date'].max())
print('Transaction count:', len(df))
"

# 2. Verify file loading
python -c "
from src.utils.data_loader import load_expense_history
df = load_expense_history('test-data/legacy/Consolidated_Expense_History_20250622.csv')
print('Loaded transactions:', len(df))
print('Date range:', df['date'].min(), 'to', df['date'].max())
"

# 3. Check for excluded transactions
grep -i "excluded\|skipped\|ignored" output/gold_standard/reconciliation_report.txt
```

### Performance Issues

#### Issue: Reconciliation takes too long

**Cause:** Large dataset or inefficient processing.

**Solutions:**
```bash
# 1. Use baseline mode instead of from_scratch
python bin/run-with-review --mode from_baseline

# 2. Profile slow operations
python -m cProfile -o profile_output.prof bin/run-with-review --mode from_baseline
python -c "
import pstats
p = pstats.Stats('profile_output.prof')
p.sort_stats('cumulative').print_stats(20)
"

# 3. Process data in chunks
# Split large CSV files into smaller pieces
split -l 1000 large_file.csv chunk_

# 4. Optimize database
sqlite3 data/phase5_manual_reviews.db "
ANALYZE;
VACUUM;
"
```

#### Issue: High memory usage

**Cause:** Loading large datasets into memory.

**Solutions:**
```python
# 1. Monitor memory usage
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
print(f'Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

# 2. Use chunked processing for large files
python -c "
import pandas as pd
chunk_size = 1000
for chunk in pd.read_csv('large_file.csv', chunksize=chunk_size):
    # Process chunk
    pass
"

# 3. Clear variables when done
# Add del statements in processing code
```

## Error Messages Reference

### Common Error Patterns

| Error Message | Cause | Solution |
|---------------|--------|----------|
| `ModuleNotFoundError` | Import path issues | Check PYTHONPATH, run from project root |
| `FileNotFoundError` | Missing data files | Verify file paths and locations |
| `UnicodeDecodeError` | File encoding issues | Convert file encoding or specify explicitly |
| `sqlite3.OperationalError` | Database issues | Check locks, permissions, initialization |
| `ValueError: Accounting invariant violated` | Balance calculation errors | Check transaction data integrity |
| `tkinter.TclError` | GUI display issues | Check X11, virtual display, or use CLI |
| `pandas.errors.EmptyDataError` | Empty/malformed CSV | Verify file contents and structure |
| `decimal.InvalidOperation` | Currency calculation errors | Check for invalid number formats |

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Set debug environment variables
export LOG_LEVEL=DEBUG
export RECONCILIATION_DEBUG=1

# Run with detailed output
python bin/run-with-review --mode from_baseline --verbose

# Save debug output
python bin/run-with-review --mode from_baseline 2>&1 | tee debug.log
```

## Getting Help

### Information to Collect

When reporting issues, please include:

1. **System Information:**
   ```bash
   python --version
   uname -a          # Linux/macOS
   systeminfo        # Windows
   ```

2. **Error Messages:**
   - Full error traceback
   - Console output leading to error

3. **File Information:**
   ```bash
   ls -la test-data/
   head -5 problematic_file.csv
   ```

4. **Database State:**
   ```bash
   sqlite3 data/phase5_manual_reviews.db ".schema"
   sqlite3 data/phase5_manual_reviews.db "SELECT count(*) FROM transactions;"
   ```

### Support Channels

- **GitHub Issues**: [Repository Issues](https://github.com/yourorg/financial-reconciliation/issues)
- **Documentation**: Check `docs/` directory for additional guides
- **Stack Overflow**: Tag questions with `financial-reconciliation`

### Before Opening an Issue

1. Search existing issues for similar problems
2. Try the suggested solutions in this guide
3. Test with minimal data set to isolate the issue
4. Provide complete error information and context

---

**Last Updated:** July 31, 2025  
**Need more help?** Check the [User Guide](GETTING_STARTED.md) or open an issue on GitHub.