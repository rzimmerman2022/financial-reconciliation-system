#!/usr/bin/env python3
"""
Run Gold Standard Reconciliation with Manual Review Integration
==============================================================

This script integrates the manual review system with the gold standard
reconciliation to handle Phase 5+ bank data that doesn't have manual review.

Workflow:
1. Run initial reconciliation
2. Export unreviewed transactions to manual review system
3. Allow user to review and classify transactions
4. Re-run reconciliation with manual review decisions applied

Author: Claude (Anthropic)
Date: July 29, 2025
"""

import pandas as pd
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import json
import sys

sys.path.append(str(Path(__file__).parent))

from gold_standard_reconciliation import GoldStandardReconciler, ReconciliationMode
from manual_review_system import (
    ManualReviewSystem, InteractiveReviewer, 
    TransactionCategory, SplitType, ReviewStatus
)


class ReconciliationWithReview:
    """Orchestrates reconciliation with manual review integration."""
    
    def __init__(self, review_db_path: str = "phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        self.reconciler = None
        
    def run_initial_reconciliation(self, mode: ReconciliationMode,
                                 phase4_start: datetime = None,
                                 phase4_end: datetime = None,
                                 phase5_start: datetime = None,
                                 phase5_end: datetime = None,
                                 baseline_date: datetime = None,
                                 baseline_amount: Decimal = None,
                                 baseline_who_owes: str = None):
        """Run initial reconciliation and export items for review."""
        
        print("\n" + "="*80)
        print("PHASE 1: INITIAL RECONCILIATION")
        print("="*80)
        
        # Initialize reconciler
        if mode == ReconciliationMode.FROM_BASELINE:
            self.reconciler = GoldStandardReconciler(
                mode=mode,
                baseline_date=baseline_date,
                baseline_amount=baseline_amount,
                baseline_who_owes=baseline_who_owes
            )
        else:
            self.reconciler = GoldStandardReconciler(mode=mode)
        
        # Run reconciliation
        self.reconciler.run_reconciliation(
            phase4_start=phase4_start,
            phase4_end=phase4_end,
            phase5_start=phase5_start,
            phase5_end=phase5_end
        )
        
        # Export items needing manual review
        if self.reconciler.manual_review_items:
            print(f"\n{len(self.reconciler.manual_review_items)} transactions need manual review")
            self._export_to_review_system()
        else:
            print("\nNo transactions need manual review!")
            
        return self.reconciler
    
    def _export_to_review_system(self):
        """Export flagged transactions to manual review database."""
        print("\nExporting transactions to manual review system...")
        
        count = 0
        for item in self.reconciler.manual_review_items:
            # Skip if it's just a data quality issue (missing amount)
            if item.get('amount', 0) == 0:
                continue
                
            review_id = self.review_system.add_transaction_for_review(
                date=item['date'],
                description=item['description'],
                amount=Decimal(str(item['amount'])),
                payer=item['payer'],
                source=item.get('source', 'Unknown')
            )
            count += 1
            
        print(f"[DONE] Exported {count} transactions for manual review")
    
    def run_manual_review(self):
        """Launch interactive review interface."""
        print("\n" + "="*80)
        print("PHASE 2: MANUAL REVIEW")
        print("="*80)
        
        # Get pending review count
        pending = self.review_system.get_pending_reviews()
        if pending.empty:
            print("No transactions pending review!")
            return
            
        print(f"\n{len(pending)} transactions need manual review")
        print("\nLaunching review interface...")
        print("-" * 60)
        
        reviewer = InteractiveReviewer(self.review_system)
        reviewer.run()
    
    def apply_manual_reviews_and_reconcile(self, 
                                         phase5_start: datetime,
                                         phase5_end: datetime):
        """Load manual review decisions and re-run reconciliation."""
        print("\n" + "="*80)
        print("PHASE 3: RECONCILIATION WITH MANUAL REVIEWS APPLIED")
        print("="*80)
        
        # Get completed reviews
        completed_reviews = self.review_system.export_reviews(
            status=ReviewStatus.COMPLETED
        )
        
        if completed_reviews.empty:
            print("No completed reviews found!")
            return
            
        print(f"\nFound {len(completed_reviews)} completed reviews")
        
        # Convert reviews to format expected by reconciliation
        review_lookup = {}
        for _, review in completed_reviews.iterrows():
            key = f"{review['date']}_{review['description']}_{review['amount']}"
            
            # Determine allowed amount based on review
            if review['is_personal'] == 1:
                allowed_amount = Decimal('0')  # Personal expense
            else:
                # Use the reviewed amount (could be adjusted)
                allowed_amount = Decimal(str(review.get('allowed_amount', review['amount'])))
            
            review_lookup[key] = {
                'allowed_amount': allowed_amount,
                'category': review['category'],
                'split_type': review['split_type'],
                'is_personal': review['is_personal'] == 1,
                'notes': review.get('notes', '')
            }
        
        # Create enhanced Phase 5 data with manual reviews
        print("\nLoading Phase 5 data with manual reviews applied...")
        phase5_df = self._load_phase5_with_reviews(
            phase5_start, phase5_end, review_lookup
        )
        
        # Run final reconciliation
        print("\nRunning final reconciliation...")
        final_reconciler = GoldStandardReconciler(
            mode=ReconciliationMode.FROM_BASELINE,
            baseline_date=datetime(2024, 9, 30),
            baseline_amount=Decimal('1577.08'),
            baseline_who_owes='Jordyn owes Ryan'
        )
        
        # Process the enhanced Phase 5 data
        for idx, row in phase5_df.iterrows():
            final_reconciler.process_transaction(row)
            if (idx + 1) % 50 == 0:
                print(f"  Processed {idx + 1} transactions...")
        
        # Validate and generate reports
        print("\nValidating accounting invariants...")
        final_reconciler.engine.validate_invariant()
        print("[DONE] All invariants validated")
        
        # Generate final reports
        output_dir = "output/gold_standard_with_manual_review"
        print(f"\nGenerating reports in {output_dir}...")
        final_reconciler.generate_comprehensive_report(output_dir)
        
        # Final summary
        final_balance = final_reconciler._get_current_balance()
        print("\n" + "="*80)
        print("FINAL RECONCILIATION WITH MANUAL REVIEWS")
        print("="*80)
        print(f"Final Balance: ${final_balance['amount']:,.2f}")
        print(f"Status: {final_balance['who_owes']}")
        print(f"Manual Reviews Applied: {len(review_lookup)}")
        print("="*80)
        
        return final_reconciler
    
    def _load_phase5_with_reviews(self, start_date: datetime, end_date: datetime,
                                  review_lookup: dict) -> pd.DataFrame:
        """Load Phase 5 data and apply manual review decisions."""
        # Use the reconciler's method to load bank data
        temp_reconciler = GoldStandardReconciler()
        phase5_df = temp_reconciler.load_bank_data(start_date, end_date)
        
        # Apply manual reviews
        for idx, row in phase5_df.iterrows():
            key = f"{row['date']}_{row['description']}_{row['amount']}"
            
            if key in review_lookup:
                review = review_lookup[key]
                # Apply manual review decisions
                phase5_df.at[idx, 'has_manual_review'] = True
                phase5_df.at[idx, 'allowed_amount'] = float(review['allowed_amount'])
                phase5_df.at[idx, 'is_personal'] = review['is_personal']
                phase5_df.at[idx, 'review_category'] = review['category']
                phase5_df.at[idx, 'review_split_type'] = review['split_type']
                phase5_df.at[idx, 'review_notes'] = review['notes']
                
                # Update amount to use allowed_amount
                phase5_df.at[idx, 'amount'] = float(review['allowed_amount'])
        
        return phase5_df
    
    def generate_review_summary(self):
        """Generate summary of manual review statistics."""
        stats = self.review_system.get_review_statistics()
        
        print("\n" + "="*60)
        print("MANUAL REVIEW STATISTICS")
        print("="*60)
        
        print("\nBy Status:")
        for status, count in stats.get('by_status', {}).items():
            print(f"  {status}: {count}")
        
        print("\nBy Category:")
        for category, count in sorted(stats.get('by_category', {}).items()):
            print(f"  {category}: {count}")
        
        print("\nBy Split Type:")
        for split, count in stats.get('by_split_type', {}).items():
            print(f"  {split}: {count}")
        
        print(f"\nPersonal vs Shared:")
        print(f"  Personal: {stats['personal_vs_shared']['personal']}")
        print(f"  Shared: {stats['personal_vs_shared']['shared']}")
        
        print(f"\nAverage Review Time: {stats['avg_review_time_hours']:.1f} hours")


def main():
    """Run the complete reconciliation workflow with manual review."""
    
    print("\n" + "="*80)
    print("GOLD STANDARD RECONCILIATION WITH MANUAL REVIEW SYSTEM")
    print("="*80)
    
    # Initialize the system
    system = ReconciliationWithReview()
    
    # Phase 1: Initial reconciliation
    reconciler = system.run_initial_reconciliation(
        mode=ReconciliationMode.FROM_BASELINE,
        baseline_date=datetime(2024, 9, 30),
        baseline_amount=Decimal('1577.08'),
        baseline_who_owes='Jordyn owes Ryan',
        phase5_start=datetime(2024, 10, 1),
        phase5_end=datetime(2024, 10, 31)
    )
    
    # Check if manual review is needed
    pending = system.review_system.get_pending_reviews()
    if not pending.empty:
        print(f"\n{len(pending)} transactions need manual review.")
        print("Options:")
        print("1. Run manual review interface")
        print("2. Skip manual review (use defaults)")
        print("3. Exit")
        
        # Auto-select option 2 for non-interactive mode
        print("\nAuto-selecting option 2: Skip manual review (use defaults)")
        choice = '2'
        
        if choice == '1':
            # Phase 2: Manual review
            system.run_manual_review()
            
            # Phase 3: Re-run with reviews applied
            system.apply_manual_reviews_and_reconcile(
                phase5_start=datetime(2024, 10, 1),
                phase5_end=datetime(2024, 10, 31)
            )
            
            # Generate review summary
            system.generate_review_summary()
            
        elif choice == '2':
            print("\nSkipping manual review - using default 50/50 splits")
        else:
            print("\nExiting...")
            return
    
    print("\n[DONE] Reconciliation complete!")


if __name__ == "__main__":
    main()