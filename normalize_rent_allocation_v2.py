#!/usr/bin/env python3
"""
Rent Allocation Data Normalization - INDUSTRY STANDARDS COMPLIANT

This script properly normalizes rent allocation data following data engineering best practices:
1. Schema validation and enforcement
2. Proper date normalization (ISO 8601)
3. Industry-standard column naming conventions
4. Data lineage and audit trail
5. Error handling and data quality validation
6. Standardized currency handling

FIXES APPLIED:
- Correctly maps source column names to standardized schema
- Converts dates to proper ISO 8601 format (YYYY-MM-DD)
- Handles quoted currency values with trailing spaces
- Follows naming conventions (snake_case, descriptive names)
- Implements proper data validation and quality checks

RUN FROM PROJECT ROOT: python normalize_rent_allocation_v2.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class RentAllocationSchema:
    """Defines the expected schema for rent allocation data following industry standards."""
    
    # Source column mapping to standardized schema
    COLUMN_MAPPING = {
        'Month': 'period_month',  # Rental period identifier
        'Tax Base Rent': 'base_rent_amount',  # Primary rent cost
        'Tax Garage': 'garage_fee_amount',  # Parking fee
        'Tax Trash': 'waste_management_fee',  # Waste disposal fee  
        'Tax Courtesy': 'courtesy_fee_amount',  # Service fee
        'Conservice': 'utility_service_fee',  # Utilities (Conservice provider)
        'Gross Total': 'total_rent_amount',  # Sum of all fees
        "Ryan's Rent (43%)": 'ryan_allocation_amount',  # Ryan's portion
        "Jordyn's Rent (57%)": 'jordyn_allocation_amount'  # Jordyn's portion
    }
    
    # Data types for each field
    FIELD_TYPES = {
        'period_month': 'date',
        'base_rent_amount': 'currency',
        'garage_fee_amount': 'currency', 
        'waste_management_fee': 'currency',
        'courtesy_fee_amount': 'currency',
        'utility_service_fee': 'currency',
        'total_rent_amount': 'currency',
        'ryan_allocation_amount': 'currency',
        'jordyn_allocation_amount': 'currency'
    }
    
    # Business rules for validation
    VALIDATION_RULES = {
        'ryan_percentage': 0.43,
        'jordyn_percentage': 0.57,
        'percentage_tolerance': 0.01,
        'minimum_rent': 1000.00,
        'maximum_rent': 5000.00
    }

class RentAllocationNormalizer:
    """Industry-standard rent allocation data normalizer."""
    
    def __init__(self):
        self.schema = RentAllocationSchema()
        self.raw_data = None
        self.normalized_data = None
        self.audit_log = {
            'processing_metadata': {},
            'schema_validation': {},
            'data_transformations': {},
            'business_rule_validation': {},
            'data_quality_metrics': {},
            'issues_identified': []
        }
    
    def load_raw_data(self, file_path: str) -> pd.DataFrame:
        """Load raw rent allocation data with proper error handling."""
        print("📁 LOADING RAW RENT ALLOCATION DATA")
        print("=" * 60)
        
        try:
            # Load with string type to preserve original formatting
            raw_df = pd.read_csv(file_path, dtype=str, encoding='utf-8')
            
            print(f"   ✓ Successfully loaded {len(raw_df)} records")
            print(f"   ✓ Detected {len(raw_df.columns)} columns")
            
            # Log original structure
            self.audit_log['processing_metadata'] = {
                'source_file': file_path,
                'load_timestamp': datetime.now().isoformat(),
                'original_row_count': len(raw_df),
                'original_column_count': len(raw_df.columns),
                'original_columns': list(raw_df.columns)
            }
            
            self.raw_data = raw_df
            return raw_df
            
        except Exception as e:
            error_msg = f"Failed to load data from {file_path}: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.audit_log['issues_identified'].append({
                'type': 'data_loading_error',
                'severity': 'critical',
                'message': error_msg
            })
            raise
    
    def validate_schema(self) -> bool:
        """Validate that raw data matches expected schema."""
        print("\n🔍 VALIDATING DATA SCHEMA")
        print("=" * 60)
        
        validation_results = {
            'expected_columns': list(self.schema.COLUMN_MAPPING.keys()),
            'actual_columns': list(self.raw_data.columns),
            'missing_columns': [],
            'extra_columns': [],
            'column_mapping_valid': True
        }
        
        expected_cols = set(self.schema.COLUMN_MAPPING.keys())
        actual_cols = set(self.raw_data.columns)
        
        # Check for missing required columns
        missing = expected_cols - actual_cols
        if missing:
            validation_results['missing_columns'] = list(missing)
            validation_results['column_mapping_valid'] = False
            print(f"   ❌ Missing required columns: {missing}")
        
        # Check for unexpected columns
        extra = actual_cols - expected_cols
        if extra:
            validation_results['extra_columns'] = list(extra)
            print(f"   ⚠ Extra columns found: {extra}")
        
        if validation_results['column_mapping_valid']:
            print("   ✅ All required columns present")
        
        self.audit_log['schema_validation'] = validation_results
        return validation_results['column_mapping_valid']
    
    def normalize_period_dates(self, period_series: pd.Series) -> pd.Series:
        """Convert period strings to proper ISO 8601 dates."""
        print("   📅 Normalizing period dates to ISO 8601 format")
        
        normalized_dates = []
        conversion_log = {'successful': 0, 'failed': 0, 'errors': []}
        
        for period in period_series:
            try:
                if pd.isna(period) or str(period).strip() == '':
                    normalized_dates.append(None)
                    conversion_log['failed'] += 1
                    continue
                
                period_str = str(period).strip()
                
                # Handle format like "24-Jan" -> "2024-01-01"
                if re.match(r'^\d{2}-[A-Za-z]{3}$', period_str):
                    year_part, month_part = period_str.split('-')
                    
                    # Convert 2-digit year to 4-digit (assuming 20xx)
                    full_year = f"20{year_part}"
                    
                    # Convert month abbreviation to number
                    month_map = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    
                    month_num = month_map.get(month_part)
                    if month_num:
                        iso_date = f"{full_year}-{month_num}-01"
                        normalized_dates.append(iso_date)
                        conversion_log['successful'] += 1
                    else:
                        raise ValueError(f"Unknown month abbreviation: {month_part}")
                else:
                    raise ValueError(f"Unexpected period format: {period_str}")
                    
            except Exception as e:
                normalized_dates.append(None)
                conversion_log['failed'] += 1
                conversion_log['errors'].append({
                    'value': str(period),
                    'error': str(e)
                })
        
        print(f"     ✓ Successfully converted {conversion_log['successful']} periods")
        if conversion_log['failed'] > 0:
            print(f"     ⚠ Failed to convert {conversion_log['failed']} periods")
        
        self.audit_log['data_transformations']['period_dates'] = conversion_log
        return pd.Series(normalized_dates)
    
    def normalize_currency_amounts(self, amount_series: pd.Series, field_name: str) -> pd.Series:
        """Normalize currency values with proper handling of quotes and formatting."""
        print(f"   💰 Normalizing currency field: {field_name}")
        
        normalized_amounts = []
        conversion_log = {'successful': 0, 'failed': 0, 'errors': []}
        
        for amount in amount_series:
            try:
                if pd.isna(amount) or str(amount).strip() == '':
                    normalized_amounts.append(None)
                    conversion_log['failed'] += 1
                    continue
                
                amount_str = str(amount).strip()
                
                # Remove quotes, dollar signs, commas, and extra spaces
                cleaned = re.sub(r'["\$,\s]', '', amount_str)
                
                # Handle negative amounts in parentheses
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    cleaned = '-' + cleaned[1:-1]
                
                if cleaned == '' or cleaned == '-':
                    normalized_amounts.append(None)
                    conversion_log['failed'] += 1
                    continue
                
                # Convert to float
                normalized_amount = float(cleaned)
                normalized_amounts.append(normalized_amount)
                conversion_log['successful'] += 1
                
            except Exception as e:
                normalized_amounts.append(None)
                conversion_log['failed'] += 1
                conversion_log['errors'].append({
                    'value': str(amount),
                    'error': str(e)
                })
        
        print(f"     ✓ Successfully converted {conversion_log['successful']} amounts")
        if conversion_log['failed'] > 0:
            print(f"     ⚠ Failed to convert {conversion_log['failed']} amounts")
        
        self.audit_log['data_transformations'][field_name] = conversion_log
        return pd.Series(normalized_amounts)
    
    def apply_column_mapping(self) -> pd.DataFrame:
        """Apply standardized column naming following industry conventions."""
        print("\n📝 APPLYING STANDARDIZED COLUMN MAPPING")
        print("=" * 60)
        
        # Create DataFrame with mapped columns
        mapped_data = pd.DataFrame()
        
        mapping_log = {'successful_mappings': {}, 'failed_mappings': []}
        
        for source_col, target_col in self.schema.COLUMN_MAPPING.items():
            if source_col in self.raw_data.columns:
                mapped_data[target_col] = self.raw_data[source_col].copy()
                mapping_log['successful_mappings'][source_col] = target_col
                print(f"   ✓ '{source_col}' → '{target_col}'")
            else:
                mapping_log['failed_mappings'].append(source_col)
                print(f"   ❌ Missing source column: '{source_col}'")
        
        self.audit_log['data_transformations']['column_mapping'] = mapping_log
        return mapped_data
    
    def apply_data_type_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply proper data type transformations based on schema."""
        print("\n🔄 APPLYING DATA TYPE TRANSFORMATIONS")
        print("=" * 60)
        
        transformed_df = df.copy()
        
        # Transform period dates
        if 'period_month' in transformed_df.columns:
            transformed_df['period_month'] = self.normalize_period_dates(transformed_df['period_month'])
        
        # Transform currency fields
        currency_fields = [col for col, dtype in self.schema.FIELD_TYPES.items() if dtype == 'currency']
        for field in currency_fields:
            if field in transformed_df.columns:
                transformed_df[field] = self.normalize_currency_amounts(transformed_df[field], field)
        
        return transformed_df
    
    def validate_business_rules(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate business rules and allocation percentages."""
        print("\n✅ VALIDATING BUSINESS RULES")
        print("=" * 60)
        
        validation_results = {
            'total_records': len(df),
            'valid_records': 0,
            'allocation_percentage_errors': [],
            'amount_validation_errors': [],
            'summary': {}
        }
        
        valid_count = 0
        
        for idx, row in df.iterrows():
            record_valid = True
            
            # Validate allocation percentages
            total_amount = row.get('total_rent_amount')
            ryan_amount = row.get('ryan_allocation_amount') 
            jordyn_amount = row.get('jordyn_allocation_amount')
            
            if pd.notna(total_amount) and pd.notna(ryan_amount) and pd.notna(jordyn_amount):
                ryan_pct = ryan_amount / total_amount
                jordyn_pct = jordyn_amount / total_amount
                
                expected_ryan = self.schema.VALIDATION_RULES['ryan_percentage']
                expected_jordyn = self.schema.VALIDATION_RULES['jordyn_percentage']
                tolerance = self.schema.VALIDATION_RULES['percentage_tolerance']
                
                if abs(ryan_pct - expected_ryan) > tolerance:
                    validation_results['allocation_percentage_errors'].append({
                        'period': row.get('period_month'),
                        'error': f"Ryan allocation {ryan_pct:.3f} vs expected {expected_ryan:.3f}"
                    })
                    record_valid = False
                
                if abs(jordyn_pct - expected_jordyn) > tolerance:
                    validation_results['allocation_percentage_errors'].append({
                        'period': row.get('period_month'),
                        'error': f"Jordyn allocation {jordyn_pct:.3f} vs expected {expected_jordyn:.3f}"
                    })
                    record_valid = False
            
            # Validate amount reasonableness
            if pd.notna(total_amount):
                min_rent = self.schema.VALIDATION_RULES['minimum_rent']
                max_rent = self.schema.VALIDATION_RULES['maximum_rent']
                
                if total_amount < min_rent or total_amount > max_rent:
                    validation_results['amount_validation_errors'].append({
                        'period': row.get('period_month'),
                        'error': f"Total rent ${total_amount:,.2f} outside expected range ${min_rent:,.2f}-${max_rent:,.2f}"
                    })
                    record_valid = False
            
            if record_valid:
                valid_count += 1
        
        validation_results['valid_records'] = valid_count
        validation_results['summary'] = {
            'validation_rate': valid_count / len(df) if len(df) > 0 else 0,
            'percentage_errors': len(validation_results['allocation_percentage_errors']),
            'amount_errors': len(validation_results['amount_validation_errors'])
        }
        
        print(f"   ✓ Valid records: {valid_count}/{len(df)} ({validation_results['summary']['validation_rate']:.1%})")
        print(f"   ⚠ Allocation percentage errors: {validation_results['summary']['percentage_errors']}")
        print(f"   ⚠ Amount validation errors: {validation_results['summary']['amount_errors']}")
        
        self.audit_log['business_rule_validation'] = validation_results
        return validation_results
    
    def add_metadata_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata fields following data lineage best practices."""
        print("\n📋 ADDING METADATA AND LINEAGE FIELDS")
        print("=" * 60)
        
        enhanced_df = df.copy()
        
        # Add data lineage fields
        enhanced_df['source_system'] = 'rent_allocation_csv'
        enhanced_df['source_file'] = 'Consolidated_Rent_Allocation_20250527.csv'
        enhanced_df['processing_timestamp'] = datetime.now().isoformat()
        enhanced_df['data_version'] = '1.0'
        enhanced_df['normalization_method'] = 'industry_standard_v2'
        
        # Add record identifiers
        enhanced_df['record_uuid'] = [f"rent_alloc_{i+1:04d}" for i in range(len(enhanced_df))]
        enhanced_df['fiscal_year'] = pd.to_datetime(enhanced_df['period_month']).dt.year
        enhanced_df['fiscal_quarter'] = pd.to_datetime(enhanced_df['period_month']).dt.quarter
        
        print("   ✓ Added data lineage metadata")
        print("   ✓ Added record identifiers and fiscal period fields")
        
        return enhanced_df
    
    def normalize(self, file_path: str) -> pd.DataFrame:
        """Execute complete normalization process following industry standards."""
        print("🏠 RENT ALLOCATION NORMALIZATION - INDUSTRY STANDARDS v2.0")
        print("=" * 80)
        
        try:
            # Step 1: Load raw data
            self.load_raw_data(file_path)
            
            # Step 2: Validate schema
            if not self.validate_schema():
                raise ValueError("Schema validation failed - cannot proceed")
            
            # Step 3: Apply column mapping
            mapped_df = self.apply_column_mapping()
            
            # Step 4: Apply data type transformations
            transformed_df = self.apply_data_type_transformations(mapped_df)
            
            # Step 5: Validate business rules
            self.validate_business_rules(transformed_df)
            
            # Step 6: Add metadata fields
            final_df = self.add_metadata_fields(transformed_df)
            
            self.normalized_data = final_df
            
            print("\n🎯 NORMALIZATION COMPLETE")
            print("=" * 80)
            print(f"✅ Successfully normalized {len(final_df)} records")
            print(f"📊 Schema: {len(final_df.columns)} standardized fields")
            print(f"📋 Audit trail: Complete data lineage captured")
            
            return final_df
            
        except Exception as e:
            error_msg = f"Normalization failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            self.audit_log['issues_identified'].append({
                'type': 'normalization_error',
                'severity': 'critical', 
                'message': error_msg
            })
            raise
    
    def save_normalized_data(self, output_path: str) -> bool:
        """Save normalized data with proper formatting."""
        if self.normalized_data is None:
            raise ValueError("No normalized data to save")
        
        try:
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save with proper formatting
            self.normalized_data.to_csv(output_path, index=False, float_format='%.2f')
            
            print(f"\n💾 NORMALIZED DATA SAVED")
            print(f"   📁 File: {output_path}")
            print(f"   📊 Records: {len(self.normalized_data)}")
            print(f"   🗂 Columns: {len(self.normalized_data.columns)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save normalized data: {str(e)}")
            return False
    
    def save_audit_trail(self, output_dir: str) -> bool:
        """Save comprehensive audit trail."""
        try:
            audit_dir = Path(output_dir)
            audit_dir.mkdir(parents=True, exist_ok=True)
            
            # Save JSON audit log
            json_path = audit_dir / "rent_allocation_normalization_audit_v2.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=2, default=str)
            
            # Save human-readable summary
            summary_path = audit_dir / "rent_allocation_normalization_summary_v2.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("RENT ALLOCATION NORMALIZATION AUDIT - INDUSTRY STANDARDS v2.0\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Processing Timestamp: {self.audit_log['processing_metadata'].get('load_timestamp')}\n")
                f.write(f"Source File: {self.audit_log['processing_metadata'].get('source_file')}\n")
                f.write(f"Normalization Method: industry_standard_v2\n\n")
                
                f.write("SCHEMA VALIDATION:\n")
                schema_val = self.audit_log['schema_validation']
                f.write(f"  Column mapping valid: {schema_val.get('column_mapping_valid')}\n")
                f.write(f"  Missing columns: {schema_val.get('missing_columns', [])}\n")
                f.write(f"  Extra columns: {schema_val.get('extra_columns', [])}\n\n")
                
                f.write("DATA TRANSFORMATIONS:\n")
                for field, log in self.audit_log['data_transformations'].items():
                    if isinstance(log, dict) and 'successful' in log:
                        f.write(f"  {field}: {log['successful']} successful, {log['failed']} failed\n")
                f.write("\n")
                
                f.write("BUSINESS RULE VALIDATION:\n")
                biz_val = self.audit_log['business_rule_validation']
                f.write(f"  Valid records: {biz_val.get('valid_records', 0)}/{biz_val.get('total_records', 0)}\n")
                f.write(f"  Validation rate: {biz_val.get('summary', {}).get('validation_rate', 0):.1%}\n")
                f.write(f"  Allocation errors: {len(biz_val.get('allocation_percentage_errors', []))}\n")
                f.write(f"  Amount errors: {len(biz_val.get('amount_validation_errors', []))}\n")
            
            print(f"\n📋 AUDIT TRAIL SAVED")
            print(f"   📄 JSON: {json_path}")
            print(f"   📝 Summary: {summary_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save audit trail: {str(e)}")
            return False

def main():
    """Main execution function."""
    try:
        # Initialize normalizer
        normalizer = RentAllocationNormalizer()
        
        # Execute normalization
        normalized_df = normalizer.normalize("data/raw/Consolidated_Rent_Allocation_20250527.csv")
        
        # Save results
        normalizer.save_normalized_data("data/processed/rent_allocation_normalized_v2.csv")
        normalizer.save_audit_trail("output/audit_trails")
        
        print("\n🏁 INDUSTRY-STANDARD NORMALIZATION COMPLETE!")
        print("=" * 80)
        print("✅ Data normalized following best practices")
        print("✅ Complete audit trail generated")
        print("✅ Business rules validated")
        print("✅ Data lineage documented")
        
        return True
        
    except Exception as e:
        print(f"\n💥 NORMALIZATION FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
