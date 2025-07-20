"""
Data Loader Module for Financial Reconciliation System - Phase 2

This module provides utilities for loading and cleaning the raw CSV data files
for the financial reconciliation system. It handles the specific formatting
issues found in the raw data, including column names with spaces and various
currency/date formats.

CRITICAL: This module handles the actual CSV column names which include spaces:
- ' Actual Amount ' (with leading/trailing spaces)
- ' Merchant Description ' (with spaces)

Integration: Works with description_decoder.py from Phase 1 for transaction analysis
"""

import pandas as pd
from decimal import Decimal, InvalidOperation
import re
from datetime import datetime
from typing import Optional, Union, Dict, Any
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names by removing spaces and converting to lowercase with underscores.
    
    Handles the actual column names from the CSV files which include spaces:
    - ' Actual Amount ' → 'actual_amount'
    - ' Merchant Description ' → 'merchant_description'
    - 'Date of Purchase' → 'date_of_purchase'
    
    Args:
        df: DataFrame with potentially messy column names
        
    Returns:
        DataFrame with cleaned column names
    """
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Clean column names: strip whitespace, lowercase, replace spaces with underscores
    df_clean.columns = [
        re.sub(r'\s+', '_', col.strip()).lower() for col in df_clean.columns
    ]
    
    logger.info(f"Cleaned column names: {list(df_clean.columns)}")
    
    return df_clean


def clean_currency(value: Union[str, float, None]) -> Optional[Decimal]:
    """
    Clean currency values and convert to Decimal for precision.
    
    Handles various formats:
    - '$84.39 ' (with spaces)
    - '$(15.00)' (negative values in parentheses)
    - '$ -' (empty/invalid values)
    - NaN values
    - Already numeric values
    
    Args:
        value: The currency value to clean
        
    Returns:
        Decimal value or None if invalid
    """
    if pd.isna(value):
        return None
        
    # If already numeric, convert directly
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    
    # Convert to string and clean
    value_str = str(value).strip()
    
    # Handle empty or invalid values
    if not value_str or value_str in ['$ -', '$-', '-', '']:
        return None
    
    # Remove currency symbols and spaces
    value_str = value_str.replace('$', '').replace(',', '').strip()
    
    # Handle negative values in parentheses
    if value_str.startswith('(') and value_str.endswith(')'):
        value_str = '-' + value_str[1:-1]
    
    try:
        return Decimal(value_str)
    except (InvalidOperation, ValueError) as e:
        logger.warning(f"Could not convert '{value}' to Decimal: {e}")
        return None


def parse_flexible_date(date_str: Union[str, datetime, pd.Timestamp]) -> Optional[datetime]:
    """
    Parse dates in various formats.
    
    Handles:
    - '9/14/2023' format (M/D/YYYY)
    - '24-Jan' format (D-Mon, assumes current year)
    - datetime/Timestamp objects
    - NaN values
    
    Args:
        date_str: The date string or object to parse
        
    Returns:
        datetime object or None if invalid
    """
    if pd.isna(date_str):
        return None
    
    # If already a datetime/Timestamp, convert to datetime
    if isinstance(date_str, (pd.Timestamp, datetime)):
        return pd.to_datetime(date_str).to_pydatetime()
    
    date_str = str(date_str).strip()
    
    if not date_str:
        return None
    
    # Common date formats to try
    date_formats = [
        '%m/%d/%Y',      # 9/14/2023
        '%m/%d/%y',      # 9/14/23
        '%Y-%m-%d',      # 2023-09-14
        '%d-%b',         # 24-Jan (will need year added)
        '%d-%B',         # 24-January
        '%b %d',         # Jan 24
        '%B %d',         # January 24
    ]
    
    for fmt in date_formats:
        try:
            # For formats with day-month, validate the day is reasonable (1-31)
            if fmt in ['%d-%b', '%d-%B'] and date_str.split('-')[0].isdigit():
                day = int(date_str.split('-')[0])
                if day > 31 or day < 1:
                    continue
            
            parsed_date = datetime.strptime(date_str, fmt)
            
            # For formats without year, use current year
            if fmt in ['%d-%b', '%d-%B', '%b %d', '%B %d']:
                current_year = datetime.now().year
                parsed_date = parsed_date.replace(year=current_year)
            
            return parsed_date
            
        except (ValueError, IndexError):
            continue
    
    # Don't use pandas parser for strings that look like invalid dates
    # (e.g., '32-Jan' would be parsed as '2032-01-01' by pandas)
    if re.match(r'^\d+-[A-Za-z]+$', date_str):
        # Check if it's a day-month format with invalid day
        parts = date_str.split('-')
        if len(parts) == 2 and parts[0].isdigit():
            day = int(parts[0])
            if day > 31 or day < 1:
                logger.warning(f"Invalid day in date '{date_str}'")
                return None
    
    # If no format worked, try pandas parser as last resort
    try:
        # Use errors='coerce' to return NaT for invalid dates, then check if valid
        parsed = pd.to_datetime(date_str, errors='coerce')
        if pd.isna(parsed):
            logger.warning(f"Could not parse date '{date_str}'")
            return None
        return parsed.to_pydatetime()
    except Exception as e:
        logger.warning(f"Could not parse date '{date_str}': {e}")
        return None


def load_expense_history(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load and clean the expense history CSV file.
    
    Expected columns (with spaces):
    ['Name', 'Date of Purchase', 'Account', 'Merchant', ' Merchant Description ',
     ' Actual Amount ', ' Allowed Amount ', ' Description ', 'Category', 'Running Balance']
    
    Args:
        file_path: Path to the Consolidated_Expense_History CSV file
        
    Returns:
        Cleaned DataFrame with standardized column names and data types
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Expense history file not found: {file_path}")
    
    logger.info(f"Loading expense history from: {file_path}")
    
    # Load the CSV
    df = pd.read_csv(file_path)
    
    # Clean column names
    df = clean_column_names(df)
    
    # Validate required columns
    required_columns = ['name', 'date_of_purchase', 'actual_amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Clean and convert data
    # Convert currency columns to Decimal
    currency_columns = ['actual_amount', 'allowed_amount', 'running_balance']
    for col in currency_columns:
        if col in df.columns:
            df[col] = df[col].apply(clean_currency)
    
    # Parse dates
    if 'date_of_purchase' in df.columns:
        df['date_of_purchase'] = df['date_of_purchase'].apply(parse_flexible_date)
    
    # Validate names (should be Ryan or Jordyn)
    if 'name' in df.columns:
        df['name'] = df['name'].str.strip()
        valid_names = df['name'].isin(['Ryan', 'Jordyn'])
        invalid_count = (~valid_names).sum()
        if invalid_count > 0:
            logger.warning(f"Found {invalid_count} records with invalid names")
            logger.warning(f"Invalid names: {df[~valid_names]['name'].unique()}")
    
    # Sort by date
    df = df.sort_values('date_of_purchase', na_position='last')
    
    logger.info(f"Loaded {len(df)} expense records")
    
    return df


def load_rent_allocation(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load and clean the rent allocation CSV file.
    
    This file contains rent payment allocations by month.
    
    Args:
        file_path: Path to the Consolidated_Rent_Allocation CSV file
        
    Returns:
        Cleaned DataFrame with standardized column names and data types
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Rent allocation file not found: {file_path}")
    
    logger.info(f"Loading rent allocation from: {file_path}")
    
    # Load the CSV
    df = pd.read_csv(file_path)
    
    # Clean column names
    df = clean_column_names(df)
    
    # Identify and clean currency columns (any column with dollar amounts)
    for col in df.columns:
        # Check if column contains currency values
        sample_values = df[col].dropna().head(5).astype(str)
        if any('$' in str(val) or re.match(r'^-?\d+\.?\d*$', str(val)) for val in sample_values):
            df[col] = df[col].apply(clean_currency)
    
    # Parse any date columns
    date_columns = [col for col in df.columns if 'date' in col.lower() or 'month' in col.lower()]
    for col in date_columns:
        df[col] = df[col].apply(parse_flexible_date)
    
    logger.info(f"Loaded {len(df)} rent allocation records")
    
    return df


def load_zelle_payments(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load and clean the Zelle payments CSV file.
    
    IMPORTANT: All payments in this file are FROM Jordyn TO Ryan.
    
    Args:
        file_path: Path to the Zelle_From_Jordyn_Final CSV file
        
    Returns:
        Cleaned DataFrame with standardized column names and data types
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Zelle payments file not found: {file_path}")
    
    logger.info(f"Loading Zelle payments from: {file_path}")
    
    # Load the CSV
    df = pd.read_csv(file_path)
    
    # Clean column names
    df = clean_column_names(df)
    
    # Add explicit from/to columns since all payments are from Jordyn to Ryan
    df['from_person'] = 'Jordyn'
    df['to_person'] = 'Ryan'
    
    # Clean currency columns
    currency_columns = [col for col in df.columns if 'amount' in col.lower() or 'payment' in col.lower()]
    for col in currency_columns:
        df[col] = df[col].apply(clean_currency)
    
    # Parse date columns
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        df[col] = df[col].apply(parse_flexible_date)
    
    logger.info(f"Loaded {len(df)} Zelle payments (all from Jordyn to Ryan)")
    
    return df


def validate_data_quality(df: pd.DataFrame, dataset_name: str = "Unknown") -> Dict[str, Any]:
    """
    Validate data quality and return a summary of issues found.
    
    Checks for:
    - NaN values in critical columns
    - Invalid names (not Ryan/Jordyn)
    - Suspicious amounts (negative, zero, very large)
    - Missing dates
    
    Args:
        df: DataFrame to validate
        dataset_name: Name of the dataset for logging
        
    Returns:
        Dictionary with validation results and issues found
    """
    issues = {
        'total_records': len(df),
        'nan_counts': {},
        'invalid_names': [],
        'suspicious_amounts': [],
        'missing_dates': 0,
        'negative_amounts': [],
        'zero_amounts': [],
        'large_amounts': []  # Over $5000
    }
    
    # Check for NaN values in each column
    for col in df.columns:
        nan_count = df[col].isna().sum()
        if nan_count > 0:
            issues['nan_counts'][col] = nan_count
    
    # Check for invalid names
    if 'name' in df.columns:
        valid_names = ['Ryan', 'Jordyn']
        invalid_mask = ~df['name'].isin(valid_names)
        if invalid_mask.any():
            issues['invalid_names'] = df[invalid_mask]['name'].unique().tolist()
    
    # Check for suspicious amounts
    amount_columns = [col for col in df.columns if 'amount' in col.lower() and df[col].dtype == 'object']
    
    for col in amount_columns:
        # Skip if column has all NaN values
        if df[col].notna().sum() == 0:
            continue
            
        # Negative amounts
        negative_mask = df[col].notna() & (df[col] < 0)
        if negative_mask.any():
            issues['negative_amounts'].extend(
                df[negative_mask].index.tolist()
            )
        
        # Zero amounts
        zero_mask = df[col].notna() & (df[col] == 0)
        if zero_mask.any():
            issues['zero_amounts'].extend(
                df[zero_mask].index.tolist()
            )
        
        # Large amounts (over $5000)
        large_mask = df[col].notna() & (df[col] > 5000)
        if large_mask.any():
            issues['large_amounts'].extend(
                [(idx, float(df.loc[idx, col])) for idx in df[large_mask].index]
            )
    
    # Check for missing dates
    date_columns = [col for col in df.columns if 'date' in col.lower()]
    for col in date_columns:
        if col in df.columns:
            issues['missing_dates'] += df[col].isna().sum()
    
    # Log summary
    logger.info(f"\nData Quality Report for {dataset_name}:")
    logger.info(f"Total records: {issues['total_records']}")
    
    if issues['nan_counts']:
        logger.warning(f"Columns with NaN values: {issues['nan_counts']}")
    
    if issues['invalid_names']:
        logger.warning(f"Invalid names found: {issues['invalid_names']}")
    
    if issues['negative_amounts']:
        logger.warning(f"Found {len(issues['negative_amounts'])} negative amounts")
    
    if issues['zero_amounts']:
        logger.warning(f"Found {len(issues['zero_amounts'])} zero amounts")
    
    if issues['large_amounts']:
        logger.warning(f"Found {len(issues['large_amounts'])} amounts over $5000")
    
    if issues['missing_dates'] > 0:
        logger.warning(f"Missing dates: {issues['missing_dates']}")
    
    return issues


# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    print("Data Loader Module - Test Run")
    print("=" * 60)
    
    # Test clean_column_names
    test_df = pd.DataFrame({
        ' Actual Amount ': [100, 200],
        'Date of Purchase': ['9/14/2023', '10/1/2023'],
        'Name': ['Ryan', 'Jordyn']
    })
    
    print("\nTest 1: Clean Column Names")
    print("Original columns:", list(test_df.columns))
    cleaned_df = clean_column_names(test_df)
    print("Cleaned columns:", list(cleaned_df.columns))
    
    # Test clean_currency
    print("\nTest 2: Clean Currency Values")
    test_values = ['$84.39 ', '$(15.00)', '$ -', None, 123.45, '$1,234.56']
    for val in test_values:
        result = clean_currency(val)
        print(f"{val} -> {result}")
    
    # Test parse_flexible_date
    print("\nTest 3: Parse Flexible Dates")
    test_dates = ['9/14/2023', '24-Jan', '2023-09-14', None, 'invalid']
    for date in test_dates:
        result = parse_flexible_date(date)
        print(f"{date} -> {result}")
    
    print("\n" + "=" * 60)
    print("To use this module with actual data:")
    print("df = load_expense_history('data/raw/Consolidated_Expense_History_20250622.csv')")
    print("print(df.columns)  # Should show cleaned column names")
    print("print(df['actual_amount'].dtype)  # Should be object (Decimal values)")