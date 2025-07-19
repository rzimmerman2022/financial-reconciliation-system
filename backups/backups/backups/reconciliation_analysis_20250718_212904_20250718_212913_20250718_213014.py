#!/usr/bin/env python3
"""
Financial Reconciliation Analysis Engine

This comprehensive engine analyzes the three normalized files to identify:
1. Rent payment patterns and coverage
2. Zelle payment validation against expenses  
3. Expense splitting analysis
4. Outstanding balances and discrepancies
5. Time-based trends and patterns

RUN FROM PROJECT ROOT: python reconciliation_analysis.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Tuple, Optional

def load_normalized_data():
    """Load all three normalized CSV files."""
    print("📁 LOADING NORMALIZED DATA")
    print("=" * 50)
    
    data = {}
    
    # Load rent allocation data
    rent_file = Path("data/processed/rent_allocation_normalized.csv")
    if rent_file.exists():
        data['rent'] = pd.read_csv(rent_file)
        print(f"   ✓ Rent data: {len(data['rent'])} records")
    else:
        print("   ❌ Rent data file not found")
        return None
    
    # Load Zelle payments data  
    zelle_file = Path("data/processed/zelle_payments_normalized.csv")
    if zelle_file.exists():
        data['zelle'] = pd.read_csv(zelle_file)
        data['zelle']['date'] = pd.to_datetime(data['zelle']['date'])
        print(f"   ✓ Zelle data: {len(data['zelle'])} records")
    else:
        print("   ❌ Zelle data file not found")
        return None
    
    # Load expense history data
    expenses_file = Path("data/processed/expense_history_normalized.csv") 
    if expenses_file.exists():
        data['expenses'] = pd.read_csv(expenses_file)
        data['expenses']['date'] = pd.to_datetime(data['expenses']['date'])
        print(f"   ✓ Expense data: {len(data['expenses'])} records")
    else:
        print("   ❌ Expense data file not found")
        return None
    
    print(f"\n✅ All data loaded successfully!")
    return data

def analyze_rent_coverage(rent_data, zelle_data):
    """Analyze how well Zelle payments cover Jordyn's rent obligations."""
    print("\n🏠 RENT COVERAGE ANALYSIS")
    print("=" * 50)
    
    analysis = {
        'monthly_breakdown': [],
        'summary': {},
        'discrepancies': []
    }
    
    # Convert rent months to datetime for easier comparison
    # Handle format like "Jan-24" -> "2024-01-01"
    rent_data['month_date'] = pd.to_datetime(rent_data['month'], format='%b-%y')
    
    # Group Zelle payments by month
    zelle_data['year_month'] = zelle_data['date'].dt.to_period('M')
    zelle_monthly = zelle_data.groupby('year_month')['amount'].sum()
    
    print("📊 Monthly rent vs Zelle payments:")
    print()
    
    total_rent_owed = 0
    total_zelle_received = 0
    
    for _, rent_row in rent_data.iterrows():
        month = rent_row['month']
        month_date = rent_row['month_date']
        jordyn_rent = rent_row['jordyn_amount']
        
        # Find corresponding Zelle payments
        rent_period = month_date.to_period('M')
        zelle_amount = zelle_monthly.get(rent_period, 0)
        
        difference = zelle_amount - jordyn_rent
        coverage_percent = (zelle_amount / jordyn_rent * 100) if jordyn_rent > 0 else 0
        
        month_analysis = {
            'month': month,
            'jordyn_rent_owed': jordyn_rent,
            'zelle_received': zelle_amount,
            'difference': difference,
            'coverage_percent': coverage_percent,
            'status': 'Overpaid' if difference > 0 else 'Underpaid' if difference < 0 else 'Exact'
        }
        
        analysis['monthly_breakdown'].append(month_analysis)
        total_rent_owed += jordyn_rent
        total_zelle_received += zelle_amount
        
        status_icon = "✅" if abs(difference) < 0.01 else "💰" if difference > 0 else "⚠️"
        print(f"   {status_icon} {month}: Owed ${jordyn_rent:,.2f}, Received ${zelle_amount:,.2f}, Diff: ${difference:+,.2f} ({coverage_percent:.1f}%)")
        
        if abs(difference) > 0.01:
            analysis['discrepancies'].append({
                'month': month,
                'type': 'overpayment' if difference > 0 else 'underpayment',
                'amount': abs(difference)
            })
    
    # Summary statistics
    analysis['summary'] = {
        'total_rent_owed': total_rent_owed,
        'total_zelle_received': total_zelle_received,
        'overall_difference': total_zelle_received - total_rent_owed,
        'average_coverage_percent': np.mean([m['coverage_percent'] for m in analysis['monthly_breakdown']]),
        'months_with_discrepancies': len(analysis['discrepancies']),
        'total_months': len(analysis['monthly_breakdown'])
    }
    
    print(f"\n📈 SUMMARY:")
    print(f"   Total rent owed by Jordyn: ${total_rent_owed:,.2f}")
    print(f"   Total Zelle payments received: ${total_zelle_received:,.2f}")
    print(f"   Overall difference: ${analysis['summary']['overall_difference']:+,.2f}")
    print(f"   Average coverage: {analysis['summary']['average_coverage_percent']:.1f}%")
    print(f"   Months with discrepancies: {analysis['summary']['months_with_discrepancies']}/{analysis['summary']['total_months']}")
    
    return analysis

