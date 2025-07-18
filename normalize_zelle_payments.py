#!/usr/bin/env python3
"""
Zelle Payments Normalization - File 2 of 3

This script normalizes the Zelle_From_Jordyn_Final.csv file
with complete audit trail for review.

WHAT THIS DOES:
1. Loads raw Zelle payment data
2. Analyzes structure and data quality
3. Normalizes column names and data types
4. Validates all payments are from Jordyn
5. Parses dates and currency amounts
6. Generates detailed audit trail
7. Saves normalized data to data/processed/

RUN FROM PROJECT ROOT: python normalize_zelle_payments.py
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
    """Load the raw Zelle payments CSV."""
    file_path = Path("data/raw/Zelle_From_Jordyn_Final.csv")
    
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
    
    # Analyze each column
    for col in raw_data.columns:
        print(f"\n📊 Column: '{col}'")
        
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
            amount_pattern = r'^\d+$'
            is_amount = non_null_values.str.match(amount_pattern, na=False).any()
            
            # Check if contains "ZELLE"
            has_zelle = non_null_values.str.contains('ZELLE', case=False, na=False).any()
            
            # Check if contains "JORDYN"
            has_jordyn = non_null_values.str.contains('JORDYN', case=False, na=False).any()
            
            if is_date:
                analysis['data_types'][col] = 'date'
                print("   📅 Detected: Date values")
            elif is_amount:
                analysis['data_types'][col] = 'amount'
                print("   💰 Detected: Amount values")
            elif has_zelle:
                analysis['data_types'][col] = 'zelle_reference'
                print("   🏦 Detected: Zelle reference")
            elif has_jordyn:
                analysis['data_types'][col] = 'jordyn_reference'
                print("   👤 Detected: Jordyn reference")
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
    """Normalize the Zelle payments data."""
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
    
    # Step 1: Standardize column names
    print("\n📝 Step 1: Standardizing column names")
    
    column_mapping = {
        'Date': 'date',
        'Merchant': 'merchant',
        'Category': 'category',
        'Account': 'account',
        'Original Statement': 'original_statement',
        'Notes': 'notes',
        'Amount': 'amount'
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
    
    # Convert amount column
    if 'amount' in normalized.columns:
        print("   Converting 'amount' to currency")
        original_values = normalized['amount'].copy()
        normalized['amount'] = normalized['amount'].apply(clean_currency_value)
        
        successful_conversions = normalized['amount'].notna().sum()
        failed_conversions = len(original_values) - successful_conversions
        
        normalization_log['data_transformations']['amount'] = {
            'type': 'currency_conversion',
            'successful': successful_conversions,
            'failed': failed_conversions,
            'sample_before': str(original_values.iloc[0]) if len(original_values) > 0 else None,
            'sample_after': normalized['amount'].iloc[0] if len(normalized) > 0 else None
        }
        
        print(f"     ✓ Converted {successful_conversions} amounts")
        if failed_conversions > 0:
            print(f"     ⚠ Failed to convert {failed_conversions} amounts")
    
    # Clean text fields
    text_fields = ['merchant', 'category', 'account', 'original_statement', 'notes']
    for field in text_fields:
        if field in normalized.columns:
            normalized[field] = normalized[field].astype(str).str.strip()
            normalized[field] = normalized[field].replace('nan', None)
    
    # Step 3: Validate business logic
    print("\n✅ Step 3: Validating business logic")
    
    validation_results = validate_zelle_logic(normalized)
    normalization_log['validation_results'] = validation_results
    
    # Report validation results
    valid_records = sum(1 for r in validation_results if r['is_valid'])
    invalid_records = len(validation_results) - valid_records
    
    print(f"   ✓ Valid Zelle records: {valid_records}")
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
    
    # Add metadata
    normalized['normalized_date'] = datetime.now().isoformat()
    normalized['data_source'] = 'Zelle_From_Jordyn_Final.csv'
    normalized['record_id'] = range(1, len(normalized) + 1)
    
    print("   ✓ Added calculated fields and metadata")
    
    return normalized, normalization_log

def validate_zelle_logic(data):
    """Validate that all records are legitimate Zelle transfers from Jordyn."""
    validation_results = []
    
    for idx, row in data.iterrows():
        result = {
            'record_id': idx + 1,
            'is_valid': True,
            'error': None,
            'checks': {}
        }
        
        # Check 1: Merchant should be "Zelle"
        merchant = str(row.get('merchant', '')).strip().upper()
        result['checks']['is_zelle_merchant'] = merchant == 'ZELLE'
        if merchant != 'ZELLE':
            result['is_valid'] = False
            result['error'] = f'Merchant is "{merchant}", expected "ZELLE"'
        
        # Check 2: Category should be "Transfer"
        category = str(row.get('category', '')).strip().upper()
        result['checks']['is_transfer_category'] = category == 'TRANSFER'
        if category != 'TRANSFER':
            result['is_valid'] = False
            result['error'] = f'Category is "{category}", expected "TRANSFER"'
        
        # Check 3: Original statement should contain "JORDYN"
        original_statement = str(row.get('original_statement', '')).upper()
        result['checks']['has_jordyn_reference'] = 'JORDYN' in original_statement
        if 'JORDYN' not in original_statement:
            result['is_valid'] = False
            result['error'] = 'Original statement does not contain "JORDYN"'
        
        # Check 4: Amount should be positive
        amount = row.get('amount')
        result['checks']['has_positive_amount'] = pd.notna(amount) and amount > 0
        if pd.isna(amount) or amount <= 0:
            result['is_valid'] = False
            result['error'] = f'Amount is not positive: {amount}'
        
        # Check 5: Date should be valid
        date_val = row.get('date')
        result['checks']['has_valid_date'] = pd.notna(date_val)
        if pd.isna(date_val):
            result['is_valid'] = False
            result['error'] = 'Date is missing or invalid'
        
        validation_results.append(result)
    
    return validation_results

def generate_audit_trail(raw_data, normalized_data, analysis, normalization_log):
    """Generate comprehensive audit trail."""
    print("\n📝 GENERATING AUDIT TRAIL")
    print("=" * 50)
    
    audit_trail = {
        'processing_metadata': {
            'processing_date': datetime.now().isoformat(),
            'source_file': 'data/raw/Zelle_From_Jordyn_Final.csv',
            'processor': 'zelle_payments_normalizer.py',
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
            'issues_count': len(normalization_log['issues_found']),
            'issues_list': normalization_log['issues_found']
        }
    }
    
    # Calculate payment statistics
    if 'amount' in normalized_data.columns:
        valid_amounts = normalized_data['amount'].dropna()
        if len(valid_amounts) > 0:
            audit_trail['payment_statistics'] = {
                'total_amount': float(valid_amounts.sum()),
                'average_payment': float(valid_amounts.mean()),
                'min_payment': float(valid_amounts.min()),
                'max_payment': float(valid_amounts.max()),
                'payment_count': len(valid_amounts)
            }
    
    # Save audit trail
    audit_file = Path("output/audit_trails/zelle_payments_normalization_audit.json")
    with open(audit_file, 'w', encoding='utf-8') as f:
        json.dump(audit_trail, f, indent=2, default=str)
    
    print(f"   ✓ Audit trail saved to: {audit_file}")
    
    # Generate human-readable summary
    summary_file = Path("output/audit_trails/zelle_payments_normalization_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("ZELLE PAYMENTS NORMALIZATION SUMMARY\n")
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
        f.write(f"  Valid records: {valid_count}\n")
        f.write(f"  Invalid records: {invalid_count}\n")
        
        if audit_trail['data_quality_summary']['issues_list']:
            f.write("\nISSUES FOUND:\n")
            for issue in audit_trail['data_quality_summary']['issues_list']:
                f.write(f"  • {issue}\n")
        
        if 'payment_statistics' in audit_trail:
            stats = audit_trail['payment_statistics']
            f.write(f"\nPAYMENT STATISTICS:\n")
            f.write(f"  Total amount: ${stats['total_amount']:,.2f}\n")
            f.write(f"  Average payment: ${stats['average_payment']:.2f}\n")
            f.write(f"  Payment range: ${stats['min_payment']:.2f} - ${stats['max_payment']:.2f}\n")
            f.write(f"  Total payments: {stats['payment_count']}\n")
    
    print(f"   ✓ Summary saved to: {summary_file}")
    
    return audit_trail

def save_normalized_data(normalized_data):
    """Save the normalized data."""
    print("\n💾 SAVING NORMALIZED DATA")
    print("=" * 50)
    
    output_file = Path("data/processed/zelle_payments_normalized.csv")
    normalized_data.to_csv(output_file, index=False)
    
    print(f"   ✓ Normalized data saved to: {output_file}")
    print(f"   ✓ File size: {output_file.stat().st_size:,} bytes")
    print(f"   ✓ Records saved: {len(normalized_data)}")
    
    return output_file

def main():
    """Main normalization process."""
    print("💸 ZELLE PAYMENTS NORMALIZATION")
    print("File 2 of 3 - Payment validation and standardization")
    print("=" * 60)
    
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
        print("=" * 60)
        print("✅ Zelle payments data successfully normalized")
        print(f"📁 Normalized file: {output_file}")
        print("📋 Audit trail: output/audit_trails/")
        print(f"📊 Records processed: {len(raw_data)} -> {len(normalized_data)}")
        
        valid_records = audit_trail['data_quality_summary']['valid_records']
        invalid_records = audit_trail['data_quality_summary']['invalid_records']
        print(f"✅ Valid records: {valid_records}")
        if invalid_records > 0:
            print(f"⚠ Invalid records: {invalid_records}")
        
        if 'payment_statistics' in audit_trail:
            stats = audit_trail['payment_statistics']
            print(f"💰 Total payments: ${stats['total_amount']:,.2f}")
            print(f"📈 Average payment: ${stats['average_payment']:.2f}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Review normalized data in data/processed/zelle_payments_normalized.csv")
        print("2. Check audit trail in output/audit_trails/")
        print("3. Verify all payments are from Jordyn")
        print("4. Proceed to File 3: Expense history normalization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during normalization: {e}")
        return False

if __name__ == "__main__":
    success = main()
