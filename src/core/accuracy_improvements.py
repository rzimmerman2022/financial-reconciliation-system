"""
Accuracy Improvements for Financial Reconciliation System
=========================================================

This module contains critical accuracy improvements to ensure the most accurate
reconciliation possible for a one-time run.

Key improvements:
1. Enhanced duplicate detection
2. Robust date and amount parsing
3. Improved description pattern matching
4. Better validation and error handling
5. Manual review decision preservation
"""

from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta
import pandas as pd
import hashlib
import re
import logging
from typing import Optional, Dict, Any, List, Tuple
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class AccuracyValidator:
    """Validates and improves accuracy of financial data processing."""
    
    def __init__(self):
        self.validation_errors = []
        self.warnings = []
        
    def create_robust_transaction_hash(self, date: datetime, amount: Decimal, 
                                      description: str, payer: str) -> str:
        """
        Create a more robust hash for duplicate detection.
        
        Improvements:
        - Uses full description (not just first 20 chars)
        - Normalizes description to catch variations
        - Includes payer in hash
        - Uses consistent date format
        """
        # Normalize description for better duplicate detection
        desc_normalized = self._normalize_description(description)
        
        # Create hash with all relevant fields
        hash_input = f"{date.date()}|{amount:.2f}|{desc_normalized}|{payer.lower()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def _normalize_description(self, description: str) -> str:
        """Normalize description for better matching."""
        if not description:
            return ""
        
        # Convert to lowercase and strip
        desc = description.lower().strip()
        
        # Remove common variations
        desc = re.sub(r'\s+', ' ', desc)  # Multiple spaces to single
        desc = re.sub(r'[^\w\s$]', '', desc)  # Remove special chars except $
        desc = re.sub(r'\b(the|a|an)\b', '', desc)  # Remove articles
        
        return desc.strip()
    
    def find_similar_transactions(self, transactions: pd.DataFrame, 
                                 threshold: float = 0.85) -> List[Tuple[int, int, float]]:
        """
        Find similar transactions that might be duplicates.
        
        Returns list of (index1, index2, similarity_score) tuples.
        """
        similar_pairs = []
        
        for i in range(len(transactions)):
            for j in range(i + 1, len(transactions)):
                # Check if dates are within 3 days
                date_diff = abs((transactions.iloc[i]['date'] - transactions.iloc[j]['date']).days)
                if date_diff > 3:
                    continue
                
                # Check if amounts are similar (within 1%)
                amount_diff = abs(transactions.iloc[i]['amount'] - transactions.iloc[j]['amount'])
                amount_avg = (transactions.iloc[i]['amount'] + transactions.iloc[j]['amount']) / 2
                if amount_avg > 0 and (amount_diff / amount_avg) > 0.01:
                    continue
                
                # Check description similarity
                desc1 = self._normalize_description(transactions.iloc[i].get('description', ''))
                desc2 = self._normalize_description(transactions.iloc[j].get('description', ''))
                
                similarity = SequenceMatcher(None, desc1, desc2).ratio()
                if similarity >= threshold:
                    similar_pairs.append((i, j, similarity))
        
        return similar_pairs
    
    def validate_date(self, date_value: Any, transaction_context: Dict = None) -> Optional[datetime]:
        """
        Robust date validation with context awareness.
        
        Args:
            date_value: The date to validate
            transaction_context: Optional context (e.g., other fields from transaction)
        
        Returns:
            Validated datetime or None if invalid
        """
        if pd.isna(date_value):
            return None
        
        # Convert to datetime if needed
        if isinstance(date_value, str):
            date_value = self._parse_flexible_date(date_value)
        elif isinstance(date_value, pd.Timestamp):
            date_value = date_value.to_pydatetime()
        
        if not isinstance(date_value, datetime):
            return None
        
        # Validation checks
        current_date = datetime.now()
        
        # Check if date is in the future
        if date_value > current_date + timedelta(days=7):  # Allow 7 days future for pending
            self.warnings.append(f"Future date detected: {date_value}")
            return None
        
        # Check if date is too old (before 2020)
        if date_value.year < 2020:
            self.warnings.append(f"Very old date detected: {date_value}")
            return None
        
        return date_value
    
    def _parse_flexible_date(self, date_str: str) -> Optional[datetime]:
        """Enhanced date parser with more formats."""
        date_formats = [
            '%m/%d/%Y', '%m/%d/%y',           # US format
            '%Y-%m-%d', '%y-%m-%d',           # ISO format
            '%d/%m/%Y', '%d/%m/%y',           # European format
            '%m-%d-%Y', '%m-%d-%y',           # Alternate US
            '%d-%m-%Y', '%d-%m-%y',           # Alternate European
            '%b %d, %Y', '%B %d, %Y',         # Jan 1, 2024
            '%d %b %Y', '%d %B %Y',           # 1 Jan 2024
            '%m.%d.%Y', '%d.%m.%Y',           # Dot separators
            '%Y/%m/%d',                        # Japanese format
        ]
        
        date_str = date_str.strip()
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        # Try pandas as fallback
        try:
            result = pd.to_datetime(date_str, errors='coerce')
            if not pd.isna(result):
                return result.to_pydatetime()
        except:
            pass
        
        return None
    
    def parse_amount(self, amount_value: Any, strict: bool = True) -> Optional[Decimal]:
        """
        Robust amount parsing with validation.
        
        Args:
            amount_value: The amount to parse
            strict: If True, reject suspicious amounts
        
        Returns:
            Decimal amount or None if invalid
        """
        if pd.isna(amount_value):
            return None
        
        # Handle numeric types
        if isinstance(amount_value, (int, float)):
            amount = Decimal(str(amount_value))
        else:
            # Clean string amounts
            amount_str = str(amount_value).strip()
            
            # Remove currency symbols and common characters
            amount_str = re.sub(r'[$,€£¥₹]', '', amount_str)
            amount_str = amount_str.replace('�', '')  # Unicode replacement char
            amount_str = amount_str.strip()
            
            # Handle empty or invalid
            if not amount_str or amount_str in ['-', '$ -', 'N/A']:
                return None
            
            # Handle negative in parentheses
            if amount_str.startswith('(') and amount_str.endswith(')'):
                amount_str = '-' + amount_str[1:-1]
            
            try:
                amount = Decimal(amount_str)
            except (InvalidOperation, ValueError):
                self.validation_errors.append(f"Could not parse amount: {amount_value}")
                return None
        
        # Validation checks
        if strict:
            # Check for suspicious amounts
            if abs(amount) > 50000:
                self.warnings.append(f"Very large amount detected: ${amount}")
            
            # Check for tiny amounts that might be errors
            if 0 < abs(amount) < Decimal('0.01'):
                self.warnings.append(f"Very small amount detected: ${amount}")
        
        return amount
    
    def validate_transaction_consistency(self, transaction: Dict) -> List[str]:
        """
        Validate internal consistency of a transaction.
        
        Returns list of validation errors.
        """
        errors = []
        
        # Check required fields
        required_fields = ['date', 'amount', 'payer']
        for field in required_fields:
            if field not in transaction or pd.isna(transaction.get(field)):
                errors.append(f"Missing required field: {field}")
        
        # Check amount consistency
        if 'original_amount' in transaction and 'amount' in transaction:
            orig = self.parse_amount(transaction['original_amount'], strict=False)
            curr = self.parse_amount(transaction['amount'], strict=False)
            if orig and curr and abs(orig - curr) > Decimal('0.01'):
                # Check if there's an allowed_amount that explains the difference
                if 'allowed_amount' not in transaction:
                    errors.append(f"Amount mismatch: original={orig}, current={curr}")
        
        # Check payer validity
        if 'payer' in transaction:
            payer = str(transaction['payer']).strip().title()
            if payer not in ['Ryan', 'Jordyn']:
                errors.append(f"Invalid payer: {payer}")
        
        # Check date validity
        if 'date' in transaction:
            valid_date = self.validate_date(transaction['date'])
            if not valid_date:
                errors.append(f"Invalid date: {transaction['date']}")
        
        return errors


