# Gold Standard Project Structure (v4.1.0)

## Overview

This document describes the gold standard directory structure implemented for the Financial Reconciliation System, following industry best practices for Python enterprise projects. 

**Updated in v4.1.0**: Added accuracy improvements module and enhanced reconciliation runner.

## Directory Layout

```
financial-reconciliation/
├── bin/                          # Executable scripts (Unix standard)
│   ├── financial-reconciliation  # Main entry point wrapper
│   └── run-with-review           # Direct reconciliation runner
│
├── src/                          # Source code (Python standard)
│   ├── __init__.py
│   ├── core/                     # Core business logic
│   │   ├── accounting_engine.py      # Double-entry bookkeeping
│   │   ├── accuracy_improvements.py  # v4.1.0: Enhanced validation & matching
│   │   ├── description_decoder.py    # Transaction pattern recognition
│   │   └── reconciliation_engine.py  # Main reconciliation logic
│   │
│   ├── review/                   # Manual review system
│   │   ├── manual_review_system.py   # SQLite-based tracking
│   │   ├── batch_review_helper.py    # Pattern-based categorization
│   │   ├── spreadsheet_review_system.py  # Excel export/import
│   │   └── web_review_interface.py   # Browser-based interface
│   │
│   ├── utils/                    # Utilities
│   │   └── data_loader.py            # CSV data loading and encoding
│   │
│   ├── loaders/                  # Data source loaders
│   │   ├── expense_loader.py         # Expense history loader
│   │   ├── rent_loader.py            # Rent allocation loader
│   │   └── zelle_loader.py           # Zelle payment loader
│   │
│   ├── processors/               # Data processors
│   │   └── expense_processor.py      # Expense processing logic
│   │
│   └── reconcilers/              # Reconciliation engines
│       └── __init__.py               # (Reserved for future engines)
│
├── tests/                        # Test suite (Universal standard)
│   ├── unit/                     # Unit tests
│   │   ├── test_accounting_engine.py
│   │   ├── test_data_loader.py
│   │   ├── test_description_decoder.py
│   │   ├── test_expense_processor.py
│   │   └── test_gold_standard.py
│   │
│   └── integration/              # Integration tests
│       └── (Reserved for integration tests)
│
├── docs/                         # Documentation
│   ├── business/                 # Business logic documentation
│   │   ├── CRITICAL_RENT_RULES.md
│   │   └── assumptions.md
│   │
│   ├── technical/                # Technical documentation
│   │   ├── AI_HANDOVER_CONTEXT.md
│   │   └── CURRENT_STATUS_AND_ISSUES.md
│   │
│   ├── api/                      # API documentation
│   ├── architecture/             # System architecture docs
│   └── user-guide/               # User guides
│
├── test-data/                    # Test and sample data
│   ├── bank-exports/             # Bank CSV exports (Phase 5+)
│   │   ├── BALANCE_*.csv         # Bank balance files
│   │   └── .gitkeep
│   │
│   ├── legacy/                   # Pre-reviewed data (Phase 4)
│   │   ├── Consolidated_*.csv    # Historical data files
│   │   └── .gitkeep
│   │
│   ├── processed/                # Normalized data outputs
│   │   ├── *_normalized.csv      # Processed data files
│   │   └── .gitkeep
│   │
│   ├── fixtures/                 # Test fixtures
│   └── samples/                  # Sample data files
│
├── data/                         # Runtime data
│   └── phase5_manual_reviews.db  # SQLite review database
│
├── tools/                        # Development tools
│   ├── setup.py                  # Package setup script
│   ├── pytest.ini                # Test configuration
│   ├── scripts/                  # Utility scripts
│   └── utilities/                # Development utilities
│
├── output/                       # Reconciliation outputs
│   └── gold_standard/            # Standard output directory
│       ├── accounting_ledger.csv
│       ├── audit_trail.csv
│       ├── data_quality_issues.csv
│       ├── data_quality_report.txt
│       └── accuracy_report.txt   # v4.1.0: Detailed accuracy metrics
│       ├── manual_review_required.csv
│       ├── reconciliation_report.txt
│       └── summary.json
│
├── config/                       # Configuration files
├── examples/                     # Usage examples
│   ├── quickstart/               # Quick start examples
│   └── advanced/                 # Advanced usage examples
│
├── build/                        # Build artifacts
├── dist/                         # Distribution packages
├── .github/                      # GitHub configuration
│   └── workflows/                # GitHub Actions workflows
├── .vscode/                      # VS Code configuration
├── .gitignore                    # Git ignore rules
├── README.md                     # Project documentation
├── run_accurate_reconciliation.py # v4.1.0: Maximum accuracy runner
└── requirements.txt              # Python dependencies
```

