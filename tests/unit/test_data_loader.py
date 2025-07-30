"""
Comprehensive Unit Tests for Data Loader Module

Tests all functions in data_loader.py with various edge cases and real-world scenarios.
"""

import unittest
import pandas as pd
import numpy as np
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import tempfile
import os

# Import the module to test
from data_loader import (
    clean_column_names,
    clean_currency,
    parse_flexible_date,
    load_expense_history,
    load_rent_allocation,
    load_zelle_payments,
    validate_data_quality
)


class TestCleanColumnNames(unittest.TestCase):
    """Test the clean_column_names function."""
    
    def test_basic_cleaning(self):
        """Test basic column name cleaning."""
        df = pd.DataFrame({
            'Name': [1, 2],
            ' Actual Amount ': [3, 4],
            'Date of Purchase': [5, 6]
        })
        
        cleaned = clean_column_names(df)
        
        self.assertEqual(list(cleaned.columns), ['name', 'actual_amount', 'date_of_purchase'])
    
    def test_multiple_spaces(self):
        """Test handling of multiple spaces."""
        df = pd.DataFrame({
            '  Multiple   Spaces  ': [1, 2],
            'CamelCase': [3, 4]
        })
        
        cleaned = clean_column_names(df)
        
        self.assertEqual(list(cleaned.columns), ['multiple_spaces', 'camelcase'])
    
    def test_special_characters(self):
        """Test that special characters are preserved (not replaced)."""
        df = pd.DataFrame({
            'Column-With-Dashes': [1, 2],
            'Column.With.Dots': [3, 4]
        })
        
        cleaned = clean_column_names(df)
        
        # Only spaces are replaced with underscores
        self.assertEqual(list(cleaned.columns), ['column-with-dashes', 'column.with.dots'])
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        cleaned = clean_column_names(df)
        self.assertEqual(len(cleaned.columns), 0)


class TestCleanCurrency(unittest.TestCase):
    """Test the clean_currency function."""
    
    def test_standard_currency(self):
        """Test standard currency formats."""
        self.assertEqual(clean_currency('$84.39'), Decimal('84.39'))
        self.assertEqual(clean_currency('$84.39 '), Decimal('84.39'))
        self.assertEqual(clean_currency(' $84.39 '), Decimal('84.39'))
    
    def test_negative_values(self):
        """Test negative value formats."""
        self.assertEqual(clean_currency('$(15.00)'), Decimal('-15.00'))
        self.assertEqual(clean_currency('-$15.00'), Decimal('-15.00'))
        self.assertEqual(clean_currency('$-15.00'), Decimal('-15.00'))
    
    def test_large_numbers(self):
        """Test numbers with commas."""
        self.assertEqual(clean_currency('$1,234.56'), Decimal('1234.56'))
        self.assertEqual(clean_currency('$1,234,567.89'), Decimal('1234567.89'))
    
    def test_invalid_values(self):
        """Test invalid and edge cases."""
        self.assertIsNone(clean_currency('$ -'))
        self.assertIsNone(clean_currency('$-'))
        self.assertIsNone(clean_currency('-'))
        self.assertIsNone(clean_currency(''))
        self.assertIsNone(clean_currency(None))
        self.assertIsNone(clean_currency(np.nan))
    
    def test_numeric_input(self):
        """Test already numeric inputs."""
        self.assertEqual(clean_currency(123.45), Decimal('123.45'))
        self.assertEqual(clean_currency(123), Decimal('123'))
        self.assertEqual(clean_currency(-50.00), Decimal('-50.00'))
    
    def test_zero_values(self):
        """Test zero values."""
        self.assertEqual(clean_currency('$0.00'), Decimal('0.00'))
        self.assertEqual(clean_currency('$0'), Decimal('0'))
        self.assertEqual(clean_currency(0), Decimal('0'))