def analyze_expense_patterns(expenses_data):
    """Analyze expense patterns by person and category."""
    print("\n💳 EXPENSE PATTERN ANALYSIS")
    print("=" * 50)
    
    # Filter to valid records only
    valid_expenses = expenses_data[expenses_data['date'].notna() & expenses_data['actual_amount'].notna()].copy()
    
    analysis = {
        'by_person': {},
        'by_category': {},
        'by_time': {},
        'shared_expenses': {},
        'summary': {}
    }
    
    # Analysis by person
    print("\n👥 EXPENSE BREAKDOWN BY PERSON:")
    person_groups = valid_expenses.groupby('person_normalized')
    
    for person, group in person_groups:
        if person and str(person).lower() != 'nan':
            person_stats = {
                'total_amount': group['actual_amount'].sum(),
                'transaction_count': len(group),
                'average_expense': group['actual_amount'].mean(),
                'date_range': {
                    'earliest': group['date'].min(),
                    'latest': group['date'].max()
                },
                'top_merchants': group.groupby('merchant')['actual_amount'].sum().sort_values(ascending=False).head(5).to_dict()
            }
            
            analysis['by_person'][person] = person_stats
            
            print(f"   {person}:")
            print(f"     💰 Total: ${person_stats['total_amount']:,.2f}")
            print(f"     📊 Transactions: {person_stats['transaction_count']}")
            print(f"     📈 Average: ${person_stats['average_expense']:.2f}")
            print(f"     📅 Period: {person_stats['date_range']['earliest'].strftime('%Y-%m-%d')} to {person_stats['date_range']['latest'].strftime('%Y-%m-%d')}")
    
    # Analysis by expense type
    print(f"\n📂 EXPENSE BREAKDOWN BY TYPE:")
    type_groups = valid_expenses.groupby('expense_type')
    
    for exp_type, group in type_groups:
        type_stats = {
            'total_amount': group['actual_amount'].sum(),
            'transaction_count': len(group),
            'average_expense': group['actual_amount'].mean(),
            'by_person': group.groupby('person_normalized')['actual_amount'].sum().to_dict()
        }
        
        analysis['by_category'][exp_type] = type_stats
        
        print(f"   {exp_type}:")
        print(f"     💰 Total: ${type_stats['total_amount']:,.2f}")
        print(f"     📊 Transactions: {type_stats['transaction_count']}")
        print(f"     📈 Average: ${type_stats['average_expense']:.2f}")
    
    # Time-based analysis
    print(f"\n📅 MONTHLY EXPENSE TRENDS:")
    monthly_expenses = valid_expenses.groupby(['year_month', 'person_normalized'])['actual_amount'].sum().unstack(fill_value=0)
    
    analysis['by_time']['monthly_totals'] = monthly_expenses.to_dict()
    
    for month in monthly_expenses.index:
        month_total = monthly_expenses.loc[month].sum()
        print(f"   {month}: ${month_total:,.2f}")
        for person in monthly_expenses.columns:
            if monthly_expenses.loc[month, person] > 0:
                print(f"     - {person}: ${monthly_expenses.loc[month, person]:,.2f}")
    
    # Overall summary
    analysis['summary'] = {
        'total_expenses': valid_expenses['actual_amount'].sum(),
        'total_transactions': len(valid_expenses),
        'average_expense': valid_expenses['actual_amount'].mean(),
        'date_range': {
            'earliest': valid_expenses['date'].min(),
            'latest': valid_expenses['date'].max(),
            'span_days': (valid_expenses['date'].max() - valid_expenses['date'].min()).days
        },
        'unique_merchants': valid_expenses['merchant'].nunique(),
        'people_count': valid_expenses['person_normalized'].nunique()
    }
    
    return analysis

