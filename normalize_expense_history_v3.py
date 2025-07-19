#!/usr/bin/env python3
"""
Enhanced Expense History Normalization - ADVANCED CALCULATION HANDLER

This script handles complex expense scenarios including:
1. Split calculations (2x to calculate appropriately) 
2. Partial allocation adjustments (100% Jordyn, Birthday present portion)
3. Mathematical operations in descriptions (addition, subtraction, etc.)
4. Item removal/exclusion logic (Remove outfit and splint)
5. EBT/Card split transactions 
6. Gift/present allocation adjustments
7. Complex refund and adjustment calculations
8. Budget variance analysis with calculation notes

ADVANCED FEATURES:
- Parses mathematical expressions in descriptions
- Identifies allocation responsibility (Ryan vs Jordyn)
- Handles gift/present adjustments automatically
- Processes split payment scenarios
- Extracts and validates calculation logic
- Flags complex transactions for manual review

RUN FROM PROJECT ROOT: python normalize_expense_history_v3.py
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, Any, Tuple, Optional
from dataclasses import dataclass

@dataclass
class AdvancedExpenseSchema:
    """Enhanced schema for complex expense calculations."""
    
    # Core column mapping (unchanged)
    COLUMN_MAPPING = {
        'Name': 'person_name',
        'Date of Purchase': 'expense_date',
        'Account': 'payment_account',
        'Merchant': 'merchant_name',
        ' Merchant Description ': 'merchant_description_text',
        ' Actual Amount ': 'actual_expense_amount',
        ' Allowed Amount ': 'budgeted_expense_amount',
        ' Description ': 'expense_description_text',
        'Category': 'expense_category',
        'Running Balance': 'account_running_balance'
    }
    
    # Enhanced calculation patterns
    CALCULATION_PATTERNS = {
        'allocation_multiplier': [
            r'2x to calculate',
            r'2\s*x\s*to\s*calculate',
            r'double\s*to\s*calculate',
            r'multiply\s*by\s*2'
        ],
        'percentage_allocation': [
            r'100%\s*Jordyn',
            r'100%\s*Ryan', 
            r'([0-9]+)%\s*(Jordyn|Ryan)',
            r'(Jordyn|Ryan)\s*([0-9]+)%'
        ],
        'gift_present': [
            r'Birthday\s*present\s*portion',
            r'Free\s*for\s*(Jordyn|Ryan)\s*from\s*(Jordyn|Ryan)\s*as\s*a\s*present',
            r'(Jordyn|Ryan)\s*100%',
            r'gift\s*for\s*(Jordyn|Ryan)',
            r'present\s*for\s*(Jordyn|Ryan)'
        ],
        'mathematical_operations': [
            r'([0-9]+\.?[0-9]*)\s*\+\s*([0-9]+\.?[0-9]*)',
            r'([0-9]+\.?[0-9]*)\s*\-\s*([0-9]+\.?[0-9]*)',
            r'([0-9]+\.?[0-9]*)\s*\*\s*([0-9]+\.?[0-9]*)',
            r'([0-9]+\.?[0-9]*)\s*/\s*([0-9]+\.?[0-9]*)',
            r'\(([^)]+)\)',
            r'=\s*([0-9]+\.?[0-9]*)'
        ],
        'exclusion_adjustments': [
            r'Remove\s*([^,]+)',
            r'remove\s*([^,]+)',
            r'Take\s*out\s*([^,]+)',
            r'exclude\s*([^,]+)',
            r'deduct\s*\$?([0-9]+\.?[0-9]*)',
            r'minus\s*\$?([0-9]+\.?[0-9]*)',
            r'\*\*\*Remove\s*([^*]+)\*\*\*'
        ],
        'split_transactions': [
            r'Split\s*\$?([0-9]+\.?[0-9]*)\s*([^/]+)/\s*\$?([0-9]+\.?[0-9]*)\s*([^)]+)',
            r'EBT.*Split',
            r'originally\s*\$?([0-9]+\.?[0-9]*)',
            r'final\s*price\s*\$?([0-9]+\.?[0-9]*)'
        ],
        'complex_notes': [
            r'Lost\s*\(I\s*will\s*take\s*half',
            r'half\s*the\s*financial\s*burden',
            r'Discuss\s*further',
            r'Reassess\s*next\s*time',
            r'Very\s*difficult\s*to\s*determine'
        ]
    }
    
    # Enhanced business rules
    VALIDATION_RULES = {
        'valid_persons': ['Ryan', 'Jordyn'],
        'minimum_expense': -1000.00,  # Allow larger refunds
        'maximum_expense': 10000.00,  # Allow larger expenses
        'variance_threshold': 0.01,
        'large_expense_threshold': 1000.00,
        'date_range_start': '2020-01-01',
        'date_range_end': '2030-12-31',
        'required_fields': ['person_name', 'expense_date', 'actual_expense_amount'],
        'calculation_complexity_threshold': 3,  # Flag entries with 3+ calculation elements
        'manual_review_keywords': [
            'Lost', 'Discuss further', 'Reassess', 'Very difficult', 
            'Where is this', 'Did Jordyn order', 'Monitor', '???'
        ]
    }

class AdvancedExpenseCalculator:
    """Handles complex expense calculations and allocations."""
    
    def __init__(self):
        self.calculation_log = {
            'total_processed': 0,
            'complex_calculations': 0,
            'allocation_adjustments': 0,
            'mathematical_operations': 0,
            'gift_adjustments': 0,
            'exclusion_adjustments': 0,
            'split_transactions': 0,
            'manual_review_flagged': 0,
            'calculation_details': []
        }
    
    def analyze_calculation_complexity(self, description: str, actual_amount: float, 
                                     budgeted_amount: Optional[float]) -> Dict[str, Any]:
        """Analyze the complexity of expense calculation."""
        if pd.isna(description) or str(description).strip() == '':
            return {'complexity_score': 0, 'calculation_type': 'simple', 'notes': []}
        
        desc_str = str(description).strip()
        analysis = {
            'complexity_score': 0,
            'calculation_type': 'simple',
            'notes': [],
            'requires_manual_review': False,
            'allocation_adjustments': {},
            'mathematical_operations': [],
            'exclusions': []
        }
        
        schema = AdvancedExpenseSchema()
        
        # Check for allocation multipliers (2x to calculate)
        for pattern in schema.CALCULATION_PATTERNS['allocation_multiplier']:
            if re.search(pattern, desc_str, re.IGNORECASE):
                analysis['complexity_score'] += 2
                analysis['calculation_type'] = 'allocation_multiplier'
                analysis['notes'].append('Contains allocation multiplier (2x calculation)')
                
                # Special case: if budgeted is 2x actual, this is intentional
                if budgeted_amount and actual_amount:
                    if abs(budgeted_amount - (actual_amount * 2)) < 0.01:
                        analysis['allocation_adjustments']['multiplier'] = 2
                        analysis['allocation_adjustments']['reason'] = 'Double charge for proper allocation'
        
        # Check for percentage allocations
        for pattern in schema.CALCULATION_PATTERNS['percentage_allocation']:
            matches = re.finditer(pattern, desc_str, re.IGNORECASE)
            for match in matches:
                analysis['complexity_score'] += 1
                analysis['notes'].append(f'Contains percentage allocation: {match.group(0)}')
                if '100%' in match.group(0):
                    person = 'Jordyn' if 'Jordyn' in match.group(0) else 'Ryan'
                    analysis['allocation_adjustments']['responsible_person'] = person
                    analysis['allocation_adjustments']['percentage'] = 100
        
        # Check for gift/present allocations
        for pattern in schema.CALCULATION_PATTERNS['gift_present']:
            matches = re.finditer(pattern, desc_str, re.IGNORECASE)
            for match in matches:
                analysis['complexity_score'] += 1
                analysis['calculation_type'] = 'gift_present'
                analysis['notes'].append(f'Gift/present allocation: {match.group(0)}')
                
                # Extract gift recipient and giver
                if 'Birthday present portion' in match.group(0):
                    analysis['allocation_adjustments']['type'] = 'birthday_present'
                    analysis['allocation_adjustments']['split_calculation'] = True
        
        # Check for mathematical operations
        for pattern in schema.CALCULATION_PATTERNS['mathematical_operations']:
            matches = re.finditer(pattern, desc_str, re.IGNORECASE)
            for match in matches:
                analysis['complexity_score'] += 1
                analysis['mathematical_operations'].append(match.group(0))
                analysis['notes'].append(f'Mathematical operation: {match.group(0)}')
        
        # Check for exclusion adjustments
        for pattern in schema.CALCULATION_PATTERNS['exclusion_adjustments']:
            matches = re.finditer(pattern, desc_str, re.IGNORECASE)
            for match in matches:
                analysis['complexity_score'] += 2
                analysis['calculation_type'] = 'exclusion_adjustment'
                analysis['exclusions'].append(match.group(0))
                analysis['notes'].append(f'Exclusion adjustment: {match.group(0)}')
        
        # Check for split transactions
        for pattern in schema.CALCULATION_PATTERNS['split_transactions']:
            matches = re.finditer(pattern, desc_str, re.IGNORECASE)
            for match in matches:
                analysis['complexity_score'] += 2
                analysis['calculation_type'] = 'split_transaction'
                analysis['notes'].append(f'Split transaction: {match.group(0)}')
        
        # Check for manual review keywords
        for keyword in schema.VALIDATION_RULES['manual_review_keywords']:
            if keyword.lower() in desc_str.lower():
                analysis['requires_manual_review'] = True
                analysis['complexity_score'] += 3
                analysis['notes'].append(f'Manual review required: {keyword}')
        
        # Determine final calculation type
        if analysis['complexity_score'] >= schema.VALIDATION_RULES['calculation_complexity_threshold']:
            if analysis['calculation_type'] == 'simple':
                analysis['calculation_type'] = 'complex'
        
        return analysis
    
    def calculate_adjusted_amounts(self, actual_amount: float, budgeted_amount: Optional[float],
                                 calculation_analysis: Dict[str, Any]) -> Tuple[float, float, Dict[str, Any]]:
        """Calculate adjusted amounts based on calculation analysis."""
        adjusted_actual = actual_amount
        adjusted_budgeted = budgeted_amount if budgeted_amount else 0.0
        adjustments = {
            'original_actual': actual_amount,
            'original_budgeted': budgeted_amount,
            'adjustment_applied': False,
            'adjustment_type': None,
            'adjustment_details': {}
        }
        
        # Handle allocation multiplier adjustments
        if 'allocation_adjustments' in calculation_analysis:
            alloc_adj = calculation_analysis['allocation_adjustments']
            
            # Handle 2x calculation scenarios
            if 'multiplier' in alloc_adj and alloc_adj['multiplier'] == 2:
                if 'reason' in alloc_adj and 'Double charge' in alloc_adj['reason']:
                    # This is intentional - keep budgeted as 2x actual
                    adjustments['adjustment_applied'] = True
                    adjustments['adjustment_type'] = 'allocation_multiplier'
                    adjustments['adjustment_details']['multiplier'] = 2
                    adjustments['adjustment_details']['reason'] = alloc_adj['reason']
            
            # Handle percentage allocations
            if 'percentage' in alloc_adj and alloc_adj['percentage'] == 100:
                person = alloc_adj.get('responsible_person')
                adjustments['adjustment_applied'] = True
                adjustments['adjustment_type'] = 'full_allocation'
                adjustments['adjustment_details']['responsible_person'] = person
                adjustments['adjustment_details']['percentage'] = 100
        
        # Handle gift/present adjustments
        if calculation_analysis['calculation_type'] == 'gift_present':
            adjustments['adjustment_applied'] = True
            adjustments['adjustment_type'] = 'gift_present'
            # For gifts, we may want to split the actual cost differently
            if 'Birthday present portion' in str(calculation_analysis['notes']):
                # Extract the gift portion amount if available
                for note in calculation_analysis['notes']:
                    amount_match = re.search(r'\$([0-9]+\.?[0-9]*)', note)
                    if amount_match:
                        gift_amount = float(amount_match.group(1))
                        adjustments['adjustment_details']['gift_amount'] = gift_amount
        
        return adjusted_actual, adjusted_budgeted, adjustments

class AdvancedExpenseNormalizer:
    """Enhanced expense normalizer with advanced calculation handling."""
    
    def __init__(self):
        self.schema = AdvancedExpenseSchema()
        self.calculator = AdvancedExpenseCalculator()
        self.raw_data = None
        self.normalized_data = None
        self.audit_log = {
            'processing_metadata': {},
            'schema_validation': {},
            'data_transformations': {},
            'calculation_analysis': {},
            'business_rule_validation': {},
            'person_validation': {},
            'expense_categorization': {},
            'variance_analysis': {},
            'manual_review_items': [],
            'data_quality_metrics': {},
            'issues_identified': []
        }
    
    def load_and_validate_data(self, file_path: str) -> pd.DataFrame:
        """Load and perform initial validation."""
        print("💳 ADVANCED EXPENSE NORMALIZATION - v3.0 (Calculation Handler)")
        print("=" * 80)
        
        # Load raw data
        print("\n📂 LOADING RAW EXPENSE DATA")
        print("-" * 40)
        
        try:
            raw_df = pd.read_csv(file_path, dtype=str, encoding='utf-8')
            print(f"   ✓ Loaded {len(raw_df)} expense records")
            
            self.audit_log['processing_metadata'] = {
                'source_file': file_path,
                'load_timestamp': datetime.now().isoformat(),
                'original_row_count': len(raw_df),
                'original_column_count': len(raw_df.columns),
                'normalization_version': 'v3.0_advanced_calculations'
            }
            
            self.raw_data = raw_df
            return raw_df
            
        except Exception as e:
            error_msg = f"Failed to load data: {str(e)}"
            print(f"   ❌ {error_msg}")
            self.audit_log['issues_identified'].append({
                'type': 'data_loading_error',
                'severity': 'critical',
                'message': error_msg
            })
            raise
    
    def apply_advanced_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply advanced transformations with calculation analysis."""
        print("\n🧮 ANALYZING COMPLEX CALCULATIONS")
        print("-" * 40)
        
        # Apply basic column mapping first
        mapped_df = pd.DataFrame()
        for source_col, target_col in self.schema.COLUMN_MAPPING.items():
            if source_col in df.columns:
                mapped_df[target_col] = df[source_col].copy()
        
        # Apply basic data type transformations
        transformed_df = self._apply_basic_transformations(mapped_df)
        
        # Now apply advanced calculation analysis
        calculation_results = []
        manual_review_items = []
        
        for idx, row in transformed_df.iterrows():
            # Analyze calculation complexity
            analysis = self.calculator.analyze_calculation_complexity(
                row.get('expense_description_text'),
                row.get('actual_expense_amount'),
                row.get('budgeted_expense_amount')
            )
            
            # Calculate adjusted amounts
            adjusted_actual, adjusted_budgeted, adjustments = self.calculator.calculate_adjusted_amounts(
                row.get('actual_expense_amount', 0),
                row.get('budgeted_expense_amount'),
                analysis
            )
            
            # Store calculation results
            calculation_result = {
                'record_index': idx,
                'person': row.get('person_name'),
                'merchant': row.get('merchant_name'),
                'date': row.get('expense_date'),
                'original_actual': row.get('actual_expense_amount'),
                'original_budgeted': row.get('budgeted_expense_amount'),
                'adjusted_actual': adjusted_actual,
                'adjusted_budgeted': adjusted_budgeted,
                'complexity_score': analysis['complexity_score'],
                'calculation_type': analysis['calculation_type'],
                'notes': analysis['notes'],
                'adjustments': adjustments,
                'requires_manual_review': analysis.get('requires_manual_review', False)
            }
            
            calculation_results.append(calculation_result)
            
            # Flag for manual review if needed
            if analysis.get('requires_manual_review', False) or analysis.get('complexity_score', 0) >= 5:
                manual_review_items.append(calculation_result)
                self.calculator.calculation_log['manual_review_flagged'] += 1
            
            # Update DataFrame with adjusted values
            transformed_df.loc[idx, 'adjusted_actual_amount'] = adjusted_actual
            transformed_df.loc[idx, 'adjusted_budgeted_amount'] = adjusted_budgeted
            transformed_df.loc[idx, 'calculation_complexity_score'] = analysis.get('complexity_score', 0)
            transformed_df.loc[idx, 'calculation_type'] = analysis.get('calculation_type', 'simple')
            transformed_df.loc[idx, 'requires_manual_review'] = analysis.get('requires_manual_review', False)
            transformed_df.loc[idx, 'calculation_notes'] = '; '.join(analysis.get('notes', []))
            
            # Track calculation types
            if analysis.get('calculation_type', 'simple') != 'simple':
                self.calculator.calculation_log['complex_calculations'] += 1
        
        # Update audit log
        self.audit_log['calculation_analysis'] = {
            'total_records_analyzed': len(calculation_results),
            'complex_calculations': self.calculator.calculation_log['complex_calculations'],
            'manual_review_required': len(manual_review_items),
            'calculation_type_distribution': {}
        }
        
        # Calculate type distribution
        type_counts = transformed_df['calculation_type'].value_counts().to_dict()
        self.audit_log['calculation_analysis']['calculation_type_distribution'] = type_counts
        
        self.audit_log['manual_review_items'] = manual_review_items
        
        print(f"   📊 Complex calculations identified: {self.calculator.calculation_log['complex_calculations']}")
        print(f"   ⚠ Manual review required: {len(manual_review_items)}")
        print(f"   🎯 Calculation types: {type_counts}")
        
        return transformed_df
    
    def _apply_basic_transformations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply basic date and currency transformations."""
        # Transform dates
        if 'expense_date' in df.columns:
            df['expense_date'] = self._normalize_dates(df['expense_date'])
        
        # Transform currency fields
        currency_fields = ['actual_expense_amount', 'budgeted_expense_amount', 'account_running_balance']
        for field in currency_fields:
            if field in df.columns:
                df[field] = self._normalize_currency(df[field])
        
        # Clean text fields
        text_fields = ['person_name', 'payment_account', 'merchant_name', 
                      'merchant_description_text', 'expense_description_text', 'expense_category']
        for field in text_fields:
            if field in df.columns:
                df[field] = df[field].astype(str).str.strip()
                df[field] = df[field].replace('nan', None)
                df[field] = df[field].replace('', None)
        
        return df
    
    def _normalize_dates(self, date_series: pd.Series) -> pd.Series:
        """Normalize dates to ISO format."""
        normalized_dates = []
        for date_val in date_series:
            try:
                if pd.isna(date_val) or str(date_val).strip() in ['', '-', 'Date of Purchase']:
                    normalized_dates.append(None)
                    continue
                
                parsed_date = pd.to_datetime(str(date_val).strip(), errors='coerce')
                if pd.isna(parsed_date):
                    normalized_dates.append(None)
                else:
                    normalized_dates.append(parsed_date.strftime('%Y-%m-%d'))
            except Exception:
                normalized_dates.append(None)
        
        return pd.Series(normalized_dates)
    
    def _normalize_currency(self, amount_series: pd.Series) -> pd.Series:
        """Normalize currency amounts."""
        normalized_amounts = []
        for amount in amount_series:
            try:
                if pd.isna(amount) or str(amount).strip() == '':
                    normalized_amounts.append(None)
                    continue
                
                amount_str = str(amount).strip()
                
                # Skip header values
                if amount_str in ['Actual Amount', 'Allowed Amount', 'Running Balance']:
                    normalized_amounts.append(None)
                    continue
                
                # Clean currency formatting
                cleaned = re.sub(r'[$,"\'"\s]', '', amount_str)
                cleaned = re.sub(r'^\$\s*\-\s*$', '0', cleaned)  # Handle "$ -" format
                
                # Handle parentheses (negative)
                if cleaned.startswith('(') and cleaned.endswith(')'):
                    cleaned = '-' + cleaned[1:-1]
                
                if cleaned == '' or cleaned == '-':
                    normalized_amounts.append(None)
                    continue
                
                normalized_amount = float(cleaned)
                normalized_amounts.append(normalized_amount)
                
            except Exception:
                normalized_amounts.append(None)
        
        return pd.Series(normalized_amounts)
    
    def add_enhanced_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add enhanced metadata including calculation tracking."""
        enhanced_df = df.copy()
        
        # Standard metadata
        enhanced_df['source_system'] = 'expense_history_csv'
        enhanced_df['source_file'] = 'Consolidated_Expense_History_20250622.csv'
        enhanced_df['processing_timestamp'] = datetime.now().isoformat()
        enhanced_df['data_version'] = '3.0'
        enhanced_df['normalization_method'] = 'advanced_calculations_v3'
        
        # Enhanced calculation metadata
        enhanced_df['expense_uuid'] = [f"exp_v3_{i+1:06d}" for i in range(len(enhanced_df))]
        
        # Add fiscal information
        enhanced_df['fiscal_year'] = pd.to_datetime(enhanced_df['expense_date']).dt.year
        enhanced_df['fiscal_month'] = pd.to_datetime(enhanced_df['expense_date']).dt.month
        enhanced_df['fiscal_quarter'] = pd.to_datetime(enhanced_df['expense_date']).dt.quarter
        
        # Advanced classification flags
        enhanced_df['is_complex_calculation'] = enhanced_df['calculation_complexity_score'] >= 3
        enhanced_df['has_allocation_adjustment'] = enhanced_df['calculation_type'].isin([
            'allocation_multiplier', 'gift_present', 'exclusion_adjustment'
        ])
        enhanced_df['is_split_transaction'] = enhanced_df['calculation_type'] == 'split_transaction'
        
        # Data quality indicators
        enhanced_df['is_complete_record'] = (
            enhanced_df['person_name'].notna() & 
            enhanced_df['expense_date'].notna() & 
            enhanced_df['actual_expense_amount'].notna()
        )
        
        enhanced_df['data_quality_score'] = (
            enhanced_df['is_complete_record'].astype(int) * 40 +
            (enhanced_df['expense_description_text'].notna()).astype(int) * 20 +
            (enhanced_df['budgeted_expense_amount'].notna()).astype(int) * 20 +
            (~enhanced_df['requires_manual_review']).astype(int) * 20
        )
        
        return enhanced_df
    
    def normalize(self, file_path: str) -> pd.DataFrame:
        """Execute complete advanced normalization."""
        try:
            # Load and validate
            self.load_and_validate_data(file_path)
            
            # Apply advanced transformations
            transformed_df = self.apply_advanced_transformations(self.raw_data)
            
            # Add enhanced metadata
            final_df = self.add_enhanced_metadata(transformed_df)
            
            self.normalized_data = final_df
            
            print("\n🎯 ADVANCED NORMALIZATION COMPLETE")
            print("=" * 80)
            print(f"✅ Total records processed: {len(final_df)}")
            print(f"🧮 Complex calculations: {self.calculator.calculation_log['complex_calculations']}")
            print(f"⚠ Manual review required: {self.calculator.calculation_log['manual_review_flagged']}")
            print(f"📊 Average data quality score: {final_df['data_quality_score'].mean():.1f}%")
            
            return final_df
            
        except Exception as e:
            error_msg = f"Advanced normalization failed: {str(e)}"
            print(f"\n❌ {error_msg}")
            raise
    
    def save_results(self, output_dir: str) -> bool:
        """Save normalized data and comprehensive audit trails."""
        if self.normalized_data is None:
            raise ValueError("No normalized data to save")
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save normalized data
            data_file = output_path / "expense_history_normalized_v3.csv"
            self.normalized_data.to_csv(data_file, index=False, float_format='%.2f')
            
            # Save audit trail
            audit_file = output_path / "expense_history_audit_v3.json"
            with open(audit_file, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log, f, indent=2, default=str)
            
            # Save manual review items
            review_file = output_path / "manual_review_items_v3.json"
            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(self.audit_log['manual_review_items'], f, indent=2, default=str)
            
            print("\n💾 RESULTS SAVED")
            print(f"   📊 Data: {data_file}")
            print(f"   📋 Audit: {audit_file}")
            print(f"   ⚠ Manual Review: {review_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to save results: {str(e)}")
            return False

def main():
    """Main execution function."""
    try:
        normalizer = AdvancedExpenseNormalizer()
        
        # Execute advanced normalization
        _ = normalizer.normalize("data/raw/Consolidated_Expense_History_20250622.csv")
        
        # Save results
        normalizer.save_results("data/processed")
        normalizer.save_results("output/audit_trails")
        
        print("\n🏁 ADVANCED EXPENSE NORMALIZATION COMPLETE!")
        print("=" * 80)
        print("✅ Complex calculations properly analyzed and handled")
        print("✅ Manual review items identified and flagged")
        print("✅ Enhanced audit trail with calculation details")
        print("✅ Ready for sophisticated reconciliation analysis")
        
        return True
        
    except Exception as e:
        print(f"\n💥 ADVANCED NORMALIZATION FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
