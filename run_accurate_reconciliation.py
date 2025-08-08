#!/usr/bin/env python3
"""
High-Accuracy Reconciliation Runner
====================================

This script runs the reconciliation with maximum accuracy improvements for a one-time
execution. It prioritizes correctness over performance.

Key features:
1. Enhanced duplicate detection
2. Robust date and amount parsing  
3. Improved description pattern matching
4. Comprehensive validation
5. Detailed logging of issues
6. Manual review preservation (no automatic 50/50 defaults)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import pandas as pd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.reconciliation_engine import GoldStandardReconciler, ReconciliationMode
from src.core.accuracy_improvements import apply_accuracy_improvements, AccuracyValidator
from src.review.manual_review_system import ManualReviewSystem
from src.core.accounting_engine import AccountingEngine

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/accurate_reconciliation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AccurateReconciliationRunner:
    """Runs reconciliation with maximum accuracy."""
    
    def __init__(self):
        self.reconciler = None
        self.validator = None
        self.review_system = None
        self.issues_found = []
        
    def initialize(self):
        """Initialize all components with accuracy improvements."""
        logger.info("=" * 80)
        logger.info("ACCURATE RECONCILIATION SYSTEM - INITIALIZATION")
        logger.info("=" * 80)
        
        # Initialize reconciler with baseline mode to avoid double-counting
        self.reconciler = GoldStandardReconciler(
            mode=ReconciliationMode.FROM_BASELINE,
            manual_review_db="data/phase5_manual_reviews.db"
        )
        
        # Apply accuracy improvements
        logger.info("Applying accuracy improvements...")
        self.validator = apply_accuracy_improvements(self.reconciler)
        
        # Initialize manual review system
        self.review_system = ManualReviewSystem("data/phase5_manual_reviews.db")
        
        logger.info("Initialization complete")
        
    def validate_data_sources(self):
        """Validate all data sources before processing."""
        logger.info("\n" + "=" * 80)
        logger.info("DATA SOURCE VALIDATION")
        logger.info("=" * 80)
        
        issues = []
        
        # Check for required data files
        required_files = [
            "data/raw/expense_history.csv",
            "data/raw/rent_allocation.csv",
            "data/raw/zelle_payments.csv"
        ]
        
        for file_path in required_files:
            path = Path(file_path)
            if not path.exists():
                issues.append(f"Missing required file: {file_path}")
            else:
                # Validate file content
                try:
                    df = pd.read_csv(path)
                    if df.empty:
                        issues.append(f"Empty file: {file_path}")
                    else:
                        logger.info(f"✓ {file_path}: {len(df)} records")
                except Exception as e:
                    issues.append(f"Cannot read {file_path}: {e}")
        
        # Check bank export directories
        bank_dirs = [
            "test-data/bank-exports/ryan",
            "test-data/bank-exports/jordyn"
        ]
        
        for dir_path in bank_dirs:
            path = Path(dir_path)
            if not path.exists():
                issues.append(f"Missing bank export directory: {dir_path}")
            else:
                csv_files = list(path.glob("*.csv"))
                if not csv_files:
                    issues.append(f"No CSV files in: {dir_path}")
                else:
                    logger.info(f"✓ {dir_path}: {len(csv_files)} CSV files")
        
        if issues:
            logger.error("Data validation issues found:")
            for issue in issues:
                logger.error(f"  - {issue}")
            self.issues_found.extend(issues)
        else:
            logger.info("All data sources validated successfully")
        
        return len(issues) == 0
    
    def check_manual_reviews(self):
        """Check status of manual reviews."""
        logger.info("\n" + "=" * 80)
        logger.info("MANUAL REVIEW STATUS")
        logger.info("=" * 80)
        
        pending = self.review_system.get_pending_reviews()
        completed = self.review_system.get_completed_reviews()
        
        logger.info(f"Pending reviews: {len(pending)}")
        logger.info(f"Completed reviews: {len(completed)}")
        
        if len(pending) > 0:
            logger.warning(f"\n⚠️  There are {len(pending)} transactions awaiting manual review")
            logger.warning("These will NOT be automatically split 50/50")
            logger.warning("To review them:")
            logger.warning("  1. Run: python -m src.review.modern_visual_review_gui")
            logger.warning("  2. Or: python -m src.review.web_interface")
            
            # Show sample of pending reviews
            logger.info("\nSample of pending reviews:")
            for _, row in pending.head(5).iterrows():
                logger.info(f"  - {row['date']}: ${row['amount']:.2f} - {row['description'][:50]}")
        
        return len(pending)
    
    def run_reconciliation(self):
        """Run the reconciliation with all accuracy improvements."""
        logger.info("\n" + "=" * 80)
        logger.info("RUNNING ACCURATE RECONCILIATION")
        logger.info("=" * 80)
        
        try:
            # Set date range
            start_date = datetime(2024, 10, 1)  # After Phase 4 baseline
            end_date = datetime(2025, 1, 31)    # Current period
            
            logger.info(f"Date range: {start_date.date()} to {end_date.date()}")
            logger.info(f"Mode: {self.reconciler.mode.value}")
            
            # Run reconciliation
            self.reconciler.run_reconciliation(
                start_date=start_date,
                end_date=end_date
            )
            
            # Check for validation warnings
            if self.validator.warnings:
                logger.warning(f"\n⚠️  {len(self.validator.warnings)} validation warnings:")
                for warning in self.validator.warnings[:10]:  # Show first 10
                    logger.warning(f"  - {warning}")
            
            if self.validator.validation_errors:
                logger.error(f"\n❌ {len(self.validator.validation_errors)} validation errors:")
                for error in self.validator.validation_errors[:10]:  # Show first 10
                    logger.error(f"  - {error}")
            
            return True
            
        except Exception as e:
            logger.error(f"Reconciliation failed: {e}", exc_info=True)
            return False
    
    def generate_accuracy_report(self):
        """Generate detailed accuracy report."""
        logger.info("\n" + "=" * 80)
        logger.info("ACCURACY REPORT")
        logger.info("=" * 80)
        
        # Get final balances
        balances = self.reconciler.engine.get_final_balance()
        
        logger.info("\nFinal Balances:")
        logger.info(f"  Who owes: {balances['who_owes']}")
        logger.info(f"  Amount: ${balances['amount']:.2f}")
        
        # Transaction statistics
        stats = self.reconciler.stats
        logger.info("\nTransaction Statistics:")
        logger.info(f"  Total processed: {stats['transactions_processed']}")
        logger.info(f"  Data quality issues: {stats['data_quality_issues']}")
        logger.info(f"  Manual reviews needed: {stats['manual_reviews_needed']}")
        logger.info(f"  Personal expenses excluded: {stats['personal_expenses_excluded']}")
        
        # Category breakdown
        logger.info("\nCategory Breakdown:")
        for category, count in sorted(stats['by_category'].items()):
            logger.info(f"  {category}: {count}")
        
        # Action breakdown
        logger.info("\nAction Breakdown:")
        for action, count in sorted(stats['by_action'].items()):
            logger.info(f"  {action}: {count}")
        
        # Accuracy metrics
        logger.info("\nAccuracy Metrics:")
        total_tx = stats['transactions_processed']
        if total_tx > 0:
            accuracy_score = 100 * (1 - (stats['data_quality_issues'] / total_tx))
            logger.info(f"  Data quality score: {accuracy_score:.1f}%")
            
            if stats['manual_reviews_needed'] > 0:
                review_rate = 100 * (stats['manual_reviews_needed'] / total_tx)
                logger.info(f"  Manual review rate: {review_rate:.1f}%")
        
        # Save detailed report
        report_path = Path("output/accuracy_report.txt")
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("ACCURATE RECONCILIATION REPORT\n")
            f.write(f"Generated: {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("FINAL BALANCE\n")
            f.write(f"Who owes: {balances['who_owes']}\n")
            f.write(f"Amount: ${balances['amount']:.2f}\n\n")
            
            f.write("STATISTICS\n")
            f.write(f"Total transactions: {stats['transactions_processed']}\n")
            f.write(f"Data quality issues: {stats['data_quality_issues']}\n")
            f.write(f"Manual reviews needed: {stats['manual_reviews_needed']}\n\n")
            
            if self.validator.warnings:
                f.write("WARNINGS\n")
                for warning in self.validator.warnings:
                    f.write(f"- {warning}\n")
                f.write("\n")
            
            if self.validator.validation_errors:
                f.write("ERRORS\n")
                for error in self.validator.validation_errors:
                    f.write(f"- {error}\n")
        
        logger.info(f"\nDetailed report saved to: {report_path}")
    
    def run(self):
        """Main execution flow."""
        try:
            # Initialize
            self.initialize()
            
            # Validate data
            if not self.validate_data_sources():
                logger.error("Data validation failed. Please fix issues before continuing.")
                return False
            
            # Check manual reviews
            pending_count = self.check_manual_reviews()
            
            if pending_count > 0:
                response = input(f"\n⚠️  Continue with {pending_count} pending reviews? (y/n): ")
                if response.lower() != 'y':
                    logger.info("Reconciliation cancelled. Please complete manual reviews first.")
                    return False
            
            # Run reconciliation
            if not self.run_reconciliation():
                logger.error("Reconciliation failed")
                return False
            
            # Generate report
            self.generate_accuracy_report()
            
            logger.info("\n" + "=" * 80)
            logger.info("✅ ACCURATE RECONCILIATION COMPLETED SUCCESSFULLY")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            return False


def main():
    """Main entry point."""
    runner = AccurateReconciliationRunner()
    success = runner.run()
    
    if not success:
        logger.error("\n❌ Reconciliation failed. Check logs for details.")
        sys.exit(1)
    else:
        logger.info("\n✅ Reconciliation completed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()