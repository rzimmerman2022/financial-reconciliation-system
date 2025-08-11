# 🚀 Quick Start Guide

> **Get up and running with the Financial Reconciliation System in under 5 minutes**

---

## 📋 Prerequisites

Before you begin, ensure you have:
- **Python 3.8+** installed on your system
- **Git** for cloning the repository
- **Terminal/Command Prompt** access
- **Bank export files** in CSV format (optional for initial testing)

---

## ⚡ 60-Second Setup

### 1. Clone and Install
```bash
# Clone the repository
git clone https://github.com/rzimmerman2022/financial-reconciliation-system.git
cd financial-reconciliation-system

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Desktop GUI (Ultra-Premium)
```bash
python launch_ultra_premium_gui.py
```

### 3. Alternative: Launch Web Interface
```bash
# Start the modern web interface
python bin/launch_web_interface
# or
python -m src.review.web_interface
```
🌐 **Your browser will automatically open to http://localhost:5000**

### 4. Run Basic Reconciliation
```bash
# Run reconciliation with sample data
python reconcile.py --mode from_baseline
```

**🎉 That's it! You're now running the Financial Reconciliation System.**

---

## 🎨 **Visual Interface Options**

### 💎 Premium Interfaces
The system now includes multiple stunning visual interfaces:

#### �️ **Desktop Review GUI**
```bash
python bin/review-gui
```
- Launches the desktop review experience  
- Keyboard shortcuts and export tools built-in

#### ✨ **Ultra Modern Interface**
- Gradient backgrounds and glassmorphism effects
- Smooth animations and visual feedback
- Color-coded transaction categories
- Real-time progress tracking

#### 💎 **Premium Experience**  
- AI-powered categorization suggestions
- Particle celebration effects 🎉
- Advanced neumorphic design
- Interactive charts and batch processing

#### ⌨️ **Universal Shortcuts**
All GUI interfaces support:
- **1-5**: Quick category selection
- **Enter**: Submit review  
- **Space**: Skip transaction
- **←/→**: Navigate transactions
- **Esc**: Exit interface

---

## 🎯 Common Usage Patterns

### 🌐 Web Interface (Recommended for Beginners)
```bash
# Launch the modern web interface with real-time progress
python bin/launch_web_interface
# or run the module directly
python -m src.review.web_interface

# Features available:
# - Real-time progress tracking
# - Interactive transaction review
# - Mobile-responsive design
# - One-click CSV export
# - Glassmorphism UI design
```

### 💻 Command Line Interface (Advanced Users)
```bash
# Basic reconciliation
python reconcile.py

# With custom date range
python reconcile.py --start-date 2024-01-01 --end-date 2024-12-31

# Using baseline mode (recommended for production)
python reconcile.py --mode from_baseline

# With verbose output
python reconcile.py --verbose
```

### 🔧 Utility Commands
```bash
# Export results to Excel
python bin/export-excel

# Run test suite
python bin/run-tests

# Launch desktop GUI for transaction review
python bin/review-gui

# Launch web interface directly (advanced)
python -m src.review.web_interface
```

---

## 📂 Quick File Overview

### 🎯 Main Entry Points
- **`bin/launch_web_interface`** - Modern web interface launcher
- **`reconcile.py`** - Command-line interface
- **`bin/`** - All executable utilities and tools

### 📁 Key Directories
- **`src/core/`** - Main reconciliation logic
- **`src/review/`** - Manual review interfaces (web, desktop, CLI)
- **`test-data/`** - Sample data and bank exports
- **`config/`** - Configuration files
- **`docs/`** - Comprehensive documentation

### ⚙️ Configuration
- **`config/config.yaml`** - Main system configuration
- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Modern Python project setup

---

## 🏦 Adding Your Bank Data

### Step 1: Export Your Bank Data
Export your transactions from your bank in CSV format:
- **Chase**: Online Banking → Statements → Download CSV
- **Wells Fargo**: Account Summary → Download → CSV
- **Discover**: Account Center → Download → CSV
- **Others**: Look for "Export" or "Download" options

### Step 2: Place Files in Correct Directory
```bash
# Copy your bank CSV files here:
cp ~/Downloads/bank_export.csv test-data/bank-exports/

# The system automatically detects bank formats
ls test-data/bank-exports/
```

### Step 3: Run Reconciliation
```bash
# Process your data
python reconcile.py --mode from_baseline

