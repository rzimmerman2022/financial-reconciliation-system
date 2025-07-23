"""
Simple Phase 5A Runner - Uses existing transaction processor directly
===================================================================

Processes Sept 30 - Oct 18, 2024 with the $1,577.08 baseline.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Simply run the existing transaction processor with extended dates
from transaction_processor import TransactionProcessor

def main():
    print("\n" + "="*80)
    print("PHASE 5A RECONCILIATION - Sept 30 to Oct 18, 2024")
    print("Starting from baseline: Jordyn owes Ryan $1,577.08")
    print("="*80)
    
    # Create processor
    processor = TransactionProcessor(output_dir="output/phase5a_simple")
    
    # Load all data (existing method loads everything)
    all_transactions = processor.load_all_data()
    
    # Process with extended date range to include Oct 18
    processor.process_all_transactions(
        all_transactions,
        start_date="2024-01-01",  # Include everything from start
        cutoff_date="2024-10-18"  # Extended to Oct 18
    )
    
    # Generate outputs
    processor.generate_outputs()
    
    print("\nPhase 5A processing complete!")
    print("Check output/phase5a_simple/ for results")

if __name__ == "__main__":
    main()