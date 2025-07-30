# Financial Reconciliation System

A production-ready financial reconciliation system implementing double-entry bookkeeping with comprehensive audit trails for tracking shared expenses.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/financial-reconciliation.git
cd financial-reconciliation

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run reconciliation from baseline (recommended)
python scripts/run_with_review.py --mode from_baseline

# Run reconciliation from scratch
python scripts/run_with_review.py --mode from_scratch

# Run tests
pytest tests/
```

## 📁 Project Structure

```
financial-reconciliation/
├── src/                      # Source code
│   ├── core/                # Core business logic
│   │   ├── accounting_engine.py      # Double-entry bookkeeping
│   │   ├── description_decoder.py    # Transaction pattern recognition
│   │   └── reconciliation_engine.py  # Main reconciliation logic
│   ├── review/              # Manual review system
│   │   ├── manual_review_system.py   # SQLite-based tracking
│   │   ├── batch_review_helper.py    # Pattern-based categorization
│   │   ├── spreadsheet_review_system.py  # Excel export/import
│   │   └── web_review_interface.py   # Browser-based interface
│   ├── utils/               # Utilities
│   │   └── data_loader.py           # CSV data loading
│   └── loaders/            # Data source loaders
│       ├── expense_loader.py
│       ├── rent_loader.py
│       └── zelle_loader.py
├── scripts/                 # Executable scripts
│   └── run_with_review.py   # Main entry point
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   └── integration/        # Integration tests
├── docs/                    # Documentation
│   ├── business/           # Business logic docs
│   └── technical/          # Technical docs
├── data/                    # Data files
│   ├── raw/                # Original CSVs
│   ├── processed/          # Normalized data
│   └── new_raw/            # Bank exports
├── output/                  # Reconciliation results
├── config/                  # Configuration files
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Optional configuration
LOG_LEVEL=INFO
OUTPUT_DIR=output
DATABASE_PATH=phase5_manual_reviews.db
```

### Data Sources

Place your data files in the appropriate directories:
- **Phase 4 Data**: `data/raw/` (pre-reviewed with allowed_amount)
- **Phase 5+ Data**: `data/new_raw/` (bank CSVs requiring review)

## 💼 Features

### Core Functionality
- **Double-Entry Bookkeeping**: Full accounting ledger with debits/credits
- **Pattern Recognition**: Automatic transaction categorization
- **Manual Review System**: Interactive review for uncategorized transactions
- **Comprehensive Audit Trail**: Complete transaction history with running balances

### Review System
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
- Ensure `phase5_manual_reviews.db` exists
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