def analyze_payment_timing(zelle_data, expenses_data):
    """Analyze timing patterns between Zelle payments and expenses."""
    print("\n⏰ PAYMENT TIMING ANALYSIS")
    print("=" * 50)
    
    analysis = {
        'zelle_patterns': {},
        'expense_patterns': {},
        'correlation': {}
    }
    
    # Zelle payment patterns
    zelle_data['day_of_month'] = zelle_data['date'].dt.day
    zelle_data['month_name'] = zelle_data['date'].dt.strftime('%B')
    
    print("💸 ZELLE PAYMENT PATTERNS:")
    print(f"   Payment frequency: {len(zelle_data)} payments over {zelle_data['date'].nunique()} unique dates")
    print(f"   Date range: {zelle_data['date'].min().strftime('%Y-%m-%d')} to {zelle_data['date'].max().strftime('%Y-%m-%d')}")
    print(f"   Most common payment day: {zelle_data['day_of_month'].mode().iloc[0]} of month")
    print(f"   Average days between payments: {(zelle_data['date'].max() - zelle_data['date'].min()).days / len(zelle_data):.1f}")
    
    # Payment amounts over time
    print(f"\n💰 ZELLE PAYMENT AMOUNTS:")
    for _, payment in zelle_data.iterrows():
        print(f"   {payment['date'].strftime('%Y-%m-%d')}: ${payment['amount']:,.2f}")
    
    analysis['zelle_patterns'] = {
        'payment_count': len(zelle_data),
        'date_range': {
            'start': zelle_data['date'].min(),
            'end': zelle_data['date'].max()
        },
        'common_day': int(zelle_data['day_of_month'].mode().iloc[0]),
        'amount_stats': {
            'total': zelle_data['amount'].sum(),
            'average': zelle_data['amount'].mean(),
            'min': zelle_data['amount'].min(),
            'max': zelle_data['amount'].max()
        }
    }
    
    # Expense timing patterns (valid records only)
    valid_expenses = expenses_data[expenses_data['date'].notna() & expenses_data['actual_amount'].notna()].copy()
    
    print(f"\n💳 EXPENSE TIMING PATTERNS:")
    monthly_expense_totals = valid_expenses.groupby('year_month')['actual_amount'].sum()
    jordyn_monthly = valid_expenses[valid_expenses['person_normalized'] == 'Jordyn'].groupby('year_month')['actual_amount'].sum()
    
    print(f"   Total expense months: {len(monthly_expense_totals)}")
    print(f"   Jordyn's expense months: {len(jordyn_monthly)}")
    
    # Look for patterns between Zelle payments and expense months
    zelle_months = set(zelle_data['year_month'].astype(str))
    jordyn_expense_months = set(jordyn_monthly.index.astype(str))
    
    overlapping_months = zelle_months.intersection(jordyn_expense_months)
    
    print(f"\n🔍 PAYMENT-EXPENSE CORRELATION:")
    print(f"   Months with Zelle payments: {len(zelle_months)}")
    print(f"   Months with Jordyn expenses: {len(jordyn_expense_months)}")
    print(f"   Overlapping months: {len(overlapping_months)}")
    
    if overlapping_months:
        print(f"   Overlapping months: {', '.join(sorted(overlapping_months))}")
    
    analysis['correlation'] = {
        'zelle_months': list(zelle_months),
        'jordyn_expense_months': list(jordyn_expense_months),
        'overlapping_months': list(overlapping_months),
        'correlation_ratio': len(overlapping_months) / len(zelle_months) if zelle_months else 0
    }
    
    return analysis