class ImprovedDescriptionDecoder:
    """Enhanced description decoder with better pattern matching."""
    
    def __init__(self):
        self.patterns = self._compile_patterns()
        
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for better performance."""
        return {
            # Full reimbursement patterns (more flexible)
            'full_reimbursement': re.compile(
                r'(2x\s*to\s*calculate|100%\s*reimburse|full\s*reimburse|'
                r'reimburse\s*full|pay\s*back\s*full|owe\s*full)',
                re.IGNORECASE
            ),
            
            # Gift patterns (expanded)
            'gift': re.compile(
                r'(birthday|gift|present|christmas|xmas|valentine|anniversary|'
                r'mother\'?s?\s*day|father\'?s?\s*day|graduation|wedding)',
                re.IGNORECASE
            ),
            
            # Personal expense patterns
            'personal_jordyn': re.compile(
                r'(100%?\s*jordyn|jordyn\'?s?\s*only|just\s*jordyn|jordyn\s*personal)',
                re.IGNORECASE
            ),
            'personal_ryan': re.compile(
                r'(100%?\s*ryan|ryan\'?s?\s*only|just\s*ryan|ryan\s*personal)',
                re.IGNORECASE
            ),
            
            # Math expressions (improved)
            'math_expression': re.compile(
                r'\(([0-9\.\+\-\*\/\s]+)\)|'  # Parentheses
                r'=\s*([0-9\.\+\-\*\/\s]+)$',  # Equals at end
                re.IGNORECASE
            ),
            
            # Exclusion patterns (improved)
            'exclusion': re.compile(
                r'(remove|exclude|deduct|minus|except|not\s*including|excluding)\s*'
                r'\$?([0-9]+\.?[0-9]*)',
                re.IGNORECASE
            ),
            
            # Split payment patterns
            'split_payment': re.compile(
                r'(split\s*\$[0-9]+|'
                r'\$[0-9]+\s*/\s*\$[0-9]+|'
                r'paid\s*\$[0-9]+.*owe\s*\$[0-9]+)',
                re.IGNORECASE
            ),
            
            # Rent-related
            'rent': re.compile(
                r'(rent|lease|apartment|housing|landlord)',
                re.IGNORECASE
            ),
        }
    
    def decode_with_confidence(self, description: str, amount: Decimal, 
                              payer: str = None) -> Dict[str, Any]:
        """
        Decode description with confidence scoring.
        
        Returns enhanced result with confidence metrics.
        """
        if not description:
            return self._default_result(amount)
        
        description = description.strip()
        
        # Check patterns in priority order
        
        # 1. Full reimbursement (highest priority)
        if self.patterns['full_reimbursement'].search(description):
            return {
                'action': 'full_reimbursement',
                'payer_share': Decimal('0'),
                'other_share': amount,
                'reason': 'Full reimbursement pattern detected',
                'confidence': 0.95,
                'pattern_matched': 'full_reimbursement'
            }
        
        # 2. Gift patterns
        gift_match = self.patterns['gift'].search(description)
        if gift_match:
            return {
                'action': 'gift',
                'payer_share': amount,
                'other_share': Decimal('0'),
                'reason': f'Gift pattern: {gift_match.group(1)}',
                'confidence': 0.90,
                'pattern_matched': 'gift'
            }
        
        # 3. Personal expense patterns
        if self.patterns['personal_jordyn'].search(description):
            if payer == 'Ryan':
                # Ryan paid for Jordyn's expense
                return {
                    'action': 'personal_jordyn',
                    'payer_share': Decimal('0'),
                    'other_share': amount,
                    'reason': "Jordyn's personal expense paid by Ryan",
                    'confidence': 0.85,
                    'pattern_matched': 'personal_jordyn'
                }
            else:
                # Jordyn paid her own expense
                return {
                    'action': 'personal_jordyn',
                    'payer_share': amount,
                    'other_share': Decimal('0'),
                    'reason': "Jordyn's personal expense",
                    'confidence': 0.85,
                    'pattern_matched': 'personal_jordyn'
                }
        
        if self.patterns['personal_ryan'].search(description):
            if payer == 'Jordyn':
                # Jordyn paid for Ryan's expense
                return {
                    'action': 'personal_ryan',
                    'payer_share': Decimal('0'),
                    'other_share': amount,
                    'reason': "Ryan's personal expense paid by Jordyn",
                    'confidence': 0.85,
                    'pattern_matched': 'personal_ryan'
                }
            else:
                # Ryan paid his own expense
                return {
                    'action': 'personal_ryan',
                    'payer_share': amount,
                    'other_share': Decimal('0'),
                    'reason': "Ryan's personal expense",
                    'confidence': 0.85,
                    'pattern_matched': 'personal_ryan'
                }
        
        # 4. Exclusion patterns
        exclusion_match = self.patterns['exclusion'].search(description)
        if exclusion_match:
            try:
                excluded_amount = Decimal(exclusion_match.group(2))
                remaining = max(amount - excluded_amount, Decimal('0'))
                return {
                    'action': 'split_50_50',
                    'payer_share': remaining / 2,
                    'other_share': remaining / 2,
                    'reason': f'Excluded ${excluded_amount}, split remaining ${remaining}',
                    'confidence': 0.75,
                    'pattern_matched': 'exclusion',
                    'excluded_amount': excluded_amount
                }
            except:
                pass
        
        # 5. Rent patterns (usually need special handling)
        if self.patterns['rent'].search(description):
            # Flag for manual review as rent has special split logic
            return {
                'action': 'manual_review',
                'payer_share': amount,
                'other_share': Decimal('0'),
                'reason': 'Rent transaction - needs special handling',
                'confidence': 0.50,
                'pattern_matched': 'rent'
            }
        
        # Default: 50/50 split
        return self._default_result(amount)
    
    def _default_result(self, amount: Decimal) -> Dict[str, Any]:
        """Return default 50/50 split result."""
        return {
            'action': 'split_50_50',
            'payer_share': amount / 2,
            'other_share': amount / 2,
            'reason': 'Default 50/50 split',
            'confidence': 0.70,
            'pattern_matched': 'none'
        }


def apply_accuracy_improvements(reconciler):
    """
    Apply accuracy improvements to an existing reconciler instance.
    
    This function monkey-patches the reconciler with improved methods.
    """
    validator = AccuracyValidator()
    decoder = ImprovedDescriptionDecoder()
    
    # Store original methods
    reconciler._original_remove_duplicates = reconciler._remove_duplicate_transactions
    reconciler._original_process_transaction = reconciler.process_transaction
    
    # Enhanced duplicate removal
    def enhanced_remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced duplicate detection."""
        if df.empty:
            return df
        
        # First, apply original duplicate removal
        df = reconciler._original_remove_duplicates(df)
        
        # Then check for similar transactions
        similar_pairs = validator.find_similar_transactions(df, threshold=0.85)
        
        if similar_pairs:
            logger.warning(f"Found {len(similar_pairs)} potentially similar transactions")
            # Mark similar transactions for review
            indices_to_review = set()
            for i, j, score in similar_pairs:
                indices_to_review.add(j)  # Keep first, mark second for review
                logger.info(f"Similar transactions (score={score:.2f}):")
                logger.info(f"  1: {df.iloc[i]['date']} | ${df.iloc[i]['amount']} | {df.iloc[i].get('description', '')[:50]}")
                logger.info(f"  2: {df.iloc[j]['date']} | ${df.iloc[j]['amount']} | {df.iloc[j].get('description', '')[:50]}")
            
            # Add flag for manual review
            df['needs_duplicate_review'] = False
            df.loc[list(indices_to_review), 'needs_duplicate_review'] = True
        
        return df
    
    # Enhanced transaction processing
    def enhanced_process_transaction(row: pd.Series) -> None:
        """Enhanced transaction processing with better validation."""
        # Validate transaction consistency
        errors = validator.validate_transaction_consistency(row.to_dict())
        if errors:
            for error in errors:
                logger.warning(f"Transaction validation error: {error}")
        
        # Validate and clean date
        if 'date' in row:
            valid_date = validator.validate_date(row['date'])
            if valid_date:
                row['date'] = valid_date
            else:
                logger.error(f"Invalid date in transaction: {row.get('description', '')[:50]}")
                return
        
        # Validate and clean amount
        if 'amount' in row:
            valid_amount = validator.parse_amount(row['amount'])
            if valid_amount:
                row['amount'] = valid_amount
            else:
                logger.error(f"Invalid amount in transaction: {row.get('description', '')[:50]}")
                return
        
        # Use enhanced description decoder if no manual review
        if not row.get('has_manual_review', False) and 'description' in row:
            result = decoder.decode_with_confidence(
                row.get('description', ''),
                row['amount'],
                row.get('payer')
            )
            
            # Log low confidence decodings
            if result['confidence'] < 0.75:
                logger.info(f"Low confidence decoding ({result['confidence']:.2f}): {row.get('description', '')[:50]}")
        
        # Call original processing
        reconciler._original_process_transaction(row)
    
    # Apply patches
    reconciler._remove_duplicate_transactions = enhanced_remove_duplicates
    reconciler.process_transaction = enhanced_process_transaction
    
    # Also enhance the decoder
    reconciler.decoder = decoder
    
    logger.info("Accuracy improvements applied successfully")
    
    return validator  # Return validator for access to warnings/errors