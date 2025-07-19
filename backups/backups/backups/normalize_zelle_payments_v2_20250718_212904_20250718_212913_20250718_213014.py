#!/usr/bin/env python3
"""
Zelle Payments Normalization - INDUSTRY STANDARDS COMPLIANT

This script properly normalizes Zelle payment data following data engineering best practices:
1. Schema validation and enforcement
2. Proper date normalization (ISO 8601)
3. Industry-standard column naming conventions
4. Data lineage and audit trail
5. Error handling and data quality validation
6. Payment validation business rules

FIXES APPLIED:
- Implements proper schema validation for payment data
- Validates payment authenticity (Zelle merchant, Transfer category, Jordyn reference)
- Follows naming conventions (snake_case, descriptive names)
- Implements comprehensive audit trail and data lineage
- Proper ISO 8601 date formatting
- Enhanced business rule validation for financial transfers

RUN FROM PROJECT ROOT: python normalize_zelle_payments_v2.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ZellePaymentSchema:
    """Defines the expected schema for Zelle payment data following industry standards."""
    
    # Source column mapping to standardized schema
    COLUMN_MAPPING = {
        'Date': 'transaction_date',  # ISO 8601 date of payment
        'Merchant': 'payment_processor',  # Should always be 'Zelle'
        'Category': 'transaction_category',  # Should always be 'Transfer'
        'Account': 'receiving_account_id',  # Destination account identifier
        'Original Statement': 'bank_statement_description',  # Bank's transaction description
        'Notes': 'transaction_notes',  # Additional notes (usually empty)
        'Amount': 'payment_amount_usd'  # Payment amount in USD
    }
    
    # Data types for each field
    FIELD_TYPES = {
        'transaction_date': 'date',
        'payment_processor': 'categorical',
        'transaction_category': 'categorical', 
        'receiving_account_id': 'text',
        'bank_statement_description': 'text',
        'transaction_notes': 'text',
        'payment_amount_usd': 'currency'
    }
    
    # Business rules for validation
    VALIDATION_RULES = {
        'required_processor': 'Zelle',
        'required_category': 'Transfer', 
        'required_sender_reference': 'JORDYN',  # Must contain sender name
        'minimum_amount': 0.01,  # Minimum valid payment
        'maximum_amount': 10000.00,  # Maximum reasonable payment
        'account_pattern': r'.*\(...\d{4}\)',  # Account format pattern
        'reference_pattern': r'REF #\s*\w+'  # Reference number pattern
    }

class ZellePaymentNormalizer:
    """Industry-standard Zelle payment data normalizer."""
    
    def __init__(self):
        self.schema = ZellePaymentSchema()
        self.raw_data = None
        self.normalized_data = None
        self.audit_log = {
            'processing_metadata': {},
            'schema_validation': {},
            'data_transformations': {},
            'business_rule_validation': {},
            'payment_authenticity_checks': {},
            'data_quality_metrics': {},
            'issues_identified': []
        }
    
    def load_raw_data(self, file_path: str) -> pd.DataFrame:
        """Load raw Zelle payment data with proper error handling."""
        print("💸 LOADING RAW ZELLE PAYMENT DATA")
        print("=" * 60)
        
        try:
            # Load with string type to preserve original formatting
            raw_df = pd.read_csv(file_path, dtype=str, encoding='utf-8')
            
            print(f"   ✓ Successfully loaded {len(raw_df)} payment records")
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
        """Validate that raw data matches expected Zelle payment schema."""
        print("\n🔍 VALIDATING ZELLE PAYMENT SCHEMA")
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
            print("   ✅ All required Zelle payment columns present")
        
        self.audit_log['schema_validation'] = validation_results
        return validation_results['column_mapping_valid']
    
    def normalize_transaction_dates(self, date_series: pd.Series) -> pd.Series:
        """Convert transaction dates to proper ISO 8601 format."""
        print("   📅 Normalizing transaction dates to ISO 8601 format")
        
        normalized_dates = []
        conversion_log = {'successful': 0, 'failed': 0, 'errors': []}
        
        for date_val in date_series:
            try:
                if pd.isna(date_val) or str(date_val).strip() == '':
                    normalized_dates.append(None)
                    conversion_log['failed'] += 1
                    continue
                
                # Parse using pandas with multiple format support
                parsed_date = pd.to_datetime(str(date_val).strip())
                iso_date = parsed_date.strftime('%Y-%m-%d')
                normalized_dates.append(iso_date)
                conversion_log['successful'] += 1
                
            except Exception as e:
                normalized_dates.append(None)
                conversion_log['failed'] += 1
                conversion_log['errors'].append({
                    'value': str(date_val),
                    'error': str(e)
                })
        
        print(f"     ✓ Successfully converted {conversion_log['successful']} dates")
        if conversion_log['failed'] > 0:
            print(f"     ⚠ Failed to convert {conversion_log['failed']} dates")
        
        self.audit_log['data_transformations']['transaction_dates'] = conversion_log
        return pd.Series(normalized_dates)
    
    def normalize_payment_amounts(self, amount_series: pd.Series) -> pd.Series:
        """Normalize payment amounts with proper currency handling."""
        print("   💰 Normalizing payment amounts")
        
        normalized_amounts = []
        conversion_log = {'successful': 0, 'failed': 0, 'errors': []}
        
        for amount in amount_series:
            try:
                if pd.isna(amount) or str(amount).strip() == '':
                    normalized_amounts.append(None)
                    conversion_log['failed'] += 1
                    continue
                
                amount_str = str(amount).strip()
                
                # Remove currency symbols, commas, and extra spaces
                cleaned = re.sub(r'[$,\s]', '', amount_str)
                
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
        
        self.audit_log['data_transformations']['payment_amounts'] = conversion_log
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
        
        # Transform transaction dates
        if 'transaction_date' in transformed_df.columns:
            transformed_df['transaction_date'] = self.normalize_transaction_dates(transformed_df['transaction_date'])
        
        # Transform payment amounts
        if 'payment_amount_usd' in transformed_df.columns:
            transformed_df['payment_amount_usd'] = self.normalize_payment_amounts(transformed_df['payment_amount_usd'])
        
        # Clean text fields
        text_fields = ['payment_processor', 'transaction_category', 'receiving_account_id', 
                      'bank_statement_description', 'transaction_notes']
        for field in text_fields:
            if field in transformed_df.columns:
                transformed_df[field] = transformed_df[field].astype(str).str.strip()
                transformed_df[field] = transformed_df[field].replace('nan', None)
        
        return transformed_df
    
    def validate_payment_authenticity(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate that payments are authentic Zelle transfers from Jordyn."""
        print("\n🔐 VALIDATING PAYMENT AUTHENTICITY")
        print("=" * 60)
        
        validation_results = {
            'total_payments': len(df),
            'authentic_payments': 0,
            'failed_validations': [],
            'validation_details': {}
        }
        
        authentic_count = 0
        
        for idx, row in df.iterrows():
            payment_id = f"payment_{idx+1:03d}"
            validation_detail = {
                'payment_id': payment_id,
                'is_authentic': True,
                'failed_checks': [],
                'validation_checks': {}
            }
            
            # Check 1: Payment processor must be Zelle
            processor = str(row.get('payment_processor', '')).strip().upper()
            validation_detail['validation_checks']['is_zelle_processor'] = processor == 'ZELLE'
            if processor != 'ZELLE':
                validation_detail['is_authentic'] = False
                validation_detail['failed_checks'].append(f'Invalid processor: {processor}')
            
            # Check 2: Category must be Transfer
            category = str(row.get('transaction_category', '')).strip().upper()
            validation_detail['validation_checks']['is_transfer_category'] = category == 'TRANSFER'
            if category != 'TRANSFER':
                validation_detail['is_authentic'] = False
                validation_detail['failed_checks'].append(f'Invalid category: {category}')
            
            # Check 3: Bank statement must contain Jordyn reference
            statement = str(row.get('bank_statement_description', '')).upper()
            has_jordyn = 'JORDYN' in statement
            validation_detail['validation_checks']['has_jordyn_reference'] = has_jordyn
            if not has_jordyn:
                validation_detail['is_authentic'] = False
                validation_detail['failed_checks'].append('Missing Jordyn reference in statement')
            
            # Check 4: Amount must be valid and reasonable
            amount = row.get('payment_amount_usd')
            valid_amount = (pd.notna(amount) and 
                          amount >= self.schema.VALIDATION_RULES['minimum_amount'] and
                          amount <= self.schema.VALIDATION_RULES['maximum_amount'])
            validation_detail['validation_checks']['has_valid_amount'] = valid_amount
            if not valid_amount:
                validation_detail['is_authentic'] = False
                validation_detail['failed_checks'].append(f'Invalid amount: {amount}')
            
            # Check 5: Account format validation
            account = str(row.get('receiving_account_id', ''))
            account_pattern = self.schema.VALIDATION_RULES['account_pattern']
            valid_account = re.search(account_pattern, account) is not None
            validation_detail['validation_checks']['has_valid_account_format'] = valid_account
            if not valid_account:
                validation_detail['is_authentic'] = False
                validation_detail['failed_checks'].append(f'Invalid account format: {account}')
            
            validation_results['validation_details'][payment_id] = validation_detail
            
            if validation_detail['is_authentic']:
                authentic_count += 1
            else:
                validation_results['failed_validations'].append({
                    'payment_id': payment_id,
                    'transaction_date': row.get('transaction_date'),
                    'amount': amount,
                    'failed_checks': validation_detail['failed_checks']
                })
        
        validation_results['authentic_payments'] = authentic_count
        validation_results['authenticity_rate'] = authentic_count / len(df) if len(df) > 0 else 0
        
        print(f"   ✅ Authentic payments: {authentic_count}/{len(df)} ({validation_results['authenticity_rate']:.1%})")
        if validation_results['failed_validations']:
            print(f"   ⚠ Failed authenticity checks: {len(validation_results['failed_validations'])}")
            for failure in validation_results['failed_validations']:
                print(f"     - {failure['payment_id']}: {', '.join(failure['failed_checks'])}")
        
        self.audit_log['payment_authenticity_checks'] = validation_results
        return validation_results
    
    def add_metadata_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add metadata fields following data lineage best practices."""
        print("\n📋 ADDING METADATA AND LINEAGE FIELDS")
        print("=" * 60)
        
        enhanced_df = df.copy()
        
        # Add data lineage fields
        enhanced_df['source_system'] = 'zelle_payment_csv'
        enhanced_df['source_file'] = 'Zelle_From_Jordyn_Final.csv'
        enhanced_df['processing_timestamp'] = datetime.now().isoformat()
        enhanced_df['data_version'] = '1.0'
        enhanced_df['normalization_method'] = 'industry_standard_v2'
        
        # Add payment identifiers and derived fields
        enhanced_df['payment_uuid'] = [f"zelle_pay_{i+1:04d}" for i in range(len(enhanced_df))]
        
        # Add fiscal period information
        enhanced_df['fiscal_year'] = pd.to_datetime(enhanced_df['transaction_date']).dt.year
        enhanced_df['fiscal_month'] = pd.to_datetime(enhanced_df['transaction_date']).dt.month
        enhanced_df['fiscal_quarter'] = pd.to_datetime(enhanced_df['transaction_date']).dt.quarter
        
        # Add payment classification
        enhanced_df['payment_type'] = 'zelle_transfer'
        enhanced_df['payment_direction'] = 'inbound'
        enhanced_df['sender_name'] = 'JORDYN_GINSBERG'  # Extracted from business rules
        
        print("   ✓ Added data lineage metadata")
        print("   ✓ Added payment identifiers and classification")
        print("   ✓ Added fiscal period fields")
        
        return enhanced_df
    
    def normalize(self, file_path: str) -> pd.DataFrame:
        """Execute complete normalization process following industry standards."""
        print("💸 ZELLE PAYMENT NORMALIZATION - INDUSTRY STANDARDS v2.0")
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
            
            # Step 5: Validate payment authenticity
            self.validate_payment_authenticity(transformed_df)
            
            # Step 6: Add metadata fields
            final_df = self.add_metadata_fields(transformed_df)
            
            self.normalized_data = final_df
            
            print("\n🎯 NORMALIZATION COMPLETE")
            print("=" * 80)
            print(f"✅ Successfully normalized {len(final_df)} payment records")
            print(f"📊 Schema: {len(final_df.columns)} standardized fields")
            print("📋 Audit trail: Complete payment validation captured")
            
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
            
            print("\n💾 NORMALIZED DATA SAVED")
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
            json_path = audit_dir / "zelle_payments_normalization_audit_v2.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=2, default=str)
            
            # Save human-readable summary
            summary_path = audit_dir / "zelle_payments_normalization_summary_v2.txt"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("ZELLE PAYMENTS NORMALIZATION AUDIT - INDUSTRY STANDARDS v2.0\n")
                f.write("=" * 80 + "\n\n")
                
                f.write(f"Processing Timestamp: {self.audit_log['processing_metadata'].get('load_timestamp')}\n")
                f.write(f"Source File: {self.audit_log['processing_metadata'].get('source_file')}\n")
                f.write("Normalization Method: industry_standard_v2\n\n")
                
                f.write("SCHEMA VALIDATION:\n")
                schema_val = self.audit_log['schema_validation']
                f.write(f"  Column mapping valid: {schema_val.get('column_mapping_valid')}\n")
                f.write(f"  Missing columns: {schema_val.get('missing_columns', [])}\n")
                f.write(f"  Extra columns: {schema_val.get('extra_columns', [])}\n\n")
                
                f.write("PAYMENT AUTHENTICITY VALIDATION:\n")
                auth_val = self.audit_log['payment_authenticity_checks']
                f.write(f"  Authentic payments: {auth_val.get('authentic_payments', 0)}/{auth_val.get('total_payments', 0)}\n")
                f.write(f"  Authenticity rate: {auth_val.get('authenticity_rate', 0):.1%}\n")
                f.write(f"  Failed validations: {len(auth_val.get('failed_validations', []))}\n\n")
                
                if auth_val.get('failed_validations'):
                    f.write("FAILED PAYMENT VALIDATIONS:\n")
                    for failure in auth_val['failed_validations']:
                        f.write(f"  {failure['payment_id']}: {', '.join(failure['failed_checks'])}\n")
            
            print("\n📋 AUDIT TRAIL SAVED")
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
        normalizer = ZellePaymentNormalizer()
        
        # Execute normalization
        normalized_df = normalizer.normalize("data/raw/Zelle_From_Jordyn_Final.csv")
        
        # Save results
        normalizer.save_normalized_data("data/processed/zelle_payments_normalized_v2.csv")
        normalizer.save_audit_trail("output/audit_trails")
        
        print("\n🏁 INDUSTRY-STANDARD ZELLE NORMALIZATION COMPLETE!")
        print("=" * 80)
        print("✅ Payments normalized following best practices")
        print("✅ Complete authenticity validation performed")
        print("✅ Business rules validated")
        print("✅ Data lineage documented")
        
        return True
        
    except Exception as e:
        print(f"\n💥 NORMALIZATION FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
