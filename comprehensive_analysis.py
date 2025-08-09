#!/usr/bin/env python3
"""
Comprehensive Financial Analysis with Fixed Date Parsing
========================================================

Complete analysis of all transactions with proper date handling,
monthly summaries, and balance calculations.

This module provides:
- Complete transaction loading from all data sources (legacy + bank exports)
- Enhanced date parsing supporting multiple formats (YY-Mon, Mon-YY, ISO, US, etc.)
- Monthly summary generation with running balance calculations
- Expense categorization and settlement tracking
- JSON export for programmatic access to financial data

Author: Claude (Anthropic)
Date: August 9, 2025
Version: 1.0.0
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import warnings
import json
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

class ComprehensiveAnalyzer:
    """Complete financial analyzer with fixed date parsing."""
    
    def __init__(self):
        self.all_transactions = []
        self.monthly_summary = {}
        self.running_balance = Decimal('0')
        
    def parse_date(self, date_str):
        """
        Enhanced date parser that correctly handles all formats.
        
        Supports:
        - YY-Mon format (e.g., "24-Jan" for January 2024)
        - Mon-YY format (e.g., "Jan-24" for January 2024)
        - ISO format (YYYY-MM-DD)
        - US format (MM/DD/YYYY or MM/DD/YY)
        - European format (DD/MM/YYYY)
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            datetime object or None if parsing fails
        """
        if pd.isna(date_str):
            return None
            
        date_str = str(date_str).strip()
        
        # Handle YY-Mon format (e.g., "24-Jan") - Common in rent data
        if '-' in date_str and len(date_str) <= 7:
            try:
                parts = date_str.split('-')
                if len(parts) == 2:
                    months_abbr = {
                        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 
                        'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                        'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                    }
                    
                    # Check if first part is year (YY-Mon)
                    if parts[0].isdigit():
                        year = int(parts[0])
                        if year < 100:  # Two-digit year
                            year = 2000 + year
                        month_str = parts[1].lower()[:3]
                        if month_str in months_abbr:
                            return datetime(year, months_abbr[month_str], 1)
                    
                    # Check if second part is year (Mon-YY)
                    elif parts[1].isdigit():
                        year = int(parts[1])
                        if year < 100:  # Two-digit year
                            year = 2000 + year
                        month_str = parts[0].lower()[:3]
                        if month_str in months_abbr:
                            return datetime(year, months_abbr[month_str], 1)
            except:
                pass
        
        # Standard date formats
        date_formats = [
            '%Y-%m-%d', '%m/%d/%Y', '%m/%d/%y',
            '%Y/%m/%d', '%d/%m/%Y', '%d/%m/%y',
            '%b %d, %Y', '%B %d, %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
                
        return None
    
    def parse_amount(self, amount_str):
        """Parse amount from various formats."""
        if pd.isna(amount_str):
            return Decimal('0')
            
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols, commas, and spaces
        amount_str = amount_str.replace('$', '').replace(',', '').replace(' ', '').strip()
        
        # Handle parentheses for negative numbers
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + amount_str.replace('(', '').replace(')', '')
        
        # Handle dash representing zero
        if amount_str == '-' or amount_str == '':
            return Decimal('0')
            
        try:
            return Decimal(amount_str)
        except:
            return Decimal('0')
    
    def load_all_data(self):
        """Load all transaction data with proper date parsing."""
        print("Loading all transaction data with fixed date parsing...")
        print("-" * 60)
        
        # Load Legacy Expenses
        self.load_legacy_expenses()
        
        # Load Legacy Rent with fixed date parsing
        self.load_legacy_rent()
        
        # Load Legacy Zelle
        self.load_legacy_zelle()
        
        # Load Bank Exports
        self.load_bank_exports()
        
        # Sort all transactions by date
        self.all_transactions.sort(key=lambda x: x['date'] if x['date'] else datetime(2099, 12, 31))
        
        print(f"\nTotal transactions loaded: {len(self.all_transactions)}")
    
    def load_legacy_expenses(self):
        """Load Phase 4 expense history."""
        print("Loading Legacy Expense History...")
        try:
            df = pd.read_csv("test-data/legacy/Consolidated_Expense_History_20250622.csv")
            count = 0
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Date of Purchase'))
                if date:
                    actual = self.parse_amount(row.get(' Actual Amount '))
                    allowed = self.parse_amount(row.get(' Allowed Amount '))
                    
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Expenses',
                        'person': row.get('Name', ''),
                        'merchant': row.get('Merchant', ''),
                        'description': str(row.get(' Description ', '')),
                        'actual_amount': actual,
                        'allowed_amount': allowed,
                        'account': row.get('Account', ''),
                        'category': row.get('Category', ''),
                        'type': 'expense'
                    })
                    count += 1
            
            print(f"  [OK] Loaded {count} expense transactions")
        except Exception as e:
            print(f"  [ERROR] Error loading expenses: {e}")
    
    def load_legacy_rent(self):
        """Load Phase 4 rent allocation with FIXED date parsing."""
        print("Loading Legacy Rent Allocation...")
        try:
            df = pd.read_csv("test-data/legacy/Consolidated_Rent_Allocation_20250527.csv")
            count = 0
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Month'))
                if date:
                    gross_total = self.parse_amount(row.get('Gross Total'))
                    ryan_rent = self.parse_amount(row.get("Ryan's Rent (43%)"))
                    jordyn_rent = self.parse_amount(row.get("Jordyn's Rent (57%)"))
                    
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Rent',
                        'person': 'Both',
                        'merchant': 'Rent Payment',
                        'description': f"Monthly Rent - Total: ${gross_total:,.2f}",
                        'actual_amount': gross_total,
                        'allowed_amount': gross_total,
                        'ryan_portion': ryan_rent,
                        'jordyn_portion': jordyn_rent,
                        'account': 'Rent',
                        'category': 'Rent',
                        'type': 'rent'
                    })
                    count += 1
            
            print(f"  [OK] Loaded {count} rent transactions with correct dates")
        except Exception as e:
            print(f"  [ERROR] Error loading rent: {e}")
    
    def load_legacy_zelle(self):
        """Load Phase 4 Zelle payments."""
        print("Loading Legacy Zelle Payments...")
        try:
            df = pd.read_csv("test-data/legacy/Zelle_From_Jordyn_Final.csv")
            count = 0
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Date'))
                if date:
                    amount = self.parse_amount(row.get('Amount'))
                    
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Zelle',
                        'person': 'Jordyn->Ryan',
                        'merchant': 'Zelle Transfer',
                        'description': str(row.get('Original Statement', '')),
                        'actual_amount': amount,
                        'allowed_amount': amount,
                        'account': row.get('Account', ''),
                        'category': 'Settlement',
                        'type': 'settlement'
                    })
                    count += 1
            
            print(f"  [OK] Loaded {count} Zelle settlements")
        except Exception as e:
            print(f"  [ERROR] Error loading Zelle: {e}")
    
    def load_bank_exports(self):
        """Load Phase 5+ bank export data."""
        print("\nLoading Bank Export Data...")
        
        bank_files = {
            "Jordyn - Chase Bank - Total Checking x6173 - All.csv": ("Jordyn", "Chase"),
            "Jordyn - Discover - Discover It Card x1544 - CSV.csv": ("Jordyn", "Discover"),
            "Jordyn - Wells Fargo - Active Cash Visa Signature Card x4296 - CSV.csv": ("Jordyn", "WellsFargo"),
            "Ryan_Monarch_Money_20250720.csv": ("Ryan", "Monarch"),
            "Ryan_Rocket_Money_20250720.csv": ("Ryan", "Rocket")
        }
        
        for filename, (person, bank) in bank_files.items():
            try:
                path = Path(f"test-data/bank-exports/{filename}")
                if not path.exists():
                    continue
                    
                df = pd.read_csv(path, low_memory=False)
                count = 0
                
                # Find date column
                date_col = None
                for col in ['Date', 'Trans Date', 'Transaction Date', 'Post Date']:
                    if col in df.columns:
                        date_col = col
                        break
                
                if not date_col:
                    continue
                
                for _, row in df.iterrows():
                    date = self.parse_date(row.get(date_col))
                    if date and date.year >= 2022:  # Only include 2022 onwards
                        # Get description
                        desc = ''
                        for col in ['Description', 'Merchant', 'Name', 'Original Statement']:
                            if col in df.columns and pd.notna(row.get(col)):
                                desc = str(row.get(col))
                                break
                        
                        # Get amount
                        amount = Decimal('0')
                        for col in ['Amount', 'Transaction Amount', 'Debit', 'Credit']:
                            if col in df.columns:
                                amt = self.parse_amount(row.get(col))
                                if amt != 0:
                                    amount = amt
                                    break
                        
                        self.all_transactions.append({
                            'date': date,
                            'source': f'{person} {bank}',
                            'person': person,
                            'merchant': desc[:50] if desc else 'Unknown',
                            'description': desc,
                            'actual_amount': amount,
                            'allowed_amount': amount,
                            'account': row.get('Account', row.get('Account Name', bank)),
                            'category': row.get('Category', 'Uncategorized'),
                            'type': 'bank_export'
                        })
                        count += 1
                
                print(f"  [OK] {person} {bank}: {count} transactions")
                
            except Exception as e:
                print(f"  [ERROR] Error loading {filename}: {e}")
    
    def generate_monthly_summary(self):
        """Generate comprehensive monthly summary with balances."""
        print("\n" + "="*80)
        print("GENERATING MONTHLY SUMMARY REPORT")
        print("="*80)
        
        # Initialize monthly data
        for trans in self.all_transactions:
            if trans['date'] and trans['date'].year >= 2022:
                month_key = trans['date'].strftime('%Y-%m')
                
                if month_key not in self.monthly_summary:
                    self.monthly_summary[month_key] = {
                        'date': trans['date'].replace(day=1),
                        'ryan_expenses': Decimal('0'),
                        'jordyn_expenses': Decimal('0'),
                        'shared_expenses': Decimal('0'),
                        'rent_total': Decimal('0'),
                        'ryan_rent': Decimal('0'),
                        'jordyn_rent': Decimal('0'),
                        'settlements': Decimal('0'),
                        'transaction_count': 0,
                        'ryan_count': 0,
                        'jordyn_count': 0
                    }
                
                summary = self.monthly_summary[month_key]
                summary['transaction_count'] += 1
                
                # Count by person
                person = str(trans.get('person', ''))
                if 'Ryan' in person:
                    summary['ryan_count'] += 1
                    if trans['type'] == 'expense':
                        summary['ryan_expenses'] += abs(trans['allowed_amount'])
                elif 'Jordyn' in person:
                    summary['jordyn_count'] += 1
                    if trans['type'] == 'expense':
                        summary['jordyn_expenses'] += abs(trans['allowed_amount'])
                
                # Handle rent
                if trans['type'] == 'rent':
                    summary['rent_total'] += abs(trans['actual_amount'])
                    if 'ryan_portion' in trans:
                        summary['ryan_rent'] += abs(trans['ryan_portion'])
                    if 'jordyn_portion' in trans:
                        summary['jordyn_rent'] += abs(trans['jordyn_portion'])
                
                # Handle settlements
                if trans['type'] == 'settlement':
                    summary['settlements'] += trans['actual_amount']
        
        # Calculate running balances
        running_balance = Decimal('0')
        for month_key in sorted(self.monthly_summary.keys()):
            summary = self.monthly_summary[month_key]
            
            # Calculate who owes whom this month
            ryan_total = summary['ryan_expenses'] / 2 + summary['ryan_rent']
            jordyn_total = summary['jordyn_expenses'] / 2 + summary['jordyn_rent']
            
            # Net for this month (positive = Ryan owes Jordyn)
            month_net = jordyn_total - ryan_total + summary['settlements']
            running_balance += month_net
            summary['running_balance'] = running_balance
            summary['month_net'] = month_net
        
        # Display summary
        self.display_summary()
        
        # Export to JSON
        self.export_summary()
    
    def display_summary(self):
        """Display the monthly summary in a formatted table."""
        print("\nMONTHLY FINANCIAL SUMMARY (2022-2025)")
        print("-" * 100)
        print(f"{'Month':<10} {'Trans':<7} {'Ryan Exp':<12} {'Jordyn Exp':<12} "
              f"{'Rent':<10} {'Settle':<10} {'Balance':<12}")
        print("-" * 100)
        
        for month_key in sorted(self.monthly_summary.keys()):
            summary = self.monthly_summary[month_key]
            month_display = summary['date'].strftime('%b %Y')
            
            balance_str = f"${abs(summary['running_balance']):,.2f}"
            if summary['running_balance'] > 0:
                balance_str = f"R->J {balance_str}"
            elif summary['running_balance'] < 0:
                balance_str = f"J->R {balance_str}"
            else:
                balance_str = "Balanced"
            
            print(f"{month_display:<10} {summary['transaction_count']:<7} "
                  f"${summary['ryan_expenses']:>10,.2f} ${summary['jordyn_expenses']:>10,.2f} "
                  f"${summary['rent_total']:>8,.2f} ${summary['settlements']:>8,.2f} {balance_str:<12}")
        
        # Final summary
        print("-" * 100)
        final_balance = list(self.monthly_summary.values())[-1]['running_balance']
        print(f"\nFINAL BALANCE as of {datetime.now().strftime('%B %Y')}:")
        if final_balance > 0:
            print(f"  Ryan owes Jordyn: ${abs(final_balance):,.2f}")
        elif final_balance < 0:
            print(f"  Jordyn owes Ryan: ${abs(final_balance):,.2f}")
        else:
            print(f"  Accounts are balanced!")
    
    def export_summary(self):
        """Export summary to JSON file."""
        filename = f"monthly_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert Decimal to float for JSON serialization
        export_data = {}
        for month_key, summary in self.monthly_summary.items():
            export_data[month_key] = {
                'date': summary['date'].strftime('%Y-%m-%d'),
                'transaction_count': summary['transaction_count'],
                'ryan_count': summary['ryan_count'],
                'jordyn_count': summary['jordyn_count'],
                'ryan_expenses': float(summary['ryan_expenses']),
                'jordyn_expenses': float(summary['jordyn_expenses']),
                'rent_total': float(summary['rent_total']),
                'ryan_rent': float(summary['ryan_rent']),
                'jordyn_rent': float(summary['jordyn_rent']),
                'settlements': float(summary['settlements']),
                'month_net': float(summary['month_net']),
                'running_balance': float(summary['running_balance'])
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\nSummary exported to: {filename}")

def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("COMPREHENSIVE FINANCIAL ANALYSIS SYSTEM")
    print("With Fixed Date Parsing and Balance Calculations")
    print("="*80)
    
    analyzer = ComprehensiveAnalyzer()
    
    # Load all data
    analyzer.load_all_data()
    
    # Generate monthly summary
    analyzer.generate_monthly_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()