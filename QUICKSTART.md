# Quick Start Guide • Gold Standard Edition

Get up and running with the **Gold Standard** Financial Reconciliation System in 5 minutes!

🌟 **NEW**: Features a cutting-edge web interface with glassmorphism design and 2025 UI standards.

## Prerequisites

- Python 3.8 or higher
- Git (for cloning the repository)

## 1. Installation (1 minute)

```bash
# Clone the repository
git clone https://github.com/your-org/financial-reconciliation.git
cd financial-reconciliation

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Run Your First Reconciliation (2 minutes)

```bash
# Run reconciliation with sample data
python reconcile.py

# You should see output like:
# ================================================================================
#                     FINANCIAL RECONCILIATION REPORT
# ================================================================================
# Mode: FROM_BASELINE
# Result: Ryan owes Jordyn $8,595.87
```

## 3. Review Pending Transactions (2 minutes)

### 🌟 Option A: Gold Standard Web Interface (RECOMMENDED)

```bash
# Launch the cutting-edge web interface
python create_modern_web_gui.py

# Features:
# • 🎨 Glassmorphism design with backdrop blur
# • 📱 Responsive mobile-first layout  
# • ⚡ Smooth animations and micro-interactions
# • ⌨️ Keyboard shortcuts (1-4 for categories)
# • 📊 Real-time progress tracking
# • 🌓 Dark/light mode toggle
# • 📄 One-click CSV export
```

### Option B: Desktop GUI

```bash
# Launch the Material Design desktop interface
python -m src.review.modern_visual_review_gui
```

### Option C: Command Line

```bash
# Use CLI for manual review
python bin/manual_review_cli.py
```

## 4. Generate Reports

After reconciliation, find your reports in:
- `output/gold_standard/` - Gold standard reconciliation reports
- `templates/` - Generated web interface templates
- Export directly from the web interface with one-click CSV export

## Next Steps

- 📖 Read the full [README](README.md)
- 🔧 Configure settings in `config/config.yaml`
- 📊 Add your own bank data to `data/bank-exports/`
- 🧪 Run tests with `python run_tests.py`

## Common Commands

```bash
# Launch Gold Standard Web Interface
python create_modern_web_gui.py

# Reconcile specific date range
python reconcile.py --start-date 2024-01-01 --end-date 2024-12-31

# Run in baseline mode
python reconcile.py --mode baseline

# Export to Excel format
python export_to_excel.py
```

## Troubleshooting

**GUI won't start?**
```bash
# Install tkinter (usually comes with Python)
# Ubuntu/Debian:
sudo apt-get install python3-tk
# macOS: Should be included
# Windows: Should be included
```

**Import errors?**
```bash
# Make sure you're in the project root
cd financial-reconciliation
# Ensure virtual environment is activated
```

**Need help?**
- Check [Documentation](docs/)
- Report issues on [GitHub](https://github.com/your-org/financial-reconciliation/issues)

---

Happy reconciling! 🎉