def calculate_balances(rent_analysis, expense_analysis, zelle_analysis):
    """Calculate overall financial balances and who owes what."""
    print("\n⚖️ BALANCE CALCULATION")
    print("=" * 50)
    
    balances = {
        'rent_balance': {},
        'expense_balance': {},
        'overall_balance': {},
        'summary': {}
    }
    
    # Rent balance (from rent coverage analysis)
    rent_difference = rent_analysis['summary']['overall_difference']
    balances['rent_balance'] = {
        'jordyn_rent_owed': rent_analysis['summary']['total_rent_owed'],
        'jordyn_paid': rent_analysis['summary']['total_zelle_received'],
        'difference': rent_difference,
        'status': 'Jordyn overpaid' if rent_difference > 0 else 'Jordyn underpaid' if rent_difference < 0 else 'Even'
    }
    
    print(f"🏠 RENT BALANCE:")
    print(f"   Jordyn's total rent obligation: ${balances['rent_balance']['jordyn_rent_owed']:,.2f}")
    print(f"   Jordyn's Zelle payments: ${balances['rent_balance']['jordyn_paid']:,.2f}")
    print(f"   Difference: ${rent_difference:+,.2f} ({balances['rent_balance']['status']})")
    
    # Expense balance analysis
    ryan_expenses = expense_analysis['by_person'].get('Ryan', {}).get('total_amount', 0)
    jordyn_expenses = expense_analysis['by_person'].get('Jordyn', {}).get('total_amount', 0)
    
    # Assuming 50/50 split for shared expenses
    total_expenses = ryan_expenses + jordyn_expenses
    each_should_pay = total_expenses / 2
    
    ryan_balance = ryan_expenses - each_should_pay
    jordyn_balance = jordyn_expenses - each_should_pay
    
    balances['expense_balance'] = {
        'total_expenses': total_expenses,
        'ryan_paid': ryan_expenses,
        'jordyn_paid': jordyn_expenses,
        'each_should_pay': each_should_pay,
        'ryan_balance': ryan_balance,
        'jordyn_balance': jordyn_balance
    }
    
    print(f"\n💳 EXPENSE BALANCE (50/50 split):")
    print(f"   Total shared expenses: ${total_expenses:,.2f}")
    print(f"   Each person should pay: ${each_should_pay:,.2f}")
    print(f"   Ryan paid: ${ryan_expenses:,.2f} (difference: ${ryan_balance:+,.2f})")
    print(f"   Jordyn paid: ${jordyn_expenses:,.2f} (difference: ${jordyn_balance:+,.2f})")
    
    # Overall balance
    jordyn_net_position = rent_difference + jordyn_balance
    ryan_net_position = -jordyn_net_position
    
    balances['overall_balance'] = {
        'jordyn_net': jordyn_net_position,
        'ryan_net': ryan_net_position,
        'who_owes_whom': 'Jordyn owes Ryan' if jordyn_net_position < 0 else 'Ryan owes Jordyn' if jordyn_net_position > 0 else 'Even',
        'amount_owed': abs(jordyn_net_position)
    }
    
    print(f"\n⚖️ OVERALL BALANCE:")
    print(f"   Jordyn's net position: ${jordyn_net_position:+,.2f}")
    print(f"   Ryan's net position: ${ryan_net_position:+,.2f}")
    print(f"   Result: {balances['overall_balance']['who_owes_whom']}")
    if balances['overall_balance']['amount_owed'] > 0:
        print(f"   Amount: ${balances['overall_balance']['amount_owed']:,.2f}")
    
    return balances

