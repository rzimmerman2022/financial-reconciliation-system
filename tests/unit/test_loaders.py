#!/usr/bin/env python3
"""
Unit tests for financial reconciliation system loaders
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import pandas as pd

from src.loaders.expense_loader import ExpenseHistoryLoader
from src.loaders.rent_loader import RentAllocationLoader  
from src.loaders.zelle_loader import ZellePaymentsLoader


class TestExpenseHistoryLoader:
    """Test cases for ExpenseHistoryLoader"""
    
    def test_loader_initialization(self):
        """Test that expense loader can be initialized"""
        loader = ExpenseHistoryLoader()
        assert loader is not None
        assert hasattr(loader, 'load_raw_data')
    
    @patch('src.loaders.expense_loader.Path')
    def test_load_raw_data_with_file(self, mock_path):
        """Test loading expense data when file exists"""
        # Setup mock file path
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path.return_value = mock_file
        
        # Mock pandas read_csv
        with patch('pandas.read_csv') as mock_read_csv:
            test_data = pd.DataFrame({
                'date': ['2025-01-01', '2025-01-02'],
                'amount': [100.00, 200.00],
                'description': ['Test expense 1', 'Test expense 2']
            })
            mock_read_csv.return_value = test_data
            
            loader = ExpenseHistoryLoader()
            result = loader.load_raw_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
    
    def test_load_raw_data_empty(self):
        """Test loading expense data raises exception when file doesn't exist"""
        with patch('pandas.read_csv') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            loader = ExpenseHistoryLoader()
            with pytest.raises(FileNotFoundError):
                loader.load_raw_data()


class TestRentAllocationLoader:
    """Test cases for RentAllocationLoader"""
    
    def test_loader_initialization(self):
        """Test that rent loader can be initialized"""
        loader = RentAllocationLoader()
        assert loader is not None
        assert hasattr(loader, 'load_raw_data')
    
    @patch('src.loaders.rent_loader.Path')
    def test_load_raw_data_with_file(self, mock_path):
        """Test loading rent data when file exists"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path.return_value = mock_file
        
        with patch('pandas.read_csv') as mock_read_csv:
            test_data = pd.DataFrame({
                'date': ['2025-01-01'],
                'amount': [2400.00],
                'payer': ['Ryan']
            })
            mock_read_csv.return_value = test_data
            
            loader = RentAllocationLoader()
            result = loader.load_raw_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 1
    
    def test_load_raw_data_empty(self):
        """Test loading rent data raises exception when file doesn't exist"""
        with patch('pandas.read_csv') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            loader = RentAllocationLoader()
            with pytest.raises(FileNotFoundError):
                loader.load_raw_data()


class TestZellePaymentsLoader:
    """Test cases for ZellePaymentsLoader"""
    
    def test_loader_initialization(self):
        """Test that Zelle loader can be initialized"""
        loader = ZellePaymentsLoader()
        assert loader is not None
        assert hasattr(loader, 'load_raw_data')
    
    @patch('src.loaders.zelle_loader.Path')
    def test_load_raw_data_with_file(self, mock_path):
        """Test loading Zelle data when file exists"""
        mock_file = MagicMock()
        mock_file.exists.return_value = True
        mock_path.return_value = mock_file
        
        with patch('pandas.read_csv') as mock_read_csv:
            test_data = pd.DataFrame({
                'date': ['2025-01-01', '2025-01-02'],
                'amount': [50.00, 75.00],
                'from': ['Jordyn', 'Ryan'],
                'to': ['Ryan', 'Jordyn']
            })
            mock_read_csv.return_value = test_data
            
            loader = ZellePaymentsLoader()
            result = loader.load_raw_data()
            
            assert isinstance(result, pd.DataFrame)
            assert len(result) == 2
    
    def test_load_raw_data_empty(self):
        """Test loading Zelle data raises exception when file doesn't exist"""
        with patch('pandas.read_csv') as mock_read:
            mock_read.side_effect = FileNotFoundError("File not found")
            
            loader = ZellePaymentsLoader()
            with pytest.raises(FileNotFoundError):
                loader.load_raw_data()


class TestAllLoadersIntegration:
    """Integration tests for all loaders working together"""
    
    def test_all_loaders_can_initialize(self):
        """Test that all loaders can be initialized without errors"""
        expense_loader = ExpenseHistoryLoader()
        rent_loader = RentAllocationLoader()
        zelle_loader = ZellePaymentsLoader()
        
        assert expense_loader is not None
        assert rent_loader is not None
        assert zelle_loader is not None
    
    @patch('pandas.read_csv')
    @patch('src.loaders.expense_loader.Path')
    @patch('src.loaders.rent_loader.Path')
    @patch('src.loaders.zelle_loader.Path')
    def test_total_records_loaded(self, mock_zelle_path, mock_rent_path, 
                                  mock_expense_path, mock_read_csv):
        """Test counting total records from all loaders"""
        # Setup mocks to return existing files
        for mock_path in [mock_expense_path, mock_rent_path, mock_zelle_path]:
            mock_file = MagicMock()
            mock_file.exists.return_value = True
            mock_path.return_value = mock_file
        
        # Mock different dataframes for each loader
        mock_read_csv.side_effect = [
            pd.DataFrame({'data': range(5)}),   # 5 expense records
            pd.DataFrame({'data': range(3)}),   # 3 rent records
            pd.DataFrame({'data': range(7)}),   # 7 zelle records
        ]
        
        expense_loader = ExpenseHistoryLoader()
        expense_data = expense_loader.load_raw_data()
        
        rent_loader = RentAllocationLoader()
        rent_data = rent_loader.load_raw_data()
        
        zelle_loader = ZellePaymentsLoader()
        zelle_data = zelle_loader.load_raw_data()
        
        total_records = len(expense_data) + len(rent_data) + len(zelle_data)
        assert total_records == 15  # 5 + 3 + 7