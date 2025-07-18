"""
Financial Reconciliation System - Main Entry Point

This script demonstrates the core functionality of the financial reconciliation system.
It loads data from all three CSV sources and provides a comprehensive overview.
"""

import logging
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from loaders import ExpenseHistoryLoader, RentAllocationLoader, ZellePaymentsLoader


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('output/reconciliation.log')
        ]
    )


def load_all_data():
    """Load data from all three CSV sources."""
    
    print("=" * 60)
    print("FINANCIAL RECONCILIATION SYSTEM")
    print("=" * 60)
    print()
    
    # Load expense history
    print("1. Loading Expense History...")
    expense_loader = ExpenseHistoryLoader()
    expense_data = expense_loader.load_raw_data()
    expense_summary = expense_loader.get_data_summary()
    expense_validation = expense_loader.validate_structure()
    
    print(f"   ✓ Loaded {len(expense_data)} expense records")
    print(f"   ✓ Date range coverage: {expense_summary.get('date_range', 'Unknown')}")
    print(f"   ✓ People: Ryan ({expense_summary['people'].get('Ryan', 0)} records), "
          f"Jordyn ({expense_summary['people'].get('Jordyn', 0) + expense_summary['people'].get('Jordyn ', 0)} records)")
    if not expense_validation['is_valid']:
        print(f"   ⚠ Validation issues: {len(expense_validation['issues'])} found")
    print()
    
    # Load rent allocation
    print("2. Loading Rent Allocation...")
    rent_loader = RentAllocationLoader()
    rent_data = rent_loader.load_raw_data()
    rent_summary = rent_loader.get_data_summary()
    rent_validation = rent_loader.validate_structure()
    
    print(f"   ✓ Loaded {len(rent_data)} rent allocation records")
    print(f"   ✓ Months covered: {len(rent_summary['months_covered'])} months")
    if 'rent_statistics' in rent_summary and rent_summary['rent_statistics']:
        stats = rent_summary['rent_statistics']
        print(f"   ✓ Average rent: ${stats.get('avg_gross_rent', 0):.2f}")
        print(f"   ✓ Ryan's share: {stats.get('ryan_percentage', 0):.1f}%, "
              f"Jordyn's share: {stats.get('jordyn_percentage', 0):.1f}%")
    print()
    
    # Load Zelle payments
    print("3. Loading Zelle Payments...")
    zelle_loader = ZellePaymentsLoader()
    zelle_data = zelle_loader.load_raw_data()
    zelle_summary = zelle_loader.get_data_summary()
    zelle_validation = zelle_loader.validate_structure()
    
    print(f"   ✓ Loaded {len(zelle_data)} Zelle payment records")
    if 'payment_statistics' in zelle_summary:
        stats = zelle_summary['payment_statistics']
        print(f"   ✓ Total Zelle payments: ${stats.get('total_amount', 0):,.2f}")
        print(f"   ✓ Average payment: ${stats.get('average_payment', 0):.2f}")
    if 'date_range' in zelle_summary:
        dr = zelle_summary['date_range']
        print(f"   ✓ Date range: {dr.get('earliest')} to {dr.get('latest')}")
    print()
    
    # Summary validation report
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_valid = True
    
    if not expense_validation['is_valid']:
        print("❌ Expense History Issues:")
        for issue in expense_validation['issues'][:5]:  # Show first 5 issues
            print(f"   • {issue}")
        if len(expense_validation['issues']) > 5:
            print(f"   • ... and {len(expense_validation['issues']) - 5} more issues")
        all_valid = False
        print()
    
    if not rent_validation['is_valid']:
        print("❌ Rent Allocation Issues:")
        for issue in rent_validation['issues']:
            print(f"   • {issue}")
        all_valid = False
        print()
    
    if not zelle_validation['is_valid']:
        print("❌ Zelle Payments Issues:")
        for issue in zelle_validation['issues']:
            print(f"   • {issue}")
        all_valid = False
        print()
    
    if all_valid:
        print("✅ All data sources passed validation!")
        print()
    
    # Key insights
    print("=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    
    # Business logic validation
    print("📊 Business Logic Validation:")
    print("   • Jordyn pays full rent to landlord")
    print(f"   • Ryan owes ~{rent_summary['rent_statistics'].get('ryan_percentage', 0):.0f}% back to Jordyn")
    print("   • Zelle payments are for expense reimbursements")
    print()
    
    # Financial summary
    if 'payment_statistics' in zelle_summary and 'rent_statistics' in rent_summary:
        total_zelle = zelle_summary['payment_statistics'].get('total_amount', 0)
        avg_monthly_rent = rent_summary['rent_statistics'].get('avg_gross_rent', 0)
        ryan_monthly_share = rent_summary['rent_statistics'].get('avg_ryan_share', 0)
        
        print("💰 Financial Overview:")
        print(f"   • Total Zelle payments from Jordyn: ${total_zelle:,.2f}")
        print(f"   • Average monthly rent (gross): ${avg_monthly_rent:.2f}")
        print(f"   • Ryan's average monthly rent obligation: ${ryan_monthly_share:.2f}")
        print()
    
    # Next steps
    print("=" * 60)
    print("NEXT DEVELOPMENT STEPS")
    print("=" * 60)
    print("1. ✅ CSV Loaders - COMPLETED")
    print("2. 🔄 Data Processors - IN PROGRESS")
    print("3. 📋 Reconciliation Engine - PENDING")
    print("4. 🧪 Unit Tests - PENDING")
    print("5. 📊 Audit Trail Generator - PENDING")
    print()
    
    return {
        'expense_data': expense_data,
        'rent_data': rent_data,
        'zelle_data': zelle_data,
        'summaries': {
            'expense': expense_summary,
            'rent': rent_summary,
            'zelle': zelle_summary
        },
        'validations': {
            'expense': expense_validation,
            'rent': rent_validation,
            'zelle': zelle_validation
        }
    }


def main():
    """Main entry point."""
    # Ensure output directory exists
    Path("output").mkdir(exist_ok=True)
    
    # Set up logging
    setup_logging()
    
    try:
        # Load and analyze all data
        results = load_all_data()
        
        # Log completion
        logger = logging.getLogger(__name__)
        logger.info("Financial reconciliation system initialization completed successfully")
        
        print("System ready for further development!")
        return results
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error during initialization: {e}")
        print(f"❌ Error: {e}")
        return None


if __name__ == "__main__":
    main()