def generate_reconciliation_report(rent_analysis, expense_analysis, timing_analysis, balances):
    """Generate comprehensive reconciliation report."""
    print("\n📊 GENERATING RECONCILIATION REPORT")
    print("=" * 50)
    
    # Ensure output directory exists
    Path("output/reconciliation").mkdir(parents=True, exist_ok=True)
    
    report = {
        'report_metadata': {
            'generation_date': datetime.now().isoformat(),
            'report_type': 'comprehensive_financial_reconciliation',
            'data_sources': [
                'rent_allocation_normalized.csv',
                'zelle_payments_normalized.csv', 
                'expense_history_normalized.csv'
            ]
        },
        'rent_analysis': rent_analysis,
        'expense_analysis': expense_analysis,
        'timing_analysis': timing_analysis,
        'balance_calculations': balances,
        'recommendations': []
    }
    
    # Generate recommendations
    recommendations = []
    
    if balances['overall_balance']['amount_owed'] > 10:
        recommendations.append({
            'type': 'payment_needed',
            'priority': 'high',
            'description': f"{balances['overall_balance']['who_owes_whom']} ${balances['overall_balance']['amount_owed']:,.2f}",
            'action': 'Schedule payment to settle balance'
        })
    
    if len(rent_analysis['discrepancies']) > 0:
        recommendations.append({
            'type': 'rent_discrepancies',
            'priority': 'medium',
            'description': f"Found {len(rent_analysis['discrepancies'])} months with rent payment discrepancies",
            'action': 'Review individual monthly payments for accuracy'
        })
    
    if timing_analysis['correlation']['correlation_ratio'] < 0.8:
        recommendations.append({
            'type': 'payment_timing',
            'priority': 'low',
            'description': f"Zelle payments only correlate with {timing_analysis['correlation']['correlation_ratio']:.1%} of expense months",
            'action': 'Consider more regular payment schedule'
        })
    
    report['recommendations'] = recommendations
    
    # Save JSON report
    json_file = Path("output/reconciliation/financial_reconciliation_report.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"   ✓ JSON report saved: {json_file}")
    
    # Generate human-readable summary
    summary_file = Path("output/reconciliation/financial_reconciliation_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("FINANCIAL RECONCILIATION SUMMARY\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Analysis Period: All available data\n\n")
        
        f.write("RENT ANALYSIS SUMMARY:\n")
        f.write(f"  Total rent owed by Jordyn: ${rent_analysis['summary']['total_rent_owed']:,.2f}\n")
        f.write(f"  Total Zelle payments: ${rent_analysis['summary']['total_zelle_received']:,.2f}\n")
        f.write(f"  Difference: ${rent_analysis['summary']['overall_difference']:+,.2f}\n")
        f.write(f"  Months analyzed: {rent_analysis['summary']['total_months']}\n")
        f.write(f"  Months with discrepancies: {rent_analysis['summary']['months_with_discrepancies']}\n\n")
        
        f.write("EXPENSE ANALYSIS SUMMARY:\n")
        f.write(f"  Total expenses: ${expense_analysis['summary']['total_expenses']:,.2f}\n")
        f.write(f"  Total transactions: {expense_analysis['summary']['total_transactions']:,}\n")
        f.write(f"  Average expense: ${expense_analysis['summary']['average_expense']:.2f}\n")
        f.write(f"  Analysis period: {expense_analysis['summary']['date_range']['span_days']} days\n\n")
        
        f.write("BALANCE SUMMARY:\n")
        f.write(f"  Overall result: {balances['overall_balance']['who_owes_whom']}\n")
        if balances['overall_balance']['amount_owed'] > 0:
            f.write(f"  Amount owed: ${balances['overall_balance']['amount_owed']:,.2f}\n")
        f.write("\n")
        
        if recommendations:
            f.write("RECOMMENDATIONS:\n")
            for i, rec in enumerate(recommendations, 1):
                f.write(f"  {i}. {rec['description']}\n")
                f.write(f"     Action: {rec['action']}\n")
                f.write(f"     Priority: {rec['priority'].upper()}\n\n")
    
    print(f"   ✓ Summary report saved: {summary_file}")
    
    return report

def main():
    """Main reconciliation analysis process."""
    print("🔍 FINANCIAL RECONCILIATION ANALYSIS")
    print("Comprehensive analysis of all normalized data")
    print("=" * 60)
    
    try:
        # Load all normalized data
        data = load_normalized_data()
        if not data:
            return False
        
        # Perform rent coverage analysis
        rent_analysis = analyze_rent_coverage(data['rent'], data['zelle'])
        
        # Perform expense pattern analysis  
        expense_analysis = analyze_expense_patterns(data['expenses'])
        
        # Perform payment timing analysis
        timing_analysis = analyze_payment_timing(data['zelle'], data['expenses'])
        
        # Calculate balances
        balances = calculate_balances(rent_analysis, expense_analysis, timing_analysis)
        
        # Generate comprehensive report
        report = generate_reconciliation_report(rent_analysis, expense_analysis, timing_analysis, balances)
        
        # Final summary
        print("\n🎯 RECONCILIATION ANALYSIS COMPLETE")
        print("=" * 60)
        print("✅ All data analyzed successfully")
        print("📁 Reports saved to: output/reconciliation/")
        print("\n🔍 KEY FINDINGS:")
        print(f"   💰 Overall balance: {balances['overall_balance']['who_owes_whom']}")
        if balances['overall_balance']['amount_owed'] > 0:
            print(f"   💸 Amount: ${balances['overall_balance']['amount_owed']:,.2f}")
        print(f"   📊 Recommendations: {len(report['recommendations'])} items")
        
        print("\n📋 NEXT STEPS:")
        print("   1. Review the reconciliation report")
        print("   2. Address any recommendations")
        print("   3. Set up regular reconciliation schedule")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during reconciliation: {e}")
        return False

if __name__ == "__main__":
    success = main()
