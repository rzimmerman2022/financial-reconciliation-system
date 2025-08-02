#!/usr/bin/env python3
"""
Main entry point for the Financial Reconciliation System.
This script provides a simple interface to run reconciliation.
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
    
    # Run the reconciliation
    return subprocess.call(cmd)

if __name__ == "__main__":
    sys.exit(main())