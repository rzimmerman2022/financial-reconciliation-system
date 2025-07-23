"""
Phase 5A Data Loader: September 30 - October 18, 2024
======================================================

This module loads and processes transaction data for the 18-day reconciliation period
from September 30, 2024 through October 18, 2024.

Starting baseline: Jordyn owes Ryan $1,577.08 (as of September 30, 2024)

Data Sources:
- Ryan: BALANCE_RZ_MonarchMoney_Ledger_20220918-20250718.csv (77 transactions)
- Ryan: BALANCE_RZ_RocketMoney_Ledger_20220915-20250720.csv (85 transactions)
- Jordyn: BALANCE_JG_Chase_6173_Ledger_20231215-20250313.csv (11 transactions)
- Jordyn: BALANCE_JG_WellsFargo_4296_Transactions_20240417-20251231.csv (30 transactions)
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime
import logging
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from data_loader import clean_currency, parse_flexible_date

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Phase 5A date range
START_DATE = "2024-09-30"
END_DATE = "2024-10-18"

# Starting baseline
STARTING_BALANCE = Decimal("1577.08")  # Jordyn owes Ryan


def parse_balance_date(date_str: str) -> datetime:
    """
    Parse date format from BALANCE files: "MM / DD / YY"
    """
    if pd.isna(date_str) or not date_str:
        return pd.NaT
    
    try:
        # Remove extra spaces and parse
        date_clean = date_str.strip().replace(" ", "")
        return pd.to_datetime(date_clean, format="%m/%d/%y")
    except:
        logger.warning(f"Could not parse date: {date_str}")
        return pd.NaT


def load_ryan_balance_data(monarch_path: str, rocket_path: str) -> pd.DataFrame:
    """
    Load and combine Ryan's transaction data from both Monarch and Rocket Money.
    
    Returns:
        Combined DataFrame with standardized columns
    """
    all_ryan_data = []
    
    # Load Monarch Money data
    logger.info(f"Loading Ryan's Monarch Money data...")
    monarch_df = pd.read_csv(monarch_path)
    
    # Parse dates and filter
    monarch_df['date'] = pd.to_datetime(monarch_df['Date'])
    mask = (monarch_df['date'] >= START_DATE) & (monarch_df['date'] <= END_DATE)
    monarch_filtered = monarch_df[mask].copy()
    
    # Standardize columns
    monarch_std = pd.DataFrame({
        'date': monarch_filtered['date'],
        'payer': 'Ryan',
        'description': monarch_filtered['Merchant'].fillna('Unknown'),
        'amount': monarch_filtered['Amount'].apply(clean_currency),
        'category': monarch_filtered['Category'].fillna('Uncategorized'),
        'source': 'Ryan_Monarch',
        'original_description': monarch_filtered.get('Original Statement', '')
    })
    all_ryan_data.append(monarch_std)
    logger.info(f"  Found {len(monarch_std)} Monarch transactions")
    
    # Load Rocket Money data
    logger.info(f"Loading Ryan's Rocket Money data...")
    rocket_df = pd.read_csv(rocket_path)
    
    # Parse dates and filter
    rocket_df['date'] = pd.to_datetime(rocket_df['Date'])
    mask = (rocket_df['date'] >= START_DATE) & (rocket_df['date'] <= END_DATE)
    rocket_filtered = rocket_df[mask].copy()
    
    # Standardize columns
    rocket_std = pd.DataFrame({
        'date': rocket_filtered['date'],
        'payer': 'Ryan',
        'description': rocket_filtered['Name'].fillna(rocket_filtered['Description'].fillna('Unknown')),
        'amount': rocket_filtered['Amount'].apply(clean_currency),
        'category': rocket_filtered['Category'].fillna('Uncategorized'),
        'source': 'Ryan_Rocket',
        'original_description': rocket_filtered['Description'].fillna('')
    })
    all_ryan_data.append(rocket_std)
    logger.info(f"  Found {len(rocket_std)} Rocket transactions")
    
    # Combine all Ryan data
    combined_ryan = pd.concat(all_ryan_data, ignore_index=True)
    logger.info(f"Total Ryan transactions: {len(combined_ryan)}")
    
    return combined_ryan


def load_jordyn_balance_data(chase_path: str, wells_path: str) -> pd.DataFrame:
    """
    Load and combine Jordyn's transaction data from Chase and Wells Fargo.
    
    Returns:
        Combined DataFrame with standardized columns
    """
    all_jordyn_data = []
    
    # Load Chase Bank data
    logger.info(f"Loading Jordyn's Chase Bank data...")
    chase_df = pd.read_csv(chase_path)
    
    # Skip the beginning balance row and parse dates
    chase_df = chase_df[chase_df['Trans. Date'].notna()].copy()
    chase_df['date'] = chase_df['Trans. Date'].apply(parse_balance_date)
    
    # Filter to date range
    mask = (chase_df['date'] >= START_DATE) & (chase_df['date'] <= END_DATE)
    chase_filtered = chase_df[mask].copy()
    
    # Standardize columns
    chase_std = pd.DataFrame({
        'date': chase_filtered['date'],
        'payer': 'Jordyn',
        'description': chase_filtered['Description'].fillna('Unknown'),
        'amount': chase_filtered['Amount'].apply(clean_currency),
        'category': chase_filtered['Category'].fillna('Banking'),
        'source': 'Jordyn_Chase',
        'original_description': chase_filtered['Description'].fillna('')
    })
    all_jordyn_data.append(chase_std)
    logger.info(f"  Found {len(chase_std)} Chase transactions")
    
    # Load Wells Fargo data
    logger.info(f"Loading Jordyn's Wells Fargo data...")
    wells_df = pd.read_csv(wells_path)
    
    # Parse dates
    wells_df['date'] = wells_df['Trans. Date'].apply(parse_balance_date)
    
    # Filter to date range
    mask = (wells_df['date'] >= START_DATE) & (wells_df['date'] <= END_DATE)
    wells_filtered = wells_df[mask].copy()
    
    # Standardize columns
    wells_std = pd.DataFrame({
        'date': wells_filtered['date'],
        'payer': 'Jordyn',
        'description': wells_filtered['Description'].fillna('Unknown'),
        'amount': wells_filtered['Amount'].apply(clean_currency),
        'category': wells_filtered['Category'].fillna('Credit Card'),
        'source': 'Jordyn_Wells_Fargo',
        'original_description': wells_filtered['Description'].fillna('')
    })
    all_jordyn_data.append(wells_std)
    logger.info(f"  Found {len(wells_std)} Wells Fargo transactions")
    
    # Combine all Jordyn data
    combined_jordyn = pd.concat(all_jordyn_data, ignore_index=True)
    logger.info(f"Total Jordyn transactions: {len(combined_jordyn)}")
    
    return combined_jordyn


def load_phase5a_data() -> pd.DataFrame:
    """
    Load all Phase 5A data and combine into a single DataFrame.
    
    Returns:
        Combined DataFrame with all transactions for Sept 30 - Oct 18, 2024
    """
    logger.info("\n" + "="*60)
    logger.info("PHASE 5A DATA LOADING")
    logger.info(f"Date Range: {START_DATE} to {END_DATE}")
    logger.info(f"Starting Balance: Jordyn owes Ryan ${STARTING_BALANCE}")
    logger.info("="*60 + "\n")
    
    # Define file paths
    base_path = Path("new_raw")
    
    # Load Ryan's data
    ryan_data = load_ryan_balance_data(
        str(base_path / "BALANCE_RZ_MonarchMoney_Ledger_20220918-20250718.csv"),
        str(base_path / "BALANCE_RZ_RocketMoney_Ledger_20220915-20250720.csv")
    )
    
    # Load Jordyn's data
    jordyn_data = load_jordyn_balance_data(
        str(base_path / "BALANCE_JG_Chase_6173_Ledger_20231215-20250313.csv"),
        str(base_path / "BALANCE_JG_WellsFargo_4296_Transactions_20240417-20251231.csv")
    )
    
    # Combine all data
    all_data = pd.concat([ryan_data, jordyn_data], ignore_index=True)
    
    # Sort by date and payer
    all_data = all_data.sort_values(['date', 'payer'])
    
    # Remove duplicates based on date, payer, description, and amount
    # This handles cases where same transaction appears in both Monarch and Rocket
    all_data['dedup_key'] = (
        all_data['date'].astype(str) + '_' +
        all_data['payer'] + '_' +
        all_data['description'].str[:20] + '_' +
        all_data['amount'].astype(str)
    )
    
    before_dedup = len(all_data)
    all_data = all_data.drop_duplicates(subset=['dedup_key'], keep='first')
    after_dedup = len(all_data)
    
    if before_dedup != after_dedup:
        logger.info(f"Removed {before_dedup - after_dedup} duplicate transactions")
    
    # Drop the dedup key
    all_data = all_data.drop(columns=['dedup_key'])
    
    # Final summary
    logger.info("\n" + "="*60)
    logger.info("PHASE 5A DATA SUMMARY")
    logger.info("="*60)
    logger.info(f"Total transactions: {len(all_data)}")
    logger.info(f"  Ryan: {len(all_data[all_data['payer'] == 'Ryan'])}")
    logger.info(f"  Jordyn: {len(all_data[all_data['payer'] == 'Jordyn'])}")
    logger.info(f"Date range: {all_data['date'].min()} to {all_data['date'].max()}")
    
    # Check for rent payments
    rent_keywords = ['rent', 'san palmas', 'apartment']
    rent_mask = all_data['description'].str.lower().str.contains('|'.join(rent_keywords), na=False)
    logger.info(f"Potential rent payments: {rent_mask.sum()}")
    
    # Check for Zelle/Venmo transfers
    transfer_keywords = ['zelle', 'venmo', 'transfer to ryan', 'transfer to jordyn']
    transfer_mask = all_data['description'].str.lower().str.contains('|'.join(transfer_keywords), na=False)
    logger.info(f"Potential transfers: {transfer_mask.sum()}")
    
    return all_data


def save_phase5a_data(df: pd.DataFrame, output_path: str = "output/phase5a_combined_data.csv"):
    """
    Save the combined Phase 5A data to CSV for review.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(exist_ok=True)
    
    # Save with proper formatting
    df.to_csv(output_path, index=False, date_format='%Y-%m-%d')
    logger.info(f"\nSaved combined data to: {output_path}")


if __name__ == "__main__":
    # Load all Phase 5A data
    phase5a_data = load_phase5a_data()
    
    # Save for review
    save_phase5a_data(phase5a_data)
    
    # Show sample transactions
    print("\n" + "="*60)
    print("SAMPLE TRANSACTIONS")
    print("="*60)
    print("\nFirst 5 transactions:")
    print(phase5a_data[['date', 'payer', 'description', 'amount', 'source']].head())
    
    print("\nLast 5 transactions:")
    print(phase5a_data[['date', 'payer', 'description', 'amount', 'source']].tail())
    
    print("\n" + "="*60)
    print("Ready for Phase 5A reconciliation!")
    print(f"Starting balance: Jordyn owes Ryan ${STARTING_BALANCE}")
    print(f"Processing {len(phase5a_data)} transactions from {START_DATE} to {END_DATE}")