## Key Design Decisions

### 1. Executable Scripts (`bin/`)
- Following Unix conventions for command-line tools
- Clear separation between wrapper scripts and implementation
- Easy to add to system PATH for global access

### 2. Source Code Organization (`src/`)
- Modular design with clear separation of concerns
- Core business logic isolated from auxiliary systems
- Review system as a separate module for flexibility
- Utilities and loaders organized by function

### 3. Test Data Management (`test-data/`)
- Clear distinction between test data and runtime data
- Descriptive naming: `bank-exports/` instead of `new_raw/`
- Legacy data clearly marked for Phase 4 compatibility
- Processed data kept separate from raw inputs

### 4. Runtime Data (`data/`)
- Minimal runtime data directory
- Only persistent application data (database)
- Clear separation from test/sample data

### 5. Development Tools (`tools/`)
- Build and test configuration centralized
- Development scripts organized separately
- Easy to find and use development utilities

### 6. Documentation Structure (`docs/`)
- Business and technical documentation separated
- Room for growth with api/, architecture/, user-guide/
- Follows common documentation patterns
- Pipeline documentation in architecture/PIPELINE.md

## Benefits of This Structure

### For Developers
- **Intuitive Navigation**: Clear where to find any component
- **Standard Patterns**: Follows Python packaging best practices
- **Clean Workspace**: No clutter from backups or archives
- **Easy Testing**: Test data clearly organized and accessible

### For Operations
- **Clear Deployment**: Obvious what needs to be deployed
- **Runtime Isolation**: Runtime data separate from code
- **Log Management**: Dedicated logs directory
- **Output Organization**: Consistent output structure

### For Maintenance
- **Scalability**: Structure supports project growth
- **Modularity**: Easy to add new components
- **Documentation**: Clear documentation hierarchy
- **Version Control**: Clean git history without clutter

## Migration Notes

### From Old Structure to Gold Standard

1. **Executable Migration**
   - `run.py` → `bin/financial-reconciliation`
   - `scripts/run_with_review.py` → `bin/run-with-review`

2. **Data Directory Changes**
   - `data/raw/` → `test-data/legacy/`
   - `data/new_raw/` → `test-data/bank-exports/`
   - `data/processed/` → `test-data/processed/`
   - `phase5_manual_reviews.db` → `data/phase5_manual_reviews.db`

3. **Tool Consolidation**
   - `setup.py` → `tools/setup.py`
   - `pytest.ini` → `tools/pytest.ini`

4. **Cleanup Actions**
   - Removed `archive/` folder (200+ old files)
   - Removed `backups/` folder (nested backup directories)
   - Removed backup subdirectories from `src/`
   - Deleted 27,613 lines of redundant code

## Best Practices

### Adding New Components
1. **New Module**: Add to appropriate `src/` subdirectory
2. **New Script**: Add to `bin/` with clear naming
3. **New Test**: Mirror source structure in `tests/`
4. **New Tool**: Place in `tools/scripts/` or `tools/utilities/`

### File Naming Conventions
- **Python Files**: `lowercase_with_underscores.py`
- **Documentation**: `UPPERCASE_OR_TITLE_CASE.md`
- **Data Files**: Descriptive names with dates where applicable
- **Config Files**: Standard names (`.gitignore`, `pytest.ini`)

### Import Patterns
- Use absolute imports from `src/`
- Example: `from src.core.accounting_engine import AccountingEngine`
- Maintain consistency across all modules

---

**Version**: 1.0.0  
**Created**: July 31, 2025  
**Standard**: Python Enterprise Best Practices