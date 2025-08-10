#!/usr/bin/env python3
"""
Financial Reconciliation System - Main Entry Point
==================================================

DESCRIPTION:
This is the primary command-line entry point for the Financial Reconciliation System.
It provides automated transaction reconciliation with comprehensive data quality
checks and detailed reporting capabilities.

FEATURES:
- Multi-bank transaction reconciliation (Chase, Wells Fargo, Discover, etc.)
- Double-entry bookkeeping with GAAP compliance
- Intelligent duplicate detection and data quality validation
- Baseline mode to prevent double-counting from known good states
- Comprehensive Excel and CSV report generation
- Configurable processing modes and parameters

USAGE:
    Basic reconciliation:
        python reconcile.py
    
    With date range:
        python reconcile.py --start-date 2024-01-01 --end-date 2024-12-31
    
    Baseline mode (recommended for production):
        python reconcile.py --mode from_baseline
    
    With custom configuration:
        python reconcile.py --config config/production.yaml

SUPPORTED MODES:
    - from_scratch: Complete reconciliation from beginning of data
    - from_baseline: Reconcile from established baseline date (prevents double-counting)

OUTPUT FILES:
    - output/reconciliation_report.txt: Human-readable summary
    - output/accounting_ledger.csv: Complete transaction ledger
    - output/manual_review_required.csv: Transactions requiring human review
    - output/data_quality_issues.csv: Data quality problems detected
    - output/audit_trail.csv: Complete audit trail of all decisions

PREREQUISITES:
    - Python 3.8+ with required packages (see requirements.txt)
    - Bank export CSV files in test-data/bank-exports/
    - Proper configuration in config/config.yaml

AUTHORS: Financial Reconciliation System Team
VERSION: 6.0.0
DATE: August 10, 2025
LICENSE: MIT License

For detailed documentation, see README.md and docs/ directory.
For troubleshooting, see docs/user-guide/TROUBLESHOOTING.md.
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the reconciliation process."""
    # Path to the actual reconciliation script
    script_path = Path(__file__).parent / "bin" / "financial-reconciliation"
    
    # Pass all command line arguments
    cmd = [sys.executable, str(script_path)] + sys.argv[1:]
    
    # Run the reconciliation with proper error handling
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running reconciliation: {e}", file=sys.stderr)
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return e.returncode

if __name__ == "__main__":
    sys.exit(main())