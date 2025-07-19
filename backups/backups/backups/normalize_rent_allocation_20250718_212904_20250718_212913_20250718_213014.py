#!/usr/bin/env python3
"""
Rent Allocation Normalization - File 1 of 3

This script normalizes the Consolidated_Rent_Allocation_20250527.csv file
with complete audit trail for review.

WHAT THIS DOES:
1. Loads raw rent allocation data
2. Analyzes structure and data quality
3. Normalizes column names and data types
4. Validates business logic (43%/57% split)
5. Generates detailed audit trail
6. Saves normalized data to data/processed/

RUN FROM PROJECT ROOT: python normalize_rent_allocation.py
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
    """Load the raw rent allocation CSV."""
    file_path = Path("data/raw/Consolidated_Rent_Allocation_20250527.csv")
    
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
            # Check if it looks like currency
            currency_pattern = r'^\$[\d,]+\.?\d*\s*$'
            is_currency = non_null_values.str.match(currency_pattern, na=False).any()
            
            # Check if it looks like date/month
            month_pattern = r'^[A-Za-z]{3}-\d{2}$'
            is_month = non_null_values.str.match(month_pattern, na=False).any()
            
            if is_currency:
                analysis['data_types'][col] = 'currency'
                print("   💰 Detected: Currency values")
            elif is_month:
                analysis['data_types'][col] = 'month'
                print("   📅 Detected: Month values")
            else:
                analysis['data_types'][col] = 'text'
                print("   📝 Detected: Text values")
    
    return analysis

def clean_currency_value(value):
    """Clean currency string to float."""
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
        print(f"   ⚠ Could not parse currency: '{value}'")
        return None

def normalize_data(raw_data, analysis):
    """Normalize the rent allocation data."""
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
        'Month': 'month',
        'Tax Base Rent': 'base_rent',
        'Tax Garage': 'garage_fee', 
        'Tax Trash': 'trash_fee',
        'Tax Courtesy': 'courtesy_fee',
        'Conservice': 'utility_fee',
        'Gross Total': 'gross_total',
        "Ryan's Rent (43%)": 'ryan_amount',
        "Jordyn's Rent (57%)": 'jordyn_amount'
    }
    
    # Apply column renaming
    actual_mapping = {}
    for old_col in normalized.columns:
        if old_col in column_mapping:
            new_col = column_mapping[old_col]
            actual_mapping[old_col] = new_col
            print(f"   '{old_col}' → '{new_col}'")
        else:
            # Fallback: clean the column name
            new_col = old_col.strip().lower().replace(' ', '_').replace('(', '').replace(')', '').replace('%', 'pct')
            actual_mapping[old_col] = new_col
            print(f"   '{old_col}' → '{new_col}' (auto-cleaned)")
    
    normalized = normalized.rename(columns=actual_mapping)
    normalization_log['column_mappings'] = actual_mapping
    
    # Step 2: Convert data types
    print("\n🔢 Step 2: Converting data types")
    
    # Identify currency columns
    currency_columns = []
    for col in normalized.columns:
        if col in ['base_rent', 'garage_fee', 'trash_fee', 'courtesy_fee', 'utility_fee', 'gross_total', 'ryan_amount', 'jordyn_amount']:
            currency_columns.append(col)
    
    # Convert currency columns
    for col in currency_columns:
        if col in normalized.columns:
            print(f"   Converting '{col}' to currency")
            original_values = normalized[col].copy()
            normalized[col] = normalized[col].apply(clean_currency_value)
            
            # Log transformation details
            successful_conversions = normalized[col].notna().sum()
            failed_conversions = len(original_values) - successful_conversions
            
            normalization_log['data_transformations'][col] = {
                'type': 'currency_conversion',
                'successful': successful_conversions,
                'failed': failed_conversions,
                'sample_before': str(original_values.iloc[0]) if len(original_values) > 0 else None,
                'sample_after': normalized[col].iloc[0] if len(normalized) > 0 else None
            }
            
            print(f"     ✓ Converted {successful_conversions} values")
            if failed_conversions > 0:
                print(f"     ⚠ Failed to convert {failed_conversions} values")
    
    # Step 3: Validate business logic
    print("\n✅ Step 3: Validating business logic")
    
    validation_results = validate_rent_split_logic(normalized)
    normalization_log['validation_results'] = validation_results
    
    for result in validation_results:
        if result['is_valid']:
            print(f"   ✓ {result['month']}: Split is correct")
        else:
            print(f"   ⚠ {result['month']}: Split error - {result['error']}")
            normalization_log['issues_found'].append(f"Rent split error in {result['month']}: {result['error']}")
    
    # Step 4: Add metadata
    print("\n📋 Step 4: Adding metadata")
    
    normalized['normalized_date'] = datetime.now().isoformat()
    normalized['data_source'] = 'Consolidated_Rent_Allocation_20250527.csv'
    normalized['record_id'] = range(1, len(normalized) + 1)
    
    print("   ✓ Added metadata columns")
    
    return normalized, normalization_log

def validate_rent_split_logic(data):
    """Validate that Ryan's amount + Jordyn's amount = Gross total."""
    validation_results = []
    
    for idx, row in data.iterrows():
        month = row.get('month', f'Row {idx}')
        gross_total = row.get('gross_total')
        ryan_amount = row.get('ryan_amount') 
        jordyn_amount = row.get('jordyn_amount')
        
        result = {
            'month': month,
            'gross_total': gross_total,
            'ryan_amount': ryan_amount,
            'jordyn_amount': jordyn_amount,
            'is_valid': True,
            'error': None
        }
        
        # Check if we have all the required values
        if pd.isna(gross_total) or pd.isna(ryan_amount) or pd.isna(jordyn_amount):
            result['is_valid'] = False
            result['error'] = 'Missing required values'
        else:
            # Check if the split adds up
            calculated_total = ryan_amount + jordyn_amount
            difference = abs(gross_total - calculated_total)
            
            # Allow for small rounding differences (2 cents)
            if difference > 0.02:
                result['is_valid'] = False
                result['error'] = f'Split doesn\'t add up: ${gross_total:.2f} != ${ryan_amount:.2f} + ${jordyn_amount:.2f} (diff: ${difference:.2f})'
            else:
                # Calculate percentages
                ryan_pct = (ryan_amount / gross_total * 100) if gross_total > 0 else 0
                jordyn_pct = (jordyn_amount / gross_total * 100) if gross_total > 0 else 0
                
                result['ryan_percentage'] = ryan_pct
                result['jordyn_percentage'] = jordyn_pct
        
        validation_results.append(result)
    
    return validation_results

def generate_audit_trail(raw_data, normalized_data, analysis, normalization_log):
    """Generate comprehensive audit trail."""
    print("\n📝 GENERATING AUDIT TRAIL")
    print("=" * 50)
    
    audit_trail = {
        'processing_metadata': {
            'processing_date': datetime.now().isoformat(),
            'source_file': 'data/raw/Consolidated_Rent_Allocation_20250527.csv',
            'processor': 'rent_allocation_normalizer.py',
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
    
    # Save audit trail
    audit_file = Path("output/audit_trails/rent_allocation_normalization_audit.json")
    with open(audit_file, 'w', encoding='utf-8') as f:
        json.dump(audit_trail, f, indent=2, default=str)
    
    print(f"   ✓ Audit trail saved to: {audit_file}")
    
    # Generate human-readable summary
    summary_file = Path("output/audit_trails/rent_allocation_normalization_summary.txt")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("RENT ALLOCATION NORMALIZATION SUMMARY\n")
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
        
        f.write("\nRENT SPLIT VALIDATION:\n")
        for result in normalization_log['validation_results']:
            if result['is_valid']:
                ryan_pct = result.get('ryan_percentage', 0)
                jordyn_pct = result.get('jordyn_percentage', 0)
                f.write(f"  {result['month']}: ✓ Ryan {ryan_pct:.1f}%, Jordyn {jordyn_pct:.1f}%\n")
            else:
                f.write(f"  {result['month']}: ✗ {result['error']}\n")
    
    print(f"   ✓ Summary saved to: {summary_file}")
    
    return audit_trail

def save_normalized_data(normalized_data):
    """Save the normalized data."""
    print("\n💾 SAVING NORMALIZED DATA")
    print("=" * 50)
    
    output_file = Path("data/processed/rent_allocation_normalized.csv")
    normalized_data.to_csv(output_file, index=False)
    
    print(f"   ✓ Normalized data saved to: {output_file}")
    print(f"   ✓ File size: {output_file.stat().st_size:,} bytes")
    print(f"   ✓ Records saved: {len(normalized_data)}")
    
    return output_file

def main():
    """Main normalization process."""
    print("🏠 RENT ALLOCATION NORMALIZATION")
    print("File 1 of 3 - Starting with simplest data")
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
        print("✅ Rent allocation data successfully normalized")
        print(f"📁 Normalized file: {output_file}")
        print("📋 Audit trail: output/audit_trails/")
        print(f"📊 Records processed: {len(raw_data)} → {len(normalized_data)}")
        
        valid_records = audit_trail['data_quality_summary']['valid_records']
        invalid_records = audit_trail['data_quality_summary']['invalid_records']
        print(f"✅ Valid records: {valid_records}")
        if invalid_records > 0:
            print(f"⚠ Invalid records: {invalid_records}")
        
        print("\n📋 NEXT STEPS:")
        print("1. Review normalized data in data/processed/rent_allocation_normalized.csv")
        print("2. Check audit trail in output/audit_trails/")
        print("3. Verify rent split calculations are correct")
        print("4. Proceed to File 2: Zelle payments normalization")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR during normalization: {e}")
        return False

if __name__ == "__main__":
    success = main()
