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