# Or use the web interface for guided experience
python bin/launch_web_interface
# or
python -m src.review.web_interface
```

---

## 🎨 Interface Options

### 🌐 Web Interface (Best for Most Users)
```bash
python bin/launch_web_interface
# or
python -m src.review.web_interface
```
**Features:**
- Modern glassmorphism design
- Real-time progress updates
- Mobile-responsive layout
- Interactive charts and visualizations
- One-click export functionality

### 🖥️ Desktop GUI (Power Users)
```bash
python bin/review-gui
```
**Features:**
- Native desktop application
- Keyboard shortcuts (F1 for help)
- Material Design interface
- Advanced review controls

### 📱 Command Line (Automation & Scripts)
```bash
python reconcile.py
```
**Features:**
- Scriptable and automatable
- Detailed logging and output
- Custom configuration options
- Batch processing capabilities

---

## 📊 Understanding the Results

### 🎯 Key Output Files
After running reconciliation, check these files:

```bash
# Main results (if using archive mode)
archive/output/gold_standard/
├── accounting_ledger.csv      # Complete transaction history
├── audit_trail.csv           # Detailed reconciliation log
├── summary.json              # Machine-readable summary
└── reconciliation_report.txt # Human-readable summary
```

### 💰 Reading the Balance
The system will show results like:
```
Final Balance: $1,234.56
Status: Ryan owes Jordyn
```

This means:
- **Positive amount**: First person owes second person
- **Negative amount**: Second person owes first person
- **Zero**: All transactions are perfectly balanced

---

## 🔧 Troubleshooting

### ❌ Common Issues

#### Python Not Found
```bash
# Install Python 3.8+ from python.org
# Then verify installation:
python --version
```

#### Module Import Errors
```bash
# Ensure you're in the project directory and virtual environment is activated
cd financial-reconciliation
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

#### Port 5000 Already in Use
```bash
# The web interface uses port 5000 by default
# Stop other applications using port 5000, or modify config/config.yaml
```

#### CSV File Encoding Issues
```bash
# The system automatically handles most encoding issues
# If you encounter problems, check the file encoding and save as UTF-8
```

### 🆘 Getting Help

#### 📚 Documentation
- **Full Documentation**: See [README.md](README.md)
- **Architecture Guide**: See [docs/architecture/PIPELINE.md](docs/architecture/PIPELINE.md)
- **Troubleshooting**: See [docs/user-guide/TROUBLESHOOTING.md](docs/user-guide/TROUBLESHOOTING.md)

#### 🐛 Reporting Issues
- **GitHub Issues**: [Create an issue](https://github.com/rzimmerman2022/financial-reconciliation-system/issues)
- **Bug Reports**: Include system info, error messages, and steps to reproduce

---

## 🚀 Next Steps

### 🎓 Learning More
1. **Read the Full Documentation**: [README.md](README.md) contains comprehensive information
2. **Explore Configuration**: Customize behavior via [config/config.yaml](config/config.yaml)
3. **Try Different Interfaces**: Test web, desktop, and CLI interfaces
4. **Review Sample Data**: Examine files in `test-data/` directory

### 🏗️ Advanced Usage
1. **Custom Configuration**: Create environment-specific config files
2. **Automated Workflows**: Set up scheduled reconciliation runs
3. **API Integration**: Use the system in automated pipelines
4. **Extend Functionality**: Add support for additional banks or formats

### 🤝 Contributing
1. **Read Contributing Guide**: See [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Join the Community**: Participate in GitHub discussions
3. **Report Issues**: Help improve the system by reporting bugs
4. **Submit Features**: Suggest new functionality or improvements

---

## 📋 Cheat Sheet

### 🔥 Essential Commands
```bash
# Quick start
python bin/launch_web_interface      # Launch web interface

# Basic reconciliation
python reconcile.py                  # CLI reconciliation
python reconcile.py --mode baseline  # Production mode

# Utilities
python bin/export-excel              # Export to Excel
python bin/run-tests                 # Run all tests
python bin/review-gui                # Desktop review GUI

# Advanced
python reconcile.py --verbose        # Detailed output
python reconcile.py --config custom.yaml  # Custom config
```

### 📂 Key File Locations
```bash
# Configuration
config/config.yaml                   # Main configuration

# Data
test-data/bank-exports/             # Place your CSV files here
data/phase5_manual_reviews.db      # Review database

# Results
archive/output/gold_standard/       # Reconciliation results

# Documentation
docs/                               # All documentation
README.md                           # Comprehensive guide
```

### 🌐 Web Interface URLs
- **Main Interface**: http://localhost:5000
- **Review Interface**: Integrated in main interface
- **API Endpoints**: http://localhost:5000/api (if enabled)

---

**🎉 You're ready to start reconciling financial transactions!**

*For comprehensive documentation, see [README.md](README.md)*