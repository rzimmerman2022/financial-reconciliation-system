# Project Structure - Gold Standard Financial Reconciliation

## Active Files (Production System)

### Core Reconciliation Engine
```
├── gold_standard_reconciliation.py    # Main reconciliation engine
├── accounting_engine.py                # Double-entry bookkeeping
├── description_decoder.py              # Transaction pattern recognition
├── data_loader.py                      # CSV data loading utilities
└── run_reconciliation_with_review.py   # Full workflow orchestrator
```

### Manual Review System
```
├── manual_review_system.py             # SQLite-based review tracking
├── batch_review_helper.py              # Pattern-based auto-categorization
├── spreadsheet_review_system.py        # Excel export/import for bulk review
├── web_review_interface.py             # Browser-based review interface
└── manual_review_helper.py             # Review utilities
```

### Testing
```
tests/
├── test_gold_standard.py               # Main system tests
├── test_accounting_engine.py           # Accounting validation tests
├── test_description_decoder.py         # Pattern recognition tests
├── test_description_decoder_comprehensive.py
├── test_data_loader.py                 # Data loading tests
├── test_loaders.py                     # Legacy loader tests
└── test_expense_processor.py           # Expense processing tests
```

### Data Files
```
data/
├── raw/                                # Original CSV files
│   ├── Consolidated_Expense_History_20250622.csv
│   ├── Consolidated_Rent_Allocation_20250527.csv
│   └── Zelle_From_Jordyn_Final.csv
├── processed/                          # Normalized data
└── new_raw/                           # Bank CSV exports
    ├── Ryan_Monarch_Money_*.csv
    ├── Ryan_Rocket_Money_*.csv
    ├── Jordyn_Chase_*.csv
    ├── Jordyn_WellsFargo_*.csv
    └── Jordyn_Discover_*.csv
```

### Documentation
```
docs/
├── GOLD_STANDARD_WORKFLOW_COMPLETE.md  # Comprehensive workflow guide
├── AI_HANDOVER_CONTEXT.md             # Technical implementation details
├── CRITICAL_RENT_RULES.md             # Business logic documentation
├── CURRENT_STATUS_AND_ISSUES.md       # Latest system status
├── GOLD_STANDARD_FINAL_REPORT.md      # Results summary
├── README.md                          # Main documentation
├── PROJECT_STRUCTURE.md               # This file
└── assumptions.md                     # Business assumptions
```

### Output
```
output/
└── gold_standard/                     # Current reconciliation results
    ├── summary.json
    ├── reconciliation_report.txt
    ├── audit_trail.csv
    ├── accounting_ledger.csv
    ├── manual_review_required.csv
    └── data_quality_issues.csv
```

### Database
```
phase5_manual_reviews.db               # SQLite database for review tracking
```

### Source Modules
```
src/
├── loaders/                          # Data loading modules
│   ├── expense_loader.py
│   ├── rent_loader.py
│   └── zelle_loader.py
├── processors/                       # Data processing
│   └── expense_processor.py
└── reconcilers/                      # Reconciliation logic
    └── __init__.py
```

## Archived Files

All obsolete files have been moved to the `archive/` directory:

```
archive/
├── phase5a/                          # Phase 5A implementation (superseded)
├── old_reconciliation/               # Previous reconciliation attempts
├── old_docs/                         # Outdated documentation
├── old_analysis/                     # Old analysis scripts
└── old_output/                       # Previous output files
```

## Key Scripts Usage

### Primary Workflows
```bash
# Standard reconciliation
python gold_standard_reconciliation.py --mode from_baseline

# With manual review
python run_reconciliation_with_review.py

# Run tests
python -m pytest tests/
```

### Manual Review
```bash
# Export for spreadsheet review
python batch_review_helper.py

# Launch web interface
python web_review_interface.py
```

## File Relationships

```
run_reconciliation_with_review.py
    ├── gold_standard_reconciliation.py
    │   ├── accounting_engine.py
    │   ├── description_decoder.py
    │   └── data_loader.py
    └── manual_review_system.py
        ├── batch_review_helper.py
        └── spreadsheet_review_system.py
```

## Notes

1. **Gold Standard**: All files prefixed with `gold_standard` or containing "gold" are the current production system
2. **Manual Review**: Required for all Phase 5+ bank data (Oct 2024 onwards)
3. **Testing**: Comprehensive test coverage for all core components
4. **Archive**: Historical files preserved for reference but not used in production

---
Last Updated: July 30, 2025