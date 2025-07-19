"""
Zelle Payments CSV Loader

Loads and validates the Zelle_From_Jordyn_Final CSV file.
This file contains Zelle payments from Jordyn to Ryan for shared expenses.

Based on resolved business logic:
- Zelle payments are for expense reimbursements, NOT rent
- These represent Jordyn paying Ryan back for shared expenses
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class ZellePaymentsLoader:
    """Loads and validates Zelle payments CSV data."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the loader with optional data path."""
        if data_path is None:
            # Default to project data directory
            self.data_path = Path(__file__).parent.parent.parent / "data" / "raw"
        else:
            self.data_path = Path(data_path)
            
        self.csv_file = self.data_path / "Zelle_From_Jordyn_Final.csv"
        self._raw_data = None
        self._processed_data = None
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw CSV data without any processing."""
        try:
            logger.info(f"Loading Zelle payments from: {self.csv_file}")
            
            # Load with basic error handling
            self._raw_data = pd.read_csv(
                self.csv_file,
                encoding='utf-8',
                dtype=str  # Keep everything as strings initially
            )
            
            logger.info(f"Loaded {len(self._raw_data)} Zelle payment records")
            return self._raw_data.copy()
            
        except FileNotFoundError:
            logger.error(f"Zelle payments file not found: {self.csv_file}")
            raise
        except Exception as e:
            logger.error(f"Error loading Zelle payments: {e}")
            raise
    
    def get_column_info(self) -> Dict[str, Any]:
        """Get information about the CSV columns."""
        if self._raw_data is None:
            self.load_raw_data()
        
        info = {
            'columns': list(self._raw_data.columns),
            'row_count': len(self._raw_data),
            'column_count': len(self._raw_data.columns),
            'sample_data': {}
        }
        
        # Get sample data for each column (first non-empty value)
        for col in self._raw_data.columns:
            non_empty = self._raw_data[col].dropna()
            if len(non_empty) > 0:
                info['sample_data'][col] = str(non_empty.iloc[0])
            else:
                info['sample_data'][col] = None
        
        return info
    
    def validate_structure(self) -> Dict[str, Any]:
        """Validate the CSV structure against expected format."""
        if self._raw_data is None:
            self.load_raw_data()
        
        # Expected columns based on the CSV sample we saw
        expected_columns = [
            'Date', 'Merchant', 'Category', 'Account', 
            'Original Statement', 'Notes', 'Amount'
        ]
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'column_check': {},
            'data_quality': {},
            'business_logic_check': {}
        }
        
        # Check for expected columns
        actual_columns = list(self._raw_data.columns)
        for col in expected_columns:
            if col in actual_columns:
                validation_results['column_check'][col] = 'present'
            else:
                validation_results['column_check'][col] = 'missing'
                validation_results['issues'].append(f"Missing expected column: {col}")
        
        # Check for unexpected columns
        for col in actual_columns:
            if col not in expected_columns:
                validation_results['issues'].append(f"Unexpected column: {col}")
        
        # Basic data quality checks
        validation_results['data_quality']['total_rows'] = len(self._raw_data)
        validation_results['data_quality']['empty_rows'] = self._raw_data.isnull().all(axis=1).sum()
        
        # Check critical columns for emptiness
        critical_columns = ['Date', 'Amount']
        for col in critical_columns:
            if col in self._raw_data.columns:
                empty_count = self._raw_data[col].isnull().sum()
                validation_results['data_quality'][f'{col}_empty_count'] = empty_count
                if empty_count > 0:
                    validation_results['issues'].append(f"Column {col} has {empty_count} empty values")
        
        # Business logic validation - ensure all are Zelle transfers
        self._validate_zelle_logic(validation_results)
        
        return validation_results
    
    def _validate_zelle_logic(self, validation_results: Dict[str, Any]) -> None:
        """Validate that all entries are indeed Zelle transfers from Jordyn."""
        try:
            # Check Merchant column - should all be "Zelle"
            if 'Merchant' in self._raw_data.columns:
                non_zelle = self._raw_data[self._raw_data['Merchant'].str.lower() != 'zelle']
                if len(non_zelle) > 0:
                    validation_results['issues'].append(f"Found {len(non_zelle)} non-Zelle entries")
                    validation_results['business_logic_check']['non_zelle_entries'] = len(non_zelle)
            
            # Check Category column - should all be "Transfer"
            if 'Category' in self._raw_data.columns:
                non_transfer = self._raw_data[self._raw_data['Category'].str.lower() != 'transfer']
                if len(non_transfer) > 0:
                    validation_results['issues'].append(f"Found {len(non_transfer)} non-Transfer entries")
                    validation_results['business_logic_check']['non_transfer_entries'] = len(non_transfer)
            
            # Check Original Statement - should contain "JORDYN GINSBERG"
            if 'Original Statement' in self._raw_data.columns:
                non_jordyn = self._raw_data[
                    ~self._raw_data['Original Statement'].str.upper().str.contains('JORDYN', na=False)
                ]
                if len(non_jordyn) > 0:
                    validation_results['issues'].append(f"Found {len(non_jordyn)} entries not from Jordyn")
                    validation_results['business_logic_check']['non_jordyn_entries'] = len(non_jordyn)
            
            # Validate amounts are positive numbers
            if 'Amount' in self._raw_data.columns:
                invalid_amounts = []
                for idx, amount in enumerate(self._raw_data['Amount']):
                    try:
                        cleaned_amount = self._clean_currency(amount)
                        if cleaned_amount <= 0:
                            invalid_amounts.append(f"Row {idx}: {amount}")
                    except (ValueError, TypeError):
                        invalid_amounts.append(f"Row {idx}: {amount} (parse error)")
                
                if invalid_amounts:
                    validation_results['issues'].append(f"Found {len(invalid_amounts)} invalid amounts")
                    validation_results['business_logic_check']['invalid_amounts'] = invalid_amounts[:5]  # Show first 5
                    
        except Exception as e:
            validation_results['issues'].append(f"Error validating Zelle logic: {e}")
    
    def _clean_currency(self, value: str) -> float:
        """Convert currency string to float."""
        if pd.isna(value) or value == '':
            return 0.0
        
        # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[$,\s]', '', str(value))
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        return float(cleaned)
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if pd.isna(date_str) or date_str == '':
            return None
        
        # Try common date formats
        date_formats = ['%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y']
        
        for fmt in date_formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except ValueError:
                continue
        
        # If none work, try pandas
        try:
            return pd.to_datetime(date_str)
        except Exception:
            return None
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded Zelle payments data."""
        if self._raw_data is None:
            self.load_raw_data()
        
        summary = {
            'total_records': len(self._raw_data),
            'date_range': {},
            'payment_statistics': {},
            'monthly_breakdown': {}
        }
        
        # Analyze date range
        if 'Date' in self._raw_data.columns:
            dates = []
            for date_str in self._raw_data['Date'].dropna():
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    dates.append(parsed_date)
            
            if dates:
                summary['date_range'] = {
                    'earliest': min(dates).strftime('%Y-%m-%d'),
                    'latest': max(dates).strftime('%Y-%m-%d'),
                    'span_days': (max(dates) - min(dates)).days
                }
                
                # Monthly breakdown
                monthly_counts = {}
                monthly_totals = {}
                for i, date in enumerate(dates):
                    month_key = date.strftime('%Y-%m')
                    monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                    
                    # Get corresponding amount
                    try:
                        amount = self._clean_currency(self._raw_data.iloc[i]['Amount'])
                        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
                    except Exception:
                        pass
                
                summary['monthly_breakdown'] = {
                    'counts': monthly_counts,
                    'totals': monthly_totals
                }
        
        # Calculate payment statistics
        if 'Amount' in self._raw_data.columns:
            amounts = []
            for amount_str in self._raw_data['Amount'].dropna():
                try:
                    amount = self._clean_currency(amount_str)
                    if amount > 0:
                        amounts.append(amount)
                except Exception:
                    pass
            
            if amounts:
                summary['payment_statistics'] = {
                    'total_amount': sum(amounts),
                    'average_payment': sum(amounts) / len(amounts),
                    'min_payment': min(amounts),
                    'max_payment': max(amounts),
                    'payment_count': len(amounts)
                }
        
        return summary


def main():
    """Test the Zelle payments loader."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and test the loader
    loader = ZellePaymentsLoader()
    
    # Load and validate data
    print("Loading Zelle payments data...")
    loader.load_raw_data()
    
    print("\nColumn Information:")
    col_info = loader.get_column_info()
    for key, value in col_info.items():
        print(f"{key}: {value}")
    
    print("\nValidation Results:")
    validation = loader.validate_structure()
    for key, value in validation.items():
        print(f"{key}: {value}")
    
    print("\nData Summary:")
    summary = loader.get_data_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
