# Financial Reconciliation System

![Version](https://img.shields.io/badge/version-3.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-gold--standard-gold.svg)
![Interface](https://img.shields.io/badge/interface-modern--web--gui-brightgreen.svg)

A **gold standard** financial transaction reconciliation system featuring a cutting-edge web interface, double-entry bookkeeping, automated matching, and comprehensive data quality management. Built with 2025 design standards including glassmorphism, responsive design, and real-time progress tracking.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Current Status](#current-status)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Financial Reconciliation System is a production-ready solution designed to handle complex financial transaction reconciliation between multiple parties. It features automated transaction matching, intelligent data quality management, and a modern visual interface for manual review of ambiguous transactions.

### Key Problems Solved

- **Multi-source Transaction Reconciliation**: Handles transactions from various banks and financial platforms
- **Double-Entry Bookkeeping**: Ensures accounting accuracy with proper debit/credit tracking
- **Data Quality Issues**: Automatically detects and flags encoding errors, missing data, and duplicates
- **Manual Review Workflow**: Provides an intuitive GUI for reviewing ambiguous transactions
- **Comprehensive Audit Trail**: Maintains detailed logs of all reconciliation decisions

## Key Features

### Core Functionality
- ✅ **Multi-Bank Support**: Chase, Wells Fargo, Apple Card, MonarchMoney, Wave
- ✅ **Intelligent Matching**: Fuzzy matching with configurable similarity thresholds
- ✅ **Data Quality Engine**: Automatic detection and flagging of data issues
- ✅ **Manual Review System**: Modern Material Design GUI for transaction review
- ✅ **Double-Entry Bookkeeping**: Complete debit/credit tracking with accounting rules
- ✅ **Multiple Output Formats**: Excel, CSV, JSON with customizable reports

### Technical Features
- 🌟 **Gold Standard Web Interface**: Glassmorphism design with 2025 standards
- 🚀 **High Performance**: Processes thousands of transactions efficiently
- 🔒 **Data Integrity**: SQLite-based storage with ACID compliance
- 📊 **Rich Visualizations**: Interactive charts and real-time progress tracking
- 📱 **Responsive Design**: Mobile-first layout that works on all devices
- ⚡ **Modern Interactions**: Smooth animations and micro-interactions
- 🔧 **Configurable**: YAML-based configuration for all settings
- 📝 **Comprehensive Logging**: Detailed audit trails and error tracking

## Current Status

**Last Reconciliation Run**: August 2, 2025
- **Result**: Ryan owes Jordyn **$8,595.87**
- **Transactions Processed**: 283
- **Pending Manual Review**: 1 transaction
- **Data Quality Issues**: 168 flagged (mainly Chase encoding errors)
- **Interface**: 🌟 Gold Standard Web GUI with glassmorphism design

### Recent Updates (August 2, 2025)
- 🌟 **NEW: Gold Standard Web Interface** with glassmorphism design
- ✅ Modern responsive web GUI with real-time progress tracking
- ✅ Smooth animations and micro-interactions
- ✅ Mobile-first responsive design
- ✅ Dark/light mode support with keyboard shortcuts
- ✅ One-click CSV export functionality
- ✅ Auto-scroll and intuitive navigation
- ✅ Complete documentation overhaul to gold standard

## Quick Start

```bash
# Clone the repository
git clone https://github.com/your-org/financial-reconciliation.git
cd financial-reconciliation

# Install dependencies
pip install -r requirements.txt

# Run reconciliation
python reconcile.py

# Launch Gold Standard Web Interface (RECOMMENDED)
python create_modern_web_gui.py
# Opens automatically at http://localhost:5000

# Alternative interfaces:
# Desktop GUI: python -m src.review.modern_visual_review_gui
# CLI: python bin/manual_review_cli.py
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- SQLite3 (included with Python)

### Standard Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install package
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Usage

### 1. Basic Reconciliation

```bash
# Run with default settings
python reconcile.py

# Run with custom date range
python reconcile.py --start-date 2024-01-01 --end-date 2024-12-31

# Run in baseline mode
python reconcile.py --mode baseline
```

### 2. Manual Transaction Review

#### 🌟 Gold Standard Web Interface (RECOMMENDED)
```bash
python create_modern_web_gui.py
# Features: Glassmorphism design, responsive layout, real-time progress
# Opens automatically at http://localhost:5000
```

#### Alternative Interfaces
```bash
# Desktop GUI
python -m src.review.modern_visual_review_gui

# Command Line Interface  
python bin/manual_review_cli.py
```

### 3. Generate Reports

```python
from src.processors.excel_report_generator import ExcelReportGenerator

generator = ExcelReportGenerator()
generator.generate_comprehensive_report(
    reconciliation_results,
    output_path="output/reports/reconciliation_report.xlsx"
)
```

## Project Structure

```
financial-reconciliation/
├── src/                    # Source code
│   ├── core/              # Core business logic
│   ├── loaders/           # Data loaders for various sources
│   ├── processors/        # Data processing and reporting
│   ├── reconcilers/       # Reconciliation engines
│   ├── review/            # Manual review system
│   └── utils/             # Utility functions
├── tests/                  # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── docs/                   # Documentation
│   ├── api/               # API reference
│   ├── architecture/      # System architecture
│   ├── business/          # Business logic docs
│   ├── technical/         # Technical documentation
│   └── user-guide/        # User guides
├── config/                 # Configuration files
├── data/                   # Data storage
├── output/                 # Generated reports
├── tools/                  # Development tools
└── examples/              # Usage examples
```

## Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Data Loaders  │────▶│ Data Processors  │────▶│  Reconciliation │
│  (Multi-source) │     │ (Normalization)  │     │     Engine      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Manual Review  │◀────│ Review Database  │◀────│ Quality Checks  │
│   GUI/CLI       │     │    (SQLite)      │     │   & Flagging    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │ Report Generator│
                                                  │  (Excel/CSV)    │
                                                  └─────────────────┘
```

For detailed architecture documentation, see [docs/architecture/](docs/architecture/).

## API Reference

### Core Classes

#### TransactionLoader
```python
from src.loaders.base_loader import TransactionLoader

loader = TransactionLoader(file_path="data/transactions.csv")
transactions = loader.load()
```

#### ReconciliationEngine
```python
from src.reconcilers.reconciliation_engine import ReconciliationEngine

engine = ReconciliationEngine(config)
results = engine.reconcile(transactions_a, transactions_b)
```

For complete API documentation, see [docs/api/](docs/api/).

## Configuration

The system uses YAML configuration files located in `config/`:

```yaml
# config/config.yaml
reconciliation:
  amount_tolerance: 0.01
  date_tolerance_days: 1
  description_similarity_threshold: 0.85

data_quality:
  enable_quality_checks: true
  flag_missing_amounts: true
  fix_encoding_issues: true
```

See [Configuration Guide](docs/user-guide/configuration.md) for all options.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration

# Run with verbose output
pytest -v
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- Follow PEP 8 style guide
- Maintain test coverage above 80%
- Update documentation for new features
- Add type hints for all functions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: support@financialreconciliation.com
- 📚 Documentation: [https://docs.financialreconciliation.com](https://docs.financialreconciliation.com)
- 🐛 Issues: [GitHub Issues](https://github.com/your-org/financial-reconciliation/issues)

---

Built with ❤️ for accurate financial reconciliation