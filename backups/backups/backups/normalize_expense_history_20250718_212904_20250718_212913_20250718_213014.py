#!/usr/bin/env python3
"""
Expense History Normalization - File 3 of 3

This script normalizes the Consolidated_Expense_History_20250622.csv file
with complete audit trail for review.

WHAT THIS DOES:
1. Loads raw expense history data  
2. Analyzes structure and data quality
3. Normalizes column names and data types (handles spaces in column names)
4. Cleans currency values and parses dates
5. Validates expense records and business logic
6. Generates detailed audit trail
7. Saves normalized data to data/processed/

RUN FROM PROJECT ROOT: python normalize_expense_history.py
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime
import json

def setup_output_directory():
    """Ensure output directories exist."""
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    Path("output/audit_trails").mkdir(parents=True, exist_ok=True)
    return True

def load_raw_data():
    """Load the raw expense history CSV."""
    file_path = Path("data/raw/Consolidated_Expense_History_20250622.csv")
    
    print(f"📁 Loading raw data from: {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Load with all strings to preserve original format
    raw_data = pd.read_csv(file_path, dtype=str)
    
    print(f"   ✓ Loaded {len(raw_data)} records")
    print(f"   ✓ Found {len(raw_data.columns)} columns")
    
    return raw_data

def analyze_raw_structure(raw_data):
    """Analyze the raw data structure."""
    print("\n🔍 ANALYZING RAW DATA STRUCTURE")
    print("=" * 50)
    
    analysis = {
        'total_records': len(raw_data),
        'total_columns': len(raw_data.columns),
        'columns': list(raw_data.columns),
        'sample_data': {},
        'data_types': {},
        'missing_values': {},
        'column_issues': []
    }
    
    # Check for problematic column names (spaces, etc.)
    for col in raw_data.columns:
        if col != col.strip():
            analysis['column_issues'].append(f"Column '{col}' has leading/trailing spaces")
        if '  ' in col:
            analysis['column_issues'].append(f"Column '{col}' has multiple spaces")
    
    # Analyze each column
    for col in raw_data.columns:
        print(f"\n📊 Column: '{col}' (length: {len(col)})")
        
        # Sample data (first non-null value)
        sample_val = raw_data[col].dropna().iloc[0] if len(raw_data[col].dropna()) > 0 else None
        analysis['sample_data'][col] = str(sample_val) if sample_val is not None else None
        print(f"   Sample value: '{sample_val}'")
        
        # Missing values
        missing_count = raw_data[col].isnull().sum()
        analysis['missing_values'][col] = missing_count
        if missing_count > 0:
            print(f"   ⚠ Missing values: {missing_count}")
        
        # Check for data type patterns
        non_null_values = raw_data[col].dropna()
        if len(non_null_values) > 0:
            # Check if it looks like a date
            date_pattern = r'^\d{1,2}/\d{1,2}/\d{4}$'
            is_date = non_null_values.str.match(date_pattern, na=False).any()
            
            # Check if it looks like currency/amount
            currency_pattern = r'^\$?-?\d+(\.\d{2})?$'
            is_currency = non_null_values.str.match(currency_pattern, na=False).any()
            
            # Check if it's a name field
            is_name = col.lower().strip() == 'name'
            
            # Check if it's a category field
            is_category = 'category' in col.lower()
            
            if is_date:
                analysis['data_types'][col] = 'date'
                print("   📅 Detected: Date values")
            elif is_currency:
                analysis['data_types'][col] = 'currency'
                print("   💰 Detected: Currency values")
            elif is_name:
                analysis['data_types'][col] = 'person_name'
                print("   👤 Detected: Person name")
            elif is_category:
                analysis['data_types'][col] = 'category'
                print("   📂 Detected: Category values")
            else:
                analysis['data_types'][col] = 'text'
                print("   📝 Detected: Text values")
    
    return analysis

def clean_currency_value(value):
    """Clean currency/amount string to float."""
    if pd.isna(value) or value == '' or str(value).strip() == '':
        return None
    
    try:
        # Remove currency symbols, commas, and extra spaces
        cleaned = re.sub(r'[$,\s]', '', str(value))
        
        # Handle negative values in parentheses
        if cleaned.startswith('(') and cleaned.endswith(')'):
            cleaned = '-' + cleaned[1:-1]
        
        if cleaned == '' or cleaned == '-':
            return None
            
        return float(cleaned)
    except (ValueError, TypeError):
        print(f"   ⚠ Could not parse amount: '{value}'")
        return None

def parse_date_value(date_str):
    """Parse date string to datetime object."""
    if pd.isna(date_str) or date_str == '' or str(date_str).strip() == '':
        return None
    
    # Try common date formats
    date_formats = [
        '%m/%d/%Y', '%Y-%m-%d', '%m-%d-%Y', '%d-%m-%Y',
        '%m/%d/%y', '%y-%m-%d', '%m-%d-%y', '%d-%m-%y'
    ]
    
    date_str = str(date_str).strip()
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    # Try pandas as fallback
    try:
        return pd.to_datetime(date_str)
    except Exception:
        print(f"   ⚠ Could not parse date: '{date_str}'")
        return None

def normalize_data(raw_data, analysis):
    """Normalize the expense history data."""
    print("\n🔄 NORMALIZING DATA")
    print("=" * 50)
    
    # Start with a copy
    normalized = raw_data.copy()
    
    normalization_log = {
        'column_mappings': {},
        'data_transformations': {},
        'validation_results': {},
        'issues_found': []
    }
    
    # Step 1: Standardize column names (handle the space issues we know about)
    print("\n📝 Step 1: Standardizing column names")
    
    # Define expected column mapping based on ExpenseProcessor
    column_mapping = {
        'Name': 'person',
        'Date of Purchase': 'date',
        'Account': 'account',
        'Merchant': 'merchant',
        ' Merchant Description ': 'merchant_description',  # Note the spaces!
        ' Actual Amount ': 'actual_amount',  # Note the spaces!
        ' Allowed Amount ': 'allowed_amount',  # Note the spaces!
        ' Description ': 'description',  # Note the spaces!
        'Category': 'category',
        'Running Balance': 'running_balance'
    }
    
    # Apply column renaming
    actual_mapping = {}
    for old_col in normalized.columns:
        if old_col in column_mapping:
            new_col = column_mapping[old_col]
            actual_mapping[old_col] = new_col
            print(f"   '{old_col}' -> '{new_col}'")
        else:
            # Fallback: clean the column name
            new_col = old_col.strip().lower().replace(' ', '_').replace('(', '').replace(')', '')
            actual_mapping[old_col] = new_col
            print(f"   '{old_col}' -> '{new_col}' (auto-cleaned)")
    
    normalized = normalized.rename(columns=actual_mapping)
    normalization_log['column_mappings'] = actual_mapping
    
    # Step 2: Convert data types
    print("\n🔢 Step 2: Converting data types")
    
    # Convert date column
    if 'date' in normalized.columns:
        print("   Converting 'date' to datetime")
        original_values = normalized['date'].copy()
        normalized['date'] = normalized['date'].apply(parse_date_value)
        normalized['date_parsed'] = normalized['date'].notna()
        
        successful_conversions = normalized['date'].notna().sum()
        failed_conversions = len(original_values) - successful_conversions
        
        normalization_log['data_transformations']['date'] = {
            'type': 'date_conversion',
            'successful': successful_conversions,
            'failed': failed_conversions,
            'sample_before': str(original_values.iloc[0]) if len(original_values) > 0 else None,
            'sample_after': normalized['date'].iloc[0].isoformat() if len(normalized) > 0 and pd.notna(normalized['date'].iloc[0]) else None
        }
        
        print(f"     ✓ Converted {successful_conversions} dates")
        if failed_conversions > 0:
            print(f"     ⚠ Failed to convert {failed_conversions} dates")
    
    # Convert currency columns
    currency_fields = ['actual_amount', 'allowed_amount', 'running_balance']
    for field in currency_fields:
        if field in normalized.columns:
            print(f"   Converting '{field}' to currency")
            original_values = normalized[field].copy()
            normalized[field] = normalized[field].apply(clean_currency_value)
            
            successful_conversions = normalized[field].notna().sum()
            failed_conversions = len(original_values) - successful_conversions
            
            normalization_log['data_transformations'][field] = {
                'type': 'currency_conversion',
                'successful': successful_conversions,
                'failed': failed_conversions,
                'sample_before': str(original_values.iloc[0]) if len(original_values) > 0 else None,
                'sample_after': normalized[field].iloc[0] if len(normalized) > 0 else None
            }
            
            print(f"     ✓ Converted {successful_conversions} values")
            if failed_conversions > 0:
                print(f"     ⚠ Failed to convert {failed_conversions} values")
    
    # Clean text fields
    text_fields = ['person', 'account', 'merchant', 'merchant_description', 'description', 'category']
    for field in text_fields:
        if field in normalized.columns:
            normalized[field] = normalized[field].astype(str).str.strip()
            normalized[field] = normalized[field].replace('nan', None)
    
    # Step 3: Validate business logic
    print("\n✅ Step 3: Validating business logic")
    
    validation_results = validate_expense_logic(normalized)
    normalization_log['validation_results'] = validation_results
    
    # Report validation results
    valid_records = sum(1 for r in validation_results if r['is_valid'])
    invalid_records = len(validation_results) - valid_records
    
    print(f"   ✓ Valid expense records: {valid_records}")
    if invalid_records > 0:
        print(f"   ⚠ Invalid records: {invalid_records}")
        for result in validation_results:
            if not result['is_valid']:
                print(f"     - Record {result['record_id']}: {result['error']}")
                normalization_log['issues_found'].append(f"Record {result['record_id']}: {result['error']}")
    
    # Step 4: Add calculated fields
    print("\n📋 Step 4: Adding calculated fields")
    
    # Add year/month for grouping
    if 'date' in normalized.columns:
        normalized['year'] = normalized['date'].dt.year
        normalized['month'] = normalized['date'].dt.month
        normalized['year_month'] = normalized['date'].dt.to_period('M').astype(str)
    
    # Normalize person names
    if 'person' in normalized.columns:
        normalized['person_normalized'] = normalized['person'].str.strip().str.title()
        # Handle variations like "Jordyn " vs "Jordyn"
        normalized['person_normalized'] = normalized['person_normalized'].replace({
            'Jordyn ': 'Jordyn',
            'Jordyn Expenses': 'Jordyn'
        })
    
    # Calculate amount differences
    if 'actual_amount' in normalized.columns and 'allowed_amount' in normalized.columns:
        normalized['amount_difference'] = normalized['actual_amount'] - normalized['allowed_amount'].fillna(0)
        normalized['has_amount_difference'] = normalized['amount_difference'].abs() > 0.01
    
    # Add expense type classification
    normalized['expense_type'] = 'Other'
    if 'merchant' in normalized.columns:
        # Grocery stores
        grocery_pattern = r"Fry's|Whole Foods|Walmart|Target|Safeway|Kroger"
        normalized.loc[normalized['merchant'].str.contains(grocery_pattern, case=False, na=False), 'expense_type'] = 'Groceries'
        
        # Online shopping
        online_pattern = r'Amazon|eBay|Online'
        normalized.loc[normalized['merchant'].str.contains(online_pattern, case=False, na=False), 'expense_type'] = 'Online Shopping'
        
        # Gas stations
        gas_pattern = r'Gas|Shell|Chevron|BP|Exxon|Mobil'
        normalized.loc[normalized['merchant'].str.contains(gas_pattern, case=False, na=False), 'expense_type'] = 'Gas'
        
        # Dining
        dining_pattern = r'Restaurant|Food|Coffee|Starbucks|McDonald|Subway'
        normalized.loc[normalized['merchant'].str.contains(dining_pattern, case=False, na=False), 'expense_type'] = 'Dining'
    
    # Add metadata
    normalized['normalized_date'] = datetime.now().isoformat()
    normalized['data_source'] = 'Consolidated_Expense_History_20250622.csv'
    normalized['record_id'] = range(1, len(normalized) + 1)
    
    print("   ✓ Added calculated fields and metadata")
    
    return normalized, normalization_log

def validate_expense_logic(data):
    """Validate that expense records make business sense."""
    validation_results = []
    
    for idx, row in data.iterrows():
        result = {
            'record_id': idx + 1,
            'is_valid': True,
            'error': None,
            'warnings': [],
            'checks': {}
        }
        
        # Check 1: Person name should be valid
        person = str(row.get('person', '')).strip()
        result['checks']['has_person'] = person != '' and person.lower() != 'nan'
        if not result['checks']['has_person']:
            result['is_valid'] = False
            result['error'] = 'Missing person name'
        
        # Check 2: Date should be valid
        date_val = row.get('date')
        result['checks']['has_valid_date'] = pd.notna(date_val)
        if pd.isna(date_val):
            result['is_valid'] = False
            result['error'] = 'Missing or invalid date'
        
        # Check 3: Actual amount should be present and reasonable
        actual_amount = row.get('actual_amount')
        result['checks']['has_actual_amount'] = pd.notna(actual_amount) and actual_amount != 0
        if pd.isna(actual_amount):
            result['is_valid'] = False
            result['error'] = 'Missing actual amount'
        elif actual_amount == 0:
            result['warnings'].append('Zero actual amount')
        elif actual_amount < 0:
            result['warnings'].append('Negative actual amount')
        elif actual_amount > 5000:
            result['warnings'].append('Very large amount (>$5000)')
        
        # Check 4: Merchant should be present
        merchant = str(row.get('merchant', '')).strip()
        result['checks']['has_merchant'] = merchant != '' and merchant.lower() != 'nan'
        if not result['checks']['has_merchant']:
            result['warnings'].append('Missing merchant')
        
        # Check 5: Category should be present
        category = str(row.get('category', '')).strip()
        result['checks']['has_category'] = category != '' and category.lower() != 'nan'
        if not result['checks']['has_category']:
            result['warnings'].append('Missing category')
        
        # Check 6: Check amount difference if both amounts present
        actual_amount = row.get('actual_amount')
        allowed_amount = row.get('allowed_amount')
        if pd.notna(actual_amount) and pd.notna(allowed_amount):
            diff = abs(actual_amount - allowed_amount)
            result['checks']['amounts_match'] = diff < 0.01
            if diff > 0.01:
                result['warnings'].append(f'Amount difference: ${diff:.2f}')
        
        validation_results.append(result)
    
    return validation_results

def generate_audit_trail(raw_data, normalized_data, analysis, normalization_log):
    """Generate comprehensive audit trail."""
    print("\n📝 GENERATING AUDIT TRAIL")
    print("=" * 50)
    
    audit_trail = {
        'processing_metadata': {
            'processing_date': datetime.now().isoformat(),
            'source_file': 'data/raw/Consolidated_Expense_History_20250622.csv',
            'processor': 'expense_history_normalizer.py',
            'records_processed': len(raw_data)
        },
        'raw_data_analysis': analysis,
        'normalization_log': normalization_log,
        'before_after_comparison': {
            'raw_columns': list(raw_data.columns),
            'normalized_columns': list(normalized_data.columns),
            'raw_sample': raw_data.head(3).to_dict('records'),
            'normalized_sample': normalized_data.head(3).to_dict('records')
        },
        'data_quality_summary': {
            'total_records': len(normalized_data),
            'valid_records': sum(1 for result in normalization_log['validation_results'] if result['is_valid']),
            'invalid_records': sum(1 for result in normalization_log['validation_results'] if not result['is_valid']),
            'records_with_warnings': sum(1 for result in normalization_log['validation_results'] if result.get('warnings')),
            'issues_count': len(normalization_log['issues_found']),
            'issues_list': normalization_log['issues_found']
        }
    }
    
    # Calculate expense statistics
    if 'actual_amount' in normalized_data.columns:
        valid_amounts = normalized_data['actual_amount'].dropna()
        if len(valid_amounts) > 0:
            audit_trail['expense_statistics'] = {
                'total_expenses': float(valid_amounts.sum()),
                'average_expense': float(valid_amounts.mean()),
                'min_expense': float(valid_amounts.min()),
                'max_expense': float(valid_amounts.max()),
                'expense_count': len(valid_amounts)
            }
    
    # Person breakdown
    if 'person_normalized' in normalized_data.columns:
        person_stats = normalized_data['person_normalized'].value_counts().to_dict()
        audit_trail['person_breakdown'] = person_stats
    
    # Expense type breakdown
    if 'expense_type' in normalized_data.columns:
        type_stats = normalized_data['expense_type'].value_counts().to_dict()
        audit_trail['expense_type_breakdown'] = type_stats
    
    # Save audit trail
    audit_file = Path("output/audit_trails/expense_history_normalization_audit.json")
    with open(audit_file, 'w', encoding='utf-8') as f:
        json.dump(audit_trail, f, indent=2, default=str)
    
    print(f"   ✓ Audit trail saved to: {audit_file}")
    
    # Generate human-readable summary
    summary_file = Path("output/audit_trails/expense_history_normalization_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("EXPENSE HISTORY NORMALIZATION SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Processing Date: {audit_trail['processing_metadata']['processing_date']}\n")
        f.write(f"Source File: {audit_trail['processing_metadata']['source_file']}\n")
        f.write(f"Records Processed: {audit_trail['processing_metadata']['records_processed']}\n\n")
        
        f.write("COLUMN MAPPINGS:\n")
        for old_col, new_col in normalization_log['column_mappings'].items():
            f.write(f"  '{old_col}' -> '{new_col}'\n")
        f.write("\n")
        
        f.write("DATA TRANSFORMATIONS:\n")
        for col, transform in normalization_log['data_transformations'].items():
            f.write(f"  {col}: {transform['successful']} successful, {transform['failed']} failed\n")
        f.write("\n")
        
        f.write("VALIDATION RESULTS:\n")
        valid_count = audit_trail['data_quality_summary']['valid_records']
        invalid_count = audit_trail['data_quality_summary']['invalid_records']
        warning_count = audit_trail['data_quality_summary']['records_with_warnings']
        f.write(f"  Valid records: {valid_count}\n")
        f.write(f"  Invalid records: {invalid_count}\n")
        f.write(f"  Records with warnings: {warning_count}\n")
        
        if audit_trail['data_quality_summary']['issues_list']:
            f.write("\nISSUES FOUND:\n")
            for issue in audit_trail['data_quality_summary']['issues_list']:
                f.write(f"  • {issue}\n")
        
        if 'expense_statistics' in audit_trail:
            stats = audit_trail['expense_statistics']
            f.write("\nEXPENSE STATISTICS:\n")
            f.write(f"  Total expenses: ${stats['total_expenses']:,.2f}\n")
            f.write(f"  Average expense: ${stats['average_expense']:.2f}\n")
            f.write(f"  Expense range: ${stats['min_expense']:.2f} - ${stats['max_expense']:.2f}\n")
            f.write(f"  Total transactions: {stats['expense_count']}\n")
        
        if 'person_breakdown' in audit_trail:
            f.write("\nPERSON BREAKDOWN:\n")
            for person, count in audit_trail['person_breakdown'].items():
                f.write(f"  {person}: {count} records\n")
        
        if 'expense_type_breakdown' in audit_trail:
            f.write("\nEXPENSE TYPE BREAKDOWN:\n")
            for exp_type, count in audit_trail['expense_type_breakdown'].items():
                f.write(f"  {exp_type}: {count} records\n")
    
    print(f"   ✓ Summary saved to: {summary_file}")
    
    return audit_trail

def save_normalized_data(normalized_data):
    """Save the normalized data."""
    print("\n💾 SAVING NORMALIZED DATA")
    print("=" * 50)
    
    output_file = Path("data/processed/expense_history_normalized.csv")
    normalized_data.to_csv(output_file, index=False)
    
    print(f"   ✓ Normalized data saved to: {output_file}")
    print(f"   ✓ File size: {output_file.stat().st_size:,} bytes")
    print(f"   ✓ Records saved: {len(normalized_data)}")
    
    return output_file

def main():
    """Main normalization process."""
    print("💳 EXPENSE HISTORY NORMALIZATION")
    print("File 3 of 3 - Comprehensive expense validation and standardization")
    print("=" * 75)
    
    try:
        # Setup
        setup_output_directory()
        
        # Load raw data
        raw_data = load_raw_data()
        
        # Analyze structure
        analysis = analyze_raw_structure(raw_data)
        
        # Normalize data
        normalized_data, normalization_log = normalize_data(raw_data, analysis)
        
        # Generate audit trail
        audit_trail = generate_audit_trail(raw_data, normalized_data, analysis, normalization_log)
        
        # Save normalized data
        output_file = save_normalized_data(normalized_data)
        
        # Final summary
        print("\n🎯 NORMALIZATION COMPLETE")
        print("=" * 75)
        print("✅ Expense history data successfully normalized")
        print(f"📁 Normalized file: {output_file}")
        print("📋 Audit trail: output/audit_trails/")
        print(f"📊 Records processed: {len(raw_data)} -> {len(normalized_data)}")
        
        valid_records = audit_trail['data_quality_summary']['valid_records']
        invalid_records = audit_trail['data_quality_summary']['invalid_records']
        warning_records = audit_trail['data_quality_summary']['records_with_warnings']
        print(f"✅ Valid records: {valid_records}")
        if invalid_records > 0:
            print(f"⚠ Invalid records: {invalid_records}")
        if warning_records > 0:
            print(f"📝 Records with warnings: {warning_records}")
        
        if 'expense_statistics' in audit_trail:
            stats = audit_trail['expense_statistics']
            print(f"💰 Total expenses: ${stats['total_expenses']:,.2f}")
            print(f"📈 Average expense: ${stats['average_expense']:.2f}")
        
        if 'person_breakdown' in audit_trail:
            print("\n👥 EXPENSE BREAKDOWN BY PERSON:")
            for person, count in audit_trail['person_breakdown'].items():
                person_total = normalized_data[normalized_data['person_normalized'] == person]['actual_amount'].sum()
                print(f"   {person}: {count} transactions, ${person_total:,.2f}")
        
        print("\n🏁 ALL 3 FILES NORMALIZED!")
        print("=" * 75)
        print("📁 NORMALIZED FILES:")
        print("   1. data/processed/rent_allocation_normalized.csv")
        print("   2. data/processed/zelle_payments_normalized.csv")
        print("   3. data/processed/expense_history_normalized.csv")
        print("\n📋 AUDIT TRAILS:")
        print("   - output/audit_trails/ (JSON + human-readable summaries)")
        print("\n🔍 NEXT STEPS:")
        print("   1. Review all normalized files")
        print("   2. Check audit trails for any issues")
        print("   3. Proceed with reconciliation analysis")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during normalization: {e}")
        return False

if __name__ == "__main__":
    success = main()
