"""
Expense History CSV Loader

Loads and validates the Consolidated_Expense_History CSV file.
This is the primary data source for shared expenses between Ryan and Jordyn.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ExpenseHistoryLoader:
    """Loads and validates expense history CSV data."""
    
    def __init__(self, data_path: Optional[Path] = None):
        """Initialize the loader with optional data path."""
        if data_path is None:
            # Default to project data directory
            self.data_path = Path(__file__).parent.parent.parent / "data" / "raw"
        else:
            self.data_path = Path(data_path)
            
        self.csv_file = self.data_path / "Consolidated_Expense_History_20250622.csv"
        self._raw_data = None
        self._processed_data = None
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw CSV data without any processing."""
        try:
            logger.info(f"Loading expense history from: {self.csv_file}")
            
            # Load with basic error handling
            self._raw_data = pd.read_csv(
                self.csv_file,
                encoding='utf-8',
                dtype=str  # Keep everything as strings initially
            )
            
            logger.info(f"Loaded {len(self._raw_data)} expense records")
            return self._raw_data.copy()
            
        except FileNotFoundError:
            logger.error(f"Expense history file not found: {self.csv_file}")
            raise
        except Exception as e:
            logger.error(f"Error loading expense history: {e}")
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
        
        expected_columns = [
            'Name', 'Date of Purchase', 'Account', 'Merchant', 
            'Merchant Description', 'Actual Amount', 'Allowed Amount',
            'Description', 'Category', 'Running Balance'
        ]
        
        validation_results = {
            'is_valid': True,
            'issues': [],
            'column_check': {},
            'data_quality': {}
        }
        
        # Check for expected columns
        actual_columns = list(self._raw_data.columns)
        for col in expected_columns:
            if col in actual_columns:
                validation_results['column_check'][col] = 'present'
            else:
                validation_results['column_check'][col] = 'missing'
                validation_results['issues'].append(f"Missing expected column: {col}")
                validation_results['is_valid'] = False
        
        # Check for unexpected columns
        for col in actual_columns:
            if col not in expected_columns:
                validation_results['issues'].append(f"Unexpected column: {col}")
        
        # Basic data quality checks
        validation_results['data_quality']['total_rows'] = len(self._raw_data)
        validation_results['data_quality']['empty_rows'] = self._raw_data.isnull().all(axis=1).sum()
        
        # Check critical columns for emptiness
        critical_columns = ['Name', 'Date of Purchase', 'Actual Amount']
        for col in critical_columns:
            if col in self._raw_data.columns:
                empty_count = self._raw_data[col].isnull().sum()
                validation_results['data_quality'][f'{col}_empty_count'] = empty_count
                if empty_count > 0:
                    validation_results['issues'].append(f"Column {col} has {empty_count} empty values")
        
        return validation_results
    
    def get_data_summary(self) -> Dict[str, Any]:
        """Get a summary of the loaded data."""
        if self._raw_data is None:
            self.load_raw_data()
        
        summary = {
            'total_records': len(self._raw_data),
            'date_range': {},
            'people': {},
            'accounts': {},
            'merchants': {}
        }
        
        # Analyze by person
        if 'Name' in self._raw_data.columns:
            summary['people'] = self._raw_data['Name'].value_counts().to_dict()
        
        # Analyze accounts
        if 'Account' in self._raw_data.columns:
            summary['accounts'] = self._raw_data['Account'].value_counts().to_dict()
        
        # Top merchants
        if 'Merchant' in self._raw_data.columns:
            summary['merchants'] = self._raw_data['Merchant'].value_counts().head(10).to_dict()
        
        return summary


def main():
    """Test the expense loader."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create and test the loader
    loader = ExpenseHistoryLoader()
    
    # Load and validate data
    print("Loading expense history data...")
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
