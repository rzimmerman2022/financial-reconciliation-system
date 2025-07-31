# Financial Reconciliation System

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Proprietary-red.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Status](https://img.shields.io/badge/status-Production-green.svg)](https://github.com/yourorg/financial-reconciliation)

A production-ready financial reconciliation system implementing double-entry bookkeeping with comprehensive audit trails for tracking shared expenses. Built with enterprise-grade architecture and professional tooling for accurate financial transaction processing and review.

## ✨ Key Features

- 🏦 **Double-Entry Bookkeeping**: GAAP-compliant accounting with automatic balance validation
- 🎯 **Visual Transaction Review**: Professional GUI with keyboard shortcuts for efficient processing
- 📊 **Comprehensive Audit Trails**: Complete transaction history with running balances
- 🔍 **Pattern Recognition**: Intelligent categorization with machine learning capabilities
- 📈 **Multiple Data Sources**: Support for bank exports, manual entries, and legacy data
- 🛡️ **Data Quality Assurance**: Encoding detection, validation, and error reporting
- 📤 **Flexible Export Options**: JSON, CSV, Excel formats for external analysis
- 🌐 **Multi-Interface Support**: GUI, CLI, web, and API interfaces

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** - Core runtime environment
- **pip** - Package manager for Python dependencies
- **Git** - Version control (for cloning repository)
- **tkinter** - GUI framework (usually included with Python)

Optional:
- **Excel/Google Sheets** - For bulk transaction review
- **SQLite Browser** - For database inspection and debugging

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourorg/financial-reconciliation.git
cd financial-reconciliation

# 2. Create and activate virtual environment
python -m venv venv

# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
python bin/review-gui --help
```

### Quick Start Guide

```bash
# 1. Prepare your data
# Place CSV files in test-data/bank-exports/ (for new data)
# Place legacy files in test-data/legacy/ (for historical data)

# 2. Run reconciliation (recommended approach)
python bin/run-with-review --mode from_baseline

# 3. When prompted, choose Visual GUI Review (option 1)
# Use keyboard shortcuts: E=Expense, R=Rent, S=Settlement, P=Personal

# 4. Review results in output/gold_standard/
```

### All Available Commands

```bash
# 🎯 Main Reconciliation Workflows
python bin/run-with-review --mode from_baseline    # Start from Sept 30, 2024 baseline
python bin/run-with-review --mode from_scratch     # Process all historical data
python bin/financial-reconciliation --help         # Main entry point with options

# 🖥️ Visual Review Interface
python bin/review-gui                               # Launch GUI for transaction review
python bin/review-gui /path/to/custom.db          # Use custom database

# 🧪 Testing and Validation
pytest                                              # Run test suite
pytest -v --cov=src                               # Run with coverage report
python -m src.core.accounting_engine               # Test core engine

# 🔧 Development Tools
python tools/setup.py develop                      # Install in development mode
black src/ tests/                                  # Format code
flake8 src/ tests/                                 # Lint code
mypy src/                                          # Type checking
```

## 📁 Project Structure

```
financial-reconciliation/
├── bin/                          # Executable scripts
│   ├── financial-reconciliation  # Main entry point
│   ├── run-with-review           # Direct reconciliation runner
│   └── review-gui                # Visual GUI for transaction review
├── src/                          # Source code
│   ├── core/                    # Core business logic
│   │   ├── accounting_engine.py      # Double-entry bookkeeping
│   │   ├── description_decoder.py    # Transaction pattern recognition
│   │   └── reconciliation_engine.py  # Main reconciliation logic
│   ├── review/                  # Manual review system
│   │   ├── manual_review_system.py   # SQLite-based tracking
│   │   ├── batch_review_helper.py    # Pattern-based categorization
│   │   ├── spreadsheet_review_system.py  # Excel export/import
│   │   └── web_review_interface.py   # Browser-based interface
│   ├── utils/                   # Utilities
│   │   └── data_loader.py            # CSV data loading
│   ├── loaders/                # Data source loaders
│   │   ├── expense_loader.py
│   │   ├── rent_loader.py
│   │   └── zelle_loader.py
│   ├── processors/             # Data processors
│   │   └── expense_processor.py
│   └── reconcilers/            # Reconciliation engines
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   └── integration/            # Integration tests
├── docs/                         # Documentation
│   ├── business/               # Business logic docs
│   ├── technical/              # Technical docs
│   ├── api/                    # API documentation
│   ├── architecture/           # System architecture
│   └── user-guide/             # User guides
├── test-data/                    # Test and sample data
│   ├── bank-exports/           # Bank CSV exports (Phase 5+)
│   ├── legacy/                 # Pre-reviewed data (Phase 4)
│   ├── processed/              # Normalized data
│   ├── fixtures/               # Test fixtures
│   └── samples/                # Sample data files
├── data/                         # Runtime data
│   └── phase5_manual_reviews.db  # Review database
├── tools/                        # Development tools
│   ├── setup.py               # Package setup
│   └── pytest.ini             # Test configuration
├── output/                       # Reconciliation results
├── config/                       # Configuration files
├── logs/                         # Application logs
├── temp/                         # Temporary files
├── examples/                     # Usage examples
│   ├── quickstart/             # Quick start examples
│   └── advanced/               # Advanced usage
└── requirements.txt              # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional configuration
LOG_LEVEL=INFO
OUTPUT_DIR=output
DATABASE_PATH=data/phase5_manual_reviews.db
```

### Data Sources

Place your data files in the appropriate directories:
- **Phase 4 Data**: `test-data/legacy/` (pre-reviewed with allowed_amount)
- **Phase 5+ Data**: `test-data/bank-exports/` (bank CSVs requiring review)
- **Runtime Database**: `data/phase5_manual_reviews.db` (review decisions)

## 💼 Features

### Core Functionality
- **Double-Entry Bookkeeping**: Full accounting ledger with debits/credits
- **Pattern Recognition**: Automatic transaction categorization
- **Manual Review System**: Interactive review for uncategorized transactions
- **Comprehensive Audit Trail**: Complete transaction history with running balances

### Review System
- **Visual GUI**: Native desktop interface with keyboard shortcuts
- **Web Interface**: Browser-based review interface
- **Batch Processing**: Pattern-based auto-categorization
- **Excel Integration**: Export/import for bulk review
- **SQLite Storage**: Persistent review decisions

### Data Quality
- **Encoding Handling**: Automatic detection and conversion
- **Missing Data Detection**: Flags incomplete transactions
- **Duplicate Prevention**: Ensures transaction uniqueness

## 📊 Output Files

The system generates comprehensive output in `output/gold_standard/`:

| File | Description |
|------|-------------|
| `summary.json` | Machine-readable results |
| `reconciliation_report.txt` | Human-readable report |
| `audit_trail.csv` | Complete transaction log |
| `accounting_ledger.csv` | Double-entry ledger |
| `manual_review_required.csv` | Transactions needing review |
| `data_quality_issues.csv` | Data problems found |

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_accounting_engine.py

# Run tests in verbose mode
pytest -v
```

## 📖 Documentation

### Key Documents
- [Technical Architecture](docs/technical/AI_HANDOVER_CONTEXT.md)
- [Business Rules](docs/business/CRITICAL_RENT_RULES.md)
- [Workflow Guide](docs/technical/GOLD_STANDARD_WORKFLOW_COMPLETE.md)
- [Project Status](docs/technical/CURRENT_STATUS_AND_ISSUES.md)

### API Documentation
See individual module docstrings for detailed API documentation.

## 🛠️ Development

### Code Style
```bash
# Format code
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Run development tools
python tools/setup.py develop
```

### Adding Features
1. Create feature branch from `main`
2. Add tests for new functionality
3. Implement feature
4. Ensure all tests pass
5. Submit pull request

## 🐛 Troubleshooting

### Common Issues

**Unicode Errors in Bank Data**
- System automatically tries multiple encodings
- Check `data_quality_issues.csv` for details

**Balance Mismatches**
- Review `audit_trail.csv` for calculation details
- Verify manual review decisions in database
- Check for duplicate transactions

**Manual Review Not Working**
- Ensure `data/phase5_manual_reviews.db` exists
- Verify transactions have non-zero amounts
- Check date range filters

## 📝 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For questions or issues:
- Check the [documentation](docs/)
- Review [troubleshooting guide](#-troubleshooting)
- Open an issue on GitHub

---

**Version**: 1.0.0  
**Last Updated**: July 30, 2025