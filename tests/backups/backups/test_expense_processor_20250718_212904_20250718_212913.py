"""
Unit tests for the expense processor

Tests the ExpenseProcessor class to ensure data processing works correctly.
"""

import sys
from pathlib import Path
import pandas as pd
import unittest
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processors.expense_processor import ExpenseProcessor


class TestExpenseProcessor(unittest.TestCase):
    """Test cases for ExpenseProcessor."""
    
    def setUp(self):
        """Set up test data."""
        self.processor = ExpenseProcessor()
        
        # Create sample test data that matches the real CSV structure
        self.sample_data = pd.DataFrame({
            'Name': ['Ryan', 'Jordyn', 'Ryan', None, 'Jordyn '],
            'Date of Purchase': ['9/14/2023', '10/15/2023', '11/16/2023', '12/17/2023', ''],
            'Account': ['Mercury', 'Wells Fargo', 'Mercury', 'Cash', 'Mercury'],
            'Merchant': ['Amazon', "Fry's", 'Target', 'Gas Station', 'Whole Foods'],
            ' Merchant Description ': [' Online shopping ', ' Groceries ', ' Household ', '', ' Organic food '],
            ' Actual Amount ': ['$84.39 ', '$123.45', '$45.67', '', '$234.56'],
            ' Allowed Amount ': ['$84.39 ', '$100.00', '$45.67', '$0.00', ''],
            ' Description ': [' Looking into overcharge possibility ', ' Weekly groceries ', '', ' Gas fill up ', ' Healthy eating '],
            'Category': ['Shopping', 'Groceries', 'Household', '', 'Groceries'],
            'Running Balance': ['$1000.00', '$876.55', '$830.88', '$830.88', '$596.32']
        })
    
    def test_column_name_cleaning(self):
        """Test that column names are properly cleaned."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that spaces are removed from column names
        self.assertIn('actual_amount', processed.columns)
        self.assertIn('allowed_amount', processed.columns)
        self.assertIn('merchant_description', processed.columns)
        self.assertIn('person', processed.columns)
        
        # Check that old column names are gone
        self.assertNotIn(' Actual Amount ', processed.columns)
        self.assertNotIn(' Allowed Amount ', processed.columns)
    
    def test_currency_cleaning(self):
        """Test that currency values are properly cleaned."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that currency values are converted to floats
        self.assertAlmostEqual(processed.iloc[0]['actual_amount'], 84.39)
        self.assertAlmostEqual(processed.iloc[1]['actual_amount'], 123.45)
        
        # Check that empty values become None
        self.assertIsNone(processed.iloc[3]['actual_amount'])
    
    def test_date_parsing(self):
        """Test that dates are properly parsed."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that valid dates are parsed
        self.assertIsInstance(processed.iloc[0]['date'], datetime)
        self.assertEqual(processed.iloc[0]['date'].year, 2023)
        self.assertEqual(processed.iloc[0]['date'].month, 9)
        self.assertEqual(processed.iloc[0]['date'].day, 14)
        
        # Check that invalid dates become None
        self.assertIsNone(processed.iloc[4]['date'])
    
    def test_person_normalization(self):
        """Test that person names are normalized."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that 'Jordyn ' becomes 'Jordyn'
        jordyn_records = processed[processed['person_normalized'] == 'Jordyn']
        self.assertEqual(len(jordyn_records), 2)  # Both 'Jordyn' and 'Jordyn ' should be normalized
    
    def test_validation_flags(self):
        """Test that validation flags are properly set."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that records with missing critical data are flagged as invalid
        invalid_records = processed[~processed['is_valid']]
        self.assertTrue(len(invalid_records) > 0)
        
        # Check that the record with missing name is invalid
        missing_name_record = processed[processed['person'].isna()]
        self.assertFalse(missing_name_record.iloc[0]['is_valid'])
    
    def test_calculated_fields(self):
        """Test that calculated fields are added correctly."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that year/month fields are added
        self.assertIn('year', processed.columns)
        self.assertIn('month', processed.columns)
        self.assertIn('year_month', processed.columns)
        
        # Check that expense type classification works
        self.assertIn('expense_type', processed.columns)
        
        # Amazon should be classified as Online Shopping
        amazon_record = processed[processed['merchant'] == 'Amazon']
        self.assertEqual(amazon_record.iloc[0]['expense_type'], 'Online Shopping')
        
        # Fry's should be classified as Groceries
        frys_record = processed[processed['merchant'] == "Fry's"]
        self.assertEqual(frys_record.iloc[0]['expense_type'], 'Groceries')
    
    def test_amount_difference_calculation(self):
        """Test that amount differences are calculated correctly."""
        processed = self.processor.load_and_process(self.sample_data)
        
        # Check that amount difference is calculated
        self.assertIn('amount_difference', processed.columns)
        self.assertIn('has_amount_difference', processed.columns)
        
        # Record 1 has $123.45 actual vs $100.00 allowed = $23.45 difference
        record_1 = processed.iloc[1]
        self.assertAlmostEqual(record_1['amount_difference'], 23.45)
        self.assertTrue(record_1['has_amount_difference'])
        
        # Record 0 has same actual and allowed, so no difference
        record_0 = processed.iloc[0]
        self.assertAlmostEqual(record_0['amount_difference'], 0.0)
        self.assertFalse(record_0['has_amount_difference'])
    
    def test_processing_summary(self):
        """Test that processing summary provides correct statistics."""
        self.processor.load_and_process(self.sample_data)
        summary = self.processor.get_processing_summary()
        
        # Check basic counts
        self.assertEqual(summary['total_records'], 5)
        self.assertIn('valid_records', summary)
        self.assertIn('invalid_records', summary)
        
        # Check that person breakdown exists
        self.assertIn('records_by_person', summary)
        self.assertIn('records_by_type', summary)
        
        # Check amount statistics
        self.assertIn('amount_statistics', summary)
        amount_stats = summary['amount_statistics']
        self.assertIn('total_amount', amount_stats)
        self.assertIn('average_amount', amount_stats)


def main():
    """Run the unit tests."""
    print("Running ExpenseProcessor unit tests...")
    unittest.main(verbosity=2)


if __name__ == "__main__":
    main()