class TestParseFlexibleDate(unittest.TestCase):
    """Test the parse_flexible_date function."""
    
    def test_standard_formats(self):
        """Test standard date formats."""
        # M/D/YYYY format
        result = parse_flexible_date('9/14/2023')
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 9)
        self.assertEqual(result.day, 14)
        
        # YYYY-MM-DD format
        result = parse_flexible_date('2023-09-14')
        self.assertEqual(result.year, 2023)
        self.assertEqual(result.month, 9)
        self.assertEqual(result.day, 14)
    
    def test_month_day_formats(self):
        """Test formats without year (should use current year)."""
        current_year = datetime.now().year
        
        # D-Mon format
        result = parse_flexible_date('24-Jan')
        self.assertEqual(result.year, current_year)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 24)
        
        # Mon D format
        result = parse_flexible_date('Jan 24')
        self.assertEqual(result.year, current_year)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 24)
    
    def test_datetime_input(self):
        """Test with datetime/Timestamp input."""
        dt = datetime(2023, 9, 14, 10, 30, 0)
        result = parse_flexible_date(dt)
        self.assertEqual(result, dt)
        
        # Test with pandas Timestamp
        ts = pd.Timestamp('2023-09-14')
        result = parse_flexible_date(ts)
        self.assertEqual(result.date(), ts.date())
    
    def test_invalid_dates(self):
        """Test invalid date inputs."""
        self.assertIsNone(parse_flexible_date(None))
        self.assertIsNone(parse_flexible_date(''))
        self.assertIsNone(parse_flexible_date('invalid'))
        self.assertIsNone(parse_flexible_date('32-Jan'))  # Invalid day
        self.assertIsNone(parse_flexible_date(np.nan))


class TestLoadExpenseHistory(unittest.TestCase):
    """Test the load_expense_history function."""
    
    def setUp(self):
        """Create a temporary CSV file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_expense.csv')
        
        # Create test data with actual column names (including spaces)
        data = {
            'Name': ['Ryan', 'Jordyn', 'Ryan'],
            'Date of Purchase': ['9/14/2023', '9/15/2023', '9/16/2023'],
            'Account': ['Chase', 'BofA', 'Chase'],
            'Merchant': ['Target', 'Walmart', 'Amazon'],
            ' Merchant Description ': ['Groceries', 'Household', 'Electronics'],
            ' Actual Amount ': ['$84.39', '$(15.00)', '$123.45'],
            ' Allowed Amount ': ['$80.00', '$15.00', '$120.00'],
            ' Description ': ['Weekly shopping', '100% Jordyn', 'Gift'],
            'Category': ['Groceries', 'Personal', 'Gift'],
            'Running Balance': ['$1000.00', '$985.00', '$861.55']
        }
        
        pd.DataFrame(data).to_csv(self.test_file, index=False)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_basic(self):
        """Test basic loading functionality."""
        df = load_expense_history(self.test_file)
        
        # Check columns are cleaned
        expected_columns = [
            'name', 'date_of_purchase', 'account', 'merchant',
            'merchant_description', 'actual_amount', 'allowed_amount',
            'description', 'category', 'running_balance'
        ]
        self.assertEqual(list(df.columns), expected_columns)
        
        # Check data types
        self.assertEqual(len(df), 3)
        self.assertIsInstance(df['actual_amount'].iloc[0], Decimal)
        self.assertIsInstance(df['date_of_purchase'].iloc[0], datetime)
    
    def test_currency_conversion(self):
        """Test that currency values are properly converted."""
        df = load_expense_history(self.test_file)
        
        self.assertEqual(df['actual_amount'].iloc[0], Decimal('84.39'))
        self.assertEqual(df['actual_amount'].iloc[1], Decimal('-15.00'))  # Negative
        self.assertEqual(df['actual_amount'].iloc[2], Decimal('123.45'))
    
    def test_name_validation(self):
        """Test name validation warnings."""
        # Create file with invalid name
        data = {
            'Name': ['Ryan', 'InvalidName', 'Jordyn'],
            'Date of Purchase': ['9/14/2023', '9/15/2023', '9/16/2023'],
            ' Actual Amount ': ['$10', '$20', '$30']
        }
        
        test_file = os.path.join(self.temp_dir, 'test_invalid_names.csv')
        pd.DataFrame(data).to_csv(test_file, index=False)
        
        # Should load but log warning
        df = load_expense_history(test_file)
        self.assertEqual(len(df), 3)
    
    def test_file_not_found(self):
        """Test error handling for missing file."""
        with self.assertRaises(FileNotFoundError):
            load_expense_history('nonexistent_file.csv')


class TestLoadRentAllocation(unittest.TestCase):
    """Test the load_rent_allocation function."""
    
    def setUp(self):
        """Create a temporary CSV file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_rent.csv')
        
        # Create test data
        data = {
            'Month': ['Jan-24', 'Feb-24', 'Mar-24'],
            'Total Rent': ['$2000.00', '$2000.00', '$2000.00'],
            'Ryan Share': ['$1000.00', '$1000.00', '$1000.00'],
            'Jordyn Share': ['$1000.00', '$1000.00', '$1000.00']
        }
        
        pd.DataFrame(data).to_csv(self.test_file, index=False)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_rent_basic(self):
        """Test basic rent loading functionality."""
        df = load_rent_allocation(self.test_file)
        
        # Check columns are cleaned
        self.assertIn('month', df.columns)
        self.assertIn('total_rent', df.columns)
        
        # Check currency conversion
        self.assertEqual(df['total_rent'].iloc[0], Decimal('2000.00'))
        self.assertEqual(df['ryan_share'].iloc[0], Decimal('1000.00'))


class TestLoadZellePayments(unittest.TestCase):
    """Test the load_zelle_payments function."""
    
    def setUp(self):
        """Create a temporary CSV file for testing."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, 'test_zelle.csv')
        
        # Create test data
        data = {
            'Date': ['9/14/2023', '10/1/2023'],
            'Amount': ['$500.00', '$750.00'],
            'Description': ['Rent payment', 'Expense reimbursement']
        }
        
        pd.DataFrame(data).to_csv(self.test_file, index=False)
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_zelle_basic(self):
        """Test basic Zelle loading functionality."""
        df = load_zelle_payments(self.test_file)
        
        # Check that from/to columns are added
        self.assertEqual(df['from_person'].iloc[0], 'Jordyn')
        self.assertEqual(df['to_person'].iloc[0], 'Ryan')
        
        # Check all records have the same from/to
        self.assertTrue((df['from_person'] == 'Jordyn').all())
        self.assertTrue((df['to_person'] == 'Ryan').all())
        
        # Check currency conversion
        self.assertEqual(df['amount'].iloc[0], Decimal('500.00'))


class TestValidateDataQuality(unittest.TestCase):
    """Test the validate_data_quality function."""
    
    def test_validation_with_issues(self):
        """Test validation with various data quality issues."""
        # Create test data with various issues
        df = pd.DataFrame({
            'name': ['Ryan', 'InvalidName', 'Jordyn', None],
            'amount': [Decimal('100'), Decimal('-50'), Decimal('0'), Decimal('6000')],
            'date': ['2023-09-14', None, '2023-09-16', '2023-09-17']
        })
        
        issues = validate_data_quality(df, 'Test Dataset')
        
        # Check detected issues
        self.assertEqual(issues['total_records'], 4)
        self.assertIn('InvalidName', issues['invalid_names'])
        self.assertIn(1, issues['negative_amounts'])  # Row index 1
        self.assertIn(2, issues['zero_amounts'])  # Row index 2
        self.assertEqual(len(issues['large_amounts']), 1)  # One amount over $5000
        self.assertEqual(issues['missing_dates'], 1)
    
    def test_validation_clean_data(self):
        """Test validation with clean data."""
        df = pd.DataFrame({
            'name': ['Ryan', 'Jordyn', 'Ryan'],
            'amount': [Decimal('100'), Decimal('200'), Decimal('300')],
            'date': pd.to_datetime(['2023-09-14', '2023-09-15', '2023-09-16'])
        })
        
        issues = validate_data_quality(df, 'Clean Dataset')
        
        # Should have no major issues
        self.assertEqual(issues['total_records'], 3)
        self.assertEqual(len(issues['invalid_names']), 0)
        self.assertEqual(len(issues['negative_amounts']), 0)
        self.assertEqual(len(issues['zero_amounts']), 0)
        self.assertEqual(len(issues['large_amounts']), 0)
        self.assertEqual(issues['missing_dates'], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)