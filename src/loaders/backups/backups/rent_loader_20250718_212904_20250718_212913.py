"""
Rent Allocation CSV Loader

Loads and validates the Consolidated_Rent_Allocation CSV file.
This file contains monthly rent breakdowns and the 43%/57% split between Ryan and Jordyn.

Based on resolved business logic:
- Jordyn pays the full rent to the landlord
- Ryan owes ~47% back to Jordyn (shown as 43% in older data)
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import re

logger = logging.getLogger(__name__)


class RentAllocationLoader:
    """Loads and validates rent allocation CSV data."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the loader with optional data path."""
        if data_path is None:
            # Default to project data directory
            self.data_path = Path(__file__).parent.parent.parent / "data" / "raw"
        else:
            self.data_path = Path(data_path)
            
        self.csv_file = self.data_path / "Consolidated_Rent_Allocation_20250527.csv"
        self._raw_data = None
        self._processed_data = None
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw CSV data without any processing."""
        try:
            logger.info(f"Loading rent allocation from: {self.csv_file}")
            
            # Load with basic error handling
            self._raw_data = pd.read_csv(
                self.csv_file,
                encoding='utf-8',
                dtype=str  # Keep everything as strings initially
            )
            
            logger.info(f"Loaded {len(self._raw_data)} rent allocation records")
            return self._raw_data.copy()
            
        except FileNotFoundError:
            logger.error(f"Rent allocation file not found: {self.csv_file}")
            raise
        except Exception as e:
            logger.error(f"Error loading rent allocation: {e}")
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
            'Month', 'Tax Base Rent', 'Tax Garage', 'Tax Trash', 
            'Tax Courtesy', 'Conservice', 'Gross Total', 
            "Ryan's Rent (43%)", "Jordyn's Rent (57%)"
        ]
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'column_check': {},
            'data_quality': {},
            'business_logic_check': {}
        }
        
        # Check for expected columns (flexible matching for slight variations)
        actual_columns = list(self._raw_data.columns)
        for expected_col in expected_columns:
            found = False
            for actual_col in actual_columns:
                if expected_col.lower() in actual_col.lower():
                    validation_results['column_check'][expected_col] = f'found as: {actual_col}'
                    found = True
                    break
            if not found:
                validation_results['column_check'][expected_col] = 'missing'
                validation_results['issues'].append(f"Missing expected column: {expected_col}")
        
        # Basic data quality checks
        validation_results['data_quality']['total_rows'] = len(self._raw_data)
        validation_results['data_quality']['empty_rows'] = self._raw_data.isnull().all(axis=1).sum()
        
        # Business logic validation - check if Ryan's % + Jordyn's % = Gross Total
        self._validate_rent_split_logic(validation_results)
        
        return validation_results
    
    def _validate_rent_split_logic(self, validation_results: Dict[str, Any]) -> None:
        """Validate that Ryan's rent + Jordyn's rent = Gross Total."""
        try:
            # Find the relevant columns (handling variations in column names)
            gross_total_col = None
            ryan_rent_col = None
            jordyn_rent_col = None
            
            for col in self._raw_data.columns:
                if 'gross total' in col.lower():
                    gross_total_col = col
                elif 'ryan' in col.lower() and 'rent' in col.lower():
                    ryan_rent_col = col
                elif 'jordyn' in col.lower() and 'rent' in col.lower():
                    jordyn_rent_col = col
            
            if all([gross_total_col, ryan_rent_col, jordyn_rent_col]):
                # Clean and convert currency values
                for idx, row in self._raw_data.iterrows():
                    try:
                        gross_total = self._clean_currency(row[gross_total_col])
                        ryan_rent = self._clean_currency(row[ryan_rent_col])
                        jordyn_rent = self._clean_currency(row[jordyn_rent_col])
                        
                        calculated_total = ryan_rent + jordyn_rent
                        difference = abs(gross_total - calculated_total)
                        
                        # Allow for small rounding differences
                        if difference > 0.02:
                            month = row.get('Month', f'Row {idx}')
                            validation_results['business_logic_check'][f'split_error_{month}'] = {
                                'gross_total': gross_total,
                                'ryan_rent': ryan_rent,
                                'jordyn_rent': jordyn_rent,
                                'calculated_total': calculated_total,
                                'difference': difference
                            }
                            validation_results['issues'].append(
                                f"Rent split doesn't add up for {month}: "
                                f"${gross_total:.2f} != ${ryan_rent:.2f} + ${jordyn_rent:.2f}"
                            )
                    except (ValueError, TypeError) as e:
                        validation_results['issues'].append(f"Error parsing rent amounts in row {idx}: {e}")
            else:
                validation_results['issues'].append("Cannot find all required rent columns for validation")
                
        except Exception as e:
            validation_results['issues'].append(f"Error validating rent split logic: {e}")
    
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
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded rent allocation data."""
        if self._raw_data is None:
            self.load_raw_data()
        
        summary = {
            'total_records': len(self._raw_data),
            'months_covered': [],
            'rent_statistics': {}
        }
        
        # Analyze months covered
        if 'Month' in self._raw_data.columns:
            summary['months_covered'] = self._raw_data['Month'].dropna().tolist()
        
        # Calculate rent statistics
        try:
            gross_total_col = None
            ryan_rent_col = None
            jordyn_rent_col = None
            
            for col in self._raw_data.columns:
                if 'gross total' in col.lower():
                    gross_total_col = col
                elif 'ryan' in col.lower() and 'rent' in col.lower():
                    ryan_rent_col = col
                elif 'jordyn' in col.lower() and 'rent' in col.lower():
                    jordyn_rent_col = col
            
            if all([gross_total_col, ryan_rent_col, jordyn_rent_col]):
                gross_totals = [self._clean_currency(val) for val in self._raw_data[gross_total_col]]
                ryan_rents = [self._clean_currency(val) for val in self._raw_data[ryan_rent_col]]
                jordyn_rents = [self._clean_currency(val) for val in self._raw_data[jordyn_rent_col]]
                
                valid_gross = [x for x in gross_totals if x > 0]
                valid_ryan = [x for x in ryan_rents if x > 0]
                valid_jordyn = [x for x in jordyn_rents if x > 0]
                
                if valid_gross:
                    summary['rent_statistics'] = {
                        'avg_gross_rent': sum(valid_gross) / len(valid_gross),
                        'min_gross_rent': min(valid_gross),
                        'max_gross_rent': max(valid_gross),
                        'avg_ryan_share': sum(valid_ryan) / len(valid_ryan) if valid_ryan else 0,
                        'avg_jordyn_share': sum(valid_jordyn) / len(valid_jordyn) if valid_jordyn else 0,
                        'ryan_percentage': (sum(valid_ryan) / sum(valid_gross) * 100) if valid_gross else 0,
                        'jordyn_percentage': (sum(valid_jordyn) / sum(valid_gross) * 100) if valid_gross else 0
                    }
                
        except Exception as e:
            summary['rent_statistics']['error'] = f"Error calculating statistics: {e}"
        
        return summary


def main():
    """Test the rent allocation loader."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and test the loader
    loader = RentAllocationLoader()
    
    # Load and validate data
    print("Loading rent allocation data...")
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
