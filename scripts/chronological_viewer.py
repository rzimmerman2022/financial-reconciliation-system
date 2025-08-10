#!/usr/bin/env python3
"""
Comprehensive Chronological Transaction Viewer
==============================================

View all transactions from the very beginning (September 2022) in chronological order.
Combines all data sources and presents a unified timeline.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
from decimal import Decimal
import warnings
warnings.filterwarnings('ignore')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

class ChronologicalViewer:
    """Comprehensive viewer for all transactions in chronological order."""
    
    def __init__(self):
        self.all_transactions = []
        self.date_formats = [
            '%Y-%m-%d',
            '%m/%d/%Y', 
            '%m/%d/%y',
            '%Y/%m/%d',
            '%d-%b',
            '%y-%b'
        ]
        
    def parse_date(self, date_str):
        """Parse various date formats."""
        if pd.isna(date_str):
            return None
            
        date_str = str(date_str).strip()
        
        # Try each format
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
                
        # Special handling for Month-Year format (e.g., "24-Jan" or "Jan-24")
        if '-' in date_str and len(date_str) <= 7:
            try:
                parts = date_str.split('-')
                if len(parts) == 2:
                    # Check both YY-Mon and Mon-YY formats
                    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 
                             'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
                    
                    # Try YY-Mon format first (e.g., "24-Jan")
                    if parts[0].isdigit() and len(parts[0]) == 2:
                        year = 2000 + int(parts[0])
                        month_lower = parts[1].lower()[:3]
                        if month_lower in months:
                            month = months.index(month_lower) + 1
                            return datetime(year, month, 1)
                    
                    # Try Mon-YY format (e.g., "Jan-24")  
                    elif parts[1].isdigit() and len(parts[1]) == 2:
                        year = 2000 + int(parts[1])
                        month_lower = parts[0].lower()[:3]
                        if month_lower in months:
                            month = months.index(month_lower) + 1
                            return datetime(year, month, 1)
            except:
                pass
                
        return None
    
    def parse_amount(self, amount_str):
        """Parse amount from various formats."""
        if pd.isna(amount_str):
            return 0.0
            
        amount_str = str(amount_str).strip()
        
        # Remove currency symbols and commas
        amount_str = amount_str.replace('$', '').replace(',', '').strip()
        
        # Handle parentheses for negative numbers
        if '(' in amount_str and ')' in amount_str:
            amount_str = '-' + amount_str.replace('(', '').replace(')', '')
            
        try:
            return float(amount_str)
        except:
            return 0.0
    
    def load_legacy_expenses(self):
        """Load Phase 4 expense history."""
        print("Loading Legacy Expense History...")
        try:
            df = pd.read_csv("test-data/legacy/Consolidated_Expense_History_20250622.csv")
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Date of Purchase'))
                if date:
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Expenses',
                        'person': row.get('Name', ''),
                        'merchant': row.get('Merchant', ''),
                        'description': row.get(' Description ', ''),
                        'actual_amount': self.parse_amount(row.get(' Actual Amount ')),
                        'allowed_amount': self.parse_amount(row.get(' Allowed Amount ')),
                        'account': row.get('Account', ''),
                        'category': row.get('Category', ''),
                        'type': 'expense'
                    })
            
            print(f"  Loaded {len(df)} expense transactions")
        except Exception as e:
            print(f"  Error loading expenses: {e}")
    
    def load_legacy_rent(self):
        """Load Phase 4 rent allocation."""
        print("Loading Legacy Rent Allocation...")
        try:
            df = pd.read_csv("test-data/legacy/Consolidated_Rent_Allocation_20250527.csv")
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Month'))
                if date:
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Rent',
                        'person': 'Both',
                        'merchant': 'Rent',
                        'description': f"Monthly Rent - Gross: {row.get('Gross Total', '')}",
                        'actual_amount': self.parse_amount(row.get('Gross Total')),
                        'allowed_amount': self.parse_amount(row.get('Gross Total')),
                        'ryan_portion': self.parse_amount(row.get("Ryan's Rent (43%)")),
                        'jordyn_portion': self.parse_amount(row.get("Jordyn's Rent (57%)")),
                        'account': 'Rent',
                        'category': 'Rent',
                        'type': 'rent'
                    })
            
            print(f"  Loaded {len(df)} rent transactions")
        except Exception as e:
            print(f"  Error loading rent: {e}")
    
    def load_legacy_zelle(self):
        """Load Phase 4 Zelle payments."""
        print("Loading Legacy Zelle Payments...")
        try:
            df = pd.read_csv("test-data/legacy/Zelle_From_Jordyn_Final.csv")
            
            for _, row in df.iterrows():
                date = self.parse_date(row.get('Date'))
                if date:
                    self.all_transactions.append({
                        'date': date,
                        'source': 'Legacy Zelle',
                        'person': 'Jordyn to Ryan',
                        'merchant': 'Zelle Transfer',
                        'description': row.get('Original Statement', ''),
                        'actual_amount': self.parse_amount(row.get('Amount')),
                        'allowed_amount': self.parse_amount(row.get('Amount')),
                        'account': row.get('Account', ''),
                        'category': 'Settlement',
                        'type': 'settlement'
                    })
            
            print(f"  Loaded {len(df)} Zelle transactions")
        except Exception as e:
            print(f"  Error loading Zelle: {e}")
    
    def load_bank_exports(self):
        """Load Phase 5+ bank export data."""
        print("\nLoading Bank Export Data...")
        
        bank_files = {
            "Jordyn - Chase Bank - Total Checking x6173 - All.csv": "Jordyn Chase",
            "Jordyn - Discover - Discover It Card x1544 - CSV.csv": "Jordyn Discover",
            "Jordyn - Wells Fargo - Active Cash Visa Signature Card x4296 - CSV.csv": "Jordyn Wells Fargo",
            "Ryan_Monarch_Money_20250720.csv": "Ryan Monarch",
            "Ryan_Rocket_Money_20250720.csv": "Ryan Rocket"
        }
        
        for filename, source_name in bank_files.items():
            try:
                path = Path(f"test-data/bank-exports/{filename}")
                if not path.exists():
                    continue
                    
                df = pd.read_csv(path)
                count = 0
                
                # Handle different date column names
                date_col = None
                for col in ['Date', 'Trans Date', 'Transaction Date', 'Post Date']:
                    if col in df.columns:
                        date_col = col
                        break
                
                if not date_col:
                    print(f"  Warning: No date column found in {filename}")
                    continue
                
                for _, row in df.iterrows():
                    date = self.parse_date(row.get(date_col))
                    if date:
                        # Determine person from source
                        if 'Jordyn' in source_name:
                            person = 'Jordyn'
                        elif 'Ryan' in source_name:
                            person = 'Ryan'
                        else:
                            person = 'Unknown'
                        
                        # Get description
                        desc_col = None
                        for col in ['Description', 'Merchant', 'Name', 'Original Statement']:
                            if col in df.columns:
                                desc_col = col
                                break
                        
                        description = row.get(desc_col, '') if desc_col else ''
                        
                        # Get amount
                        amount_col = None
                        for col in ['Amount', 'Transaction Amount', 'Debit', 'Credit']:
                            if col in df.columns:
                                amount_col = col
                                break
                        
                        amount = self.parse_amount(row.get(amount_col)) if amount_col else 0.0
                        
                        self.all_transactions.append({
                            'date': date,
                            'source': source_name,
                            'person': person,
                            'merchant': row.get('Merchant', description[:50]),
                            'description': description,
                            'actual_amount': amount,
                            'allowed_amount': amount,  # Phase 5+ needs manual review
                            'account': row.get('Account', row.get('Account Name', '')),
                            'category': row.get('Category', 'Uncategorized'),
                            'type': 'bank_export'
                        })
                        count += 1
                
                print(f"  Loaded {count} transactions from {source_name}")
                
            except Exception as e:
                print(f"  Error loading {filename}: {e}")
    
    def display_chronological(self):
        """Display all transactions in chronological order."""
        # Sort by date
        self.all_transactions.sort(key=lambda x: x['date'] if x['date'] else datetime(2099, 12, 31))
        
        # Group by month for summary
        monthly_summary = {}
        
        for trans in self.all_transactions:
            if trans['date']:
                month_key = trans['date'].strftime('%Y-%m')
                if month_key not in monthly_summary:
                    monthly_summary[month_key] = {
                        'count': 0,
                        'total_amount': 0,
                        'ryan_count': 0,
                        'jordyn_count': 0,
                        'settlements': 0
                    }
                
                monthly_summary[month_key]['count'] += 1
                monthly_summary[month_key]['total_amount'] += abs(trans['actual_amount'])
                
                person = str(trans.get('person', ''))
                if 'Ryan' in person:
                    monthly_summary[month_key]['ryan_count'] += 1
                elif 'Jordyn' in person:
                    monthly_summary[month_key]['jordyn_count'] += 1
                    
                if trans['type'] == 'settlement':
                    monthly_summary[month_key]['settlements'] += 1
        
        # Display summary
        print("\n" + "="*80)
        print("CHRONOLOGICAL TRANSACTION SUMMARY")
        print("="*80)
        print(f"\nTotal Transactions: {len(self.all_transactions)}")
        
        if self.all_transactions:
            first_date = min(t['date'] for t in self.all_transactions if t['date'])
            last_date = max(t['date'] for t in self.all_transactions if t['date'])
            print(f"Date Range: {first_date.strftime('%B %d, %Y')} to {last_date.strftime('%B %d, %Y')}")
        
        print("\n" + "-"*80)
        print("MONTHLY BREAKDOWN")
        print("-"*80)
        print(f"{'Month':<12} {'Total':<8} {'Ryan':<8} {'Jordyn':<8} {'Settle':<8} {'Amount':<15}")
        print("-"*80)
        
        for month in sorted(monthly_summary.keys()):
            data = monthly_summary[month]
            month_display = datetime.strptime(month, '%Y-%m').strftime('%b %Y')
            print(f"{month_display:<12} {data['count']:<8} {data['ryan_count']:<8} "
                  f"{data['jordyn_count']:<8} {data['settlements']:<8} "
                  f"${data['total_amount']:,.2f}")
        
        # Show first and last transactions
        print("\n" + "-"*80)
        print("FIRST 10 TRANSACTIONS")
        print("-"*80)
        
        for i, trans in enumerate(self.all_transactions[:10], 1):
            if trans['date']:
                print(f"\n{i}. {trans['date'].strftime('%Y-%m-%d')} | {trans['source']}")
                print(f"   Person: {trans['person']} | Merchant: {trans['merchant'][:50]}")
                print(f"   Amount: ${trans['actual_amount']:,.2f} | Type: {trans['type']}")
                if trans['description']:
                    print(f"   Description: {trans['description'][:100]}")
        
        print("\n" + "-"*80)
        print("LAST 10 TRANSACTIONS")
        print("-"*80)
        
        for i, trans in enumerate(self.all_transactions[-10:], 1):
            if trans['date']:
                print(f"\n{i}. {trans['date'].strftime('%Y-%m-%d')} | {trans['source']}")
                print(f"   Person: {trans['person']} | Merchant: {trans['merchant'][:50]}")
                print(f"   Amount: ${trans['actual_amount']:,.2f} | Type: {trans['type']}")
                if trans['description']:
                    print(f"   Description: {trans['description'][:100]}")
        
        # Auto-export to CSV
        print("\n" + "="*80)
        print("AUTO-EXPORTING TO CSV")
        print("="*80)
        self.export_to_csv()
    
    def export_to_csv(self):
        """Export all transactions to CSV."""
        try:
            # Convert to DataFrame
            df = pd.DataFrame(self.all_transactions)
            
            # Format dates
            df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d') if x else '')
            
            # Sort by date
            df = df.sort_values('date')
            
            # Save to CSV
            filename = f"chronological_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            df.to_csv(filename, index=False)
            
            print(f"\nTransactions exported to: {filename}")
            print(f"Total rows: {len(df)}")
        except Exception as e:
            print(f"\nError exporting to CSV: {e}")

def main():
    """Main entry point."""
    print("\n" + "="*80)
    print("COMPREHENSIVE CHRONOLOGICAL TRANSACTION VIEWER")
    print("Starting from September 2022 - The Very Beginning")
    print("="*80)
    
    viewer = ChronologicalViewer()
    
    # Load all data sources
    print("\nLoading all transaction data...")
    print("-"*40)
    
    # Phase 4 Legacy Data
    viewer.load_legacy_expenses()
    viewer.load_legacy_rent()
    viewer.load_legacy_zelle()
    
    # Phase 5+ Bank Exports
    viewer.load_bank_exports()
    
    # Display chronological view
    viewer.display_chronological()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting viewer...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()