"""
Description Language Decoder for Financial Reconciliation System

This module decodes transaction descriptions to determine the correct split logic
for Ryan and Jordyn's financial reconciliation system. Previous attempts failed
because the automated system misunderstood custom description codes as notes
rather than processing instructions.

CRITICAL BACKGROUND:
The expense system automatically split everything 50/50. Description codes were
created as WORKAROUNDS:
- "2x to calculate" does NOT mean double the amount
- It means "do NOT split - reimburse 100%" 
- Why? System did (Amount × 2) ÷ 2 = Amount for full reimbursement
"""

from decimal import Decimal
import re
from typing import Dict, Any, Optional
import logging

# Set up logging (without overriding app config)
logger = logging.getLogger(__name__)


class DescriptionDecoder:
    """
    Decoder for transaction description patterns in the financial reconciliation system.
    """
    
    def __init__(self):
        # Compile regex patterns for efficiency
        self.math_expression_pattern = re.compile(r'\(([0-9\.\+\-\*\/\s]+)\)', re.IGNORECASE)
        self.split_payment_pattern = re.compile(r'split\s+\$[0-9]+', re.IGNORECASE)
        # Add pattern for dollar amounts in exclusions
        self.exclusion_amount_pattern = re.compile(r'(?:remove|exclude|deduct).*?\$([0-9]+\.?[0-9]*)', re.IGNORECASE)
        
    def decode_transaction(self, description: str, amount: Decimal, payer: str = None) -> Dict[str, Any]:
        """
        Decode transaction description to determine split logic.
        
        Args:
            description: The description field from the transaction
            amount: The transaction amount (for validation)
            payer: Optional - who paid the transaction ("Ryan" or "Jordyn")
        
        Returns:
            dict with keys:
            - action: "split_50_50" | "full_reimbursement" | "gift" | 
                      "personal_ryan" | "personal_jordyn" | "manual_review"
            - payer_share: Decimal - amount payer is responsible for
            - other_share: Decimal - amount the other person owes
            - reason: str explaining the decoding logic applied
            - confidence: "high" | "medium" | "low"
            - extracted_data: dict of any parsed values
        """
        
        if not description:
            description = ""
        
        description_lower = description.lower().strip()
        
        # Initialize result structure
        result = {
            "action": "split_50_50",
            "payer_share": amount / 2,
            "other_share": amount / 2,
            "reason": "Default 50/50 split - no special pattern detected",
            "confidence": "high",
            "extracted_data": {}
        }
        
        # Check patterns in order of specificity
        
        # 1. Check for "2x to calculate" pattern - HIGHEST PRIORITY
        if self._contains_pattern(description_lower, ["2x to calculate"]):
            result.update({
                "action": "full_reimbursement",
                "payer_share": Decimal('0'),
                "other_share": amount,
                "reason": "2x to calculate pattern detected - 2x workaround for full reimbursement",
                "confidence": "high"
            })
            return result
        
        # 2. Check for gift patterns - Updated to include Christmas and Valentine
        gift_patterns = ["birthday", "gift", "present", "christmas", "valentine", "anniversary"]
        if self._contains_pattern(description_lower, gift_patterns):
            result.update({
                "action": "gift",
                "payer_share": amount,
                "other_share": Decimal('0'),
                "reason": f"Gift pattern detected: {self._find_matching_pattern(description_lower, gift_patterns)}",
                "confidence": "high"
            })
            return result
        
        # 3. Check for personal expense patterns
        if self._contains_pattern(description_lower, ["100% jordyn"]):
            if payer and payer.lower() == "ryan":
                result.update({
                    "action": "personal_jordyn",
                    "payer_share": Decimal('0'),
                    "other_share": amount,
                    "reason": "100% Jordyn pattern - Jordyn's personal expense paid by Ryan",
                    "confidence": "high"
                })
            else:
                result.update({
                    "action": "personal_jordyn",
                    "payer_share": amount,
                    "other_share": Decimal('0'),
                    "reason": "100% Jordyn pattern - Jordyn paid her own expense",
                    "confidence": "high"
                })
            return result
        
        if self._contains_pattern(description_lower, ["100% ryan"]):
            if payer and payer.lower() == "jordyn":
                result.update({
                    "action": "personal_ryan",
                    "payer_share": Decimal('0'),
                    "other_share": amount,
                    "reason": "100% Ryan pattern - Ryan's personal expense paid by Jordyn",
                    "confidence": "high"
                })
            else:
                result.update({
                    "action": "personal_ryan",
                    "payer_share": amount,
                    "other_share": Decimal('0'),
                    "reason": "100% Ryan pattern - Ryan paid his own expense",
                    "confidence": "high"
                })
            return result
        
        # 4. Check for mathematical expressions in parentheses
        math_match = self.math_expression_pattern.search(description)
        if math_match:
            try:
                expression = math_match.group(1).strip()
                # Safely evaluate simple math expressions
                calculated_amount = self._safe_evaluate_expression(expression)
                if calculated_amount is not None:
                    split_amount = calculated_amount / 2
                    result.update({
                        "action": "split_50_50",
                        "payer_share": split_amount,
                        "other_share": split_amount,
                        "reason": f"Mathematical expression found: ({expression}) = {calculated_amount}, split 50/50",
                        "confidence": "medium",
                        "extracted_data": {
                            "original_expression": expression,
                            "calculated_amount": calculated_amount
                        }
                    })
                    return result
            except Exception as e:
                logger.warning(f"Could not evaluate expression: {math_match.group(1)} - {e}")
        
        # 5. Check for exclusion/removal patterns
        exclusion_patterns = ["remove", "exclude", "deduct"]
        if self._contains_pattern(description_lower, exclusion_patterns):
            # Try to extract the amount to be removed
            excluded_amount = self._extract_excluded_amount(description)
            if excluded_amount is not None:
                remaining_amount = max(amount - excluded_amount, Decimal('0'))  # Prevent negative
                split_amount = remaining_amount / 2
                result.update({
                    "action": "split_50_50",
                    "payer_share": split_amount,
                    "other_share": split_amount,
                    "reason": f"Exclusion pattern detected - removed ${excluded_amount}, split remaining ${remaining_amount} 50/50",
                    "confidence": "medium",
                    "extracted_data": {
                        "excluded_amount": excluded_amount,
                        "remaining_amount": remaining_amount
                    }
                })
            else:
                result.update({
                    "action": "manual_review",
                    "payer_share": amount,
                    "other_share": Decimal('0'),
                    "reason": "Exclusion pattern detected but could not determine excluded amount",
                    "confidence": "low"
                })
            return result
        
        # 6. Check for split payment patterns - Enhanced regex
        split_patterns = [
            re.compile(r'split\s+\$[0-9]+', re.IGNORECASE),
            re.compile(r'\$[0-9]+.*\/.*\$[0-9]+', re.IGNORECASE),  # $XX / $YY pattern
            re.compile(r'credit card.*\/.*ebt', re.IGNORECASE)      # Credit Card / EBT pattern
        ]
        
        for pattern in split_patterns:
            if pattern.search(description):
                result.update({
                    "action": "manual_review",
                    "payer_share": amount,
                    "other_share": Decimal('0'),
                    "reason": "Split payment pattern detected - requires manual review",
                    "confidence": "low"
                })
                return result
        
        # 7. Check for unclear/discussion patterns
        unclear_patterns = ["lost", "discuss", "???", "reassess", "difficult to determine", "unsure"]
        if self._contains_pattern(description_lower, unclear_patterns):
            result.update({
                "action": "manual_review",
                "payer_share": amount,
                "other_share": Decimal('0'),
                "reason": f"Unclear pattern detected: {self._find_matching_pattern(description_lower, unclear_patterns)}",
                "confidence": "low"
            })
            return result
        
        # Default: Standard 50/50 split
        return result
    
    def _contains_pattern(self, text: str, patterns: list) -> bool:
        """Check if any of the patterns exist in the text."""
        return any(pattern in text for pattern in patterns)
    
    def _find_matching_pattern(self, text: str, patterns: list) -> str:
        """Find the first matching pattern in the text, preferring longer/more specific matches."""
        # Sort patterns by length (longest first) to prefer more specific matches
        sorted_patterns = sorted(patterns, key=len, reverse=True)
        for pattern in sorted_patterns:
            if pattern in text:
                return pattern
        return "unknown"
    
    def _safe_evaluate_expression(self, expression: str) -> Optional[Decimal]:
        """
        Safely evaluate a mathematical expression.
        Only allows basic arithmetic operations on numbers.
        Uses AST parsing instead of eval for security.
        """
        import ast
        import operator
        
        try:
            # Remove any whitespace
            expression = expression.replace(" ", "")
            
            # Check if expression contains only allowed characters
            allowed_chars = set("0123456789.+-*/()")
            if not all(c in allowed_chars for c in expression):
                return None
            
            # Define allowed operations
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.USub: operator.neg,
            }
            
            def eval_expr(node):
                if isinstance(node, ast.Num):  # <number>
                    return node.n
                elif isinstance(node, ast.Constant):  # Python 3.8+
                    return node.value
                elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
                    return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
                elif isinstance(node, ast.UnaryOp):  # <operator> <operand> e.g., -1
                    return ops[type(node.op)](eval_expr(node.operand))
                else:
                    raise ValueError(f"Unsupported expression: {ast.dump(node)}")
            
            # Parse and evaluate the expression
            node = ast.parse(expression, mode='eval')
            result = eval_expr(node.body)
            return Decimal(str(result))
        
        except Exception:
            return None
    
    def _extract_excluded_amount(self, description: str) -> Optional[Decimal]:
        """
        Extract the amount to be excluded from the description.
        Looks for patterns like "Remove $29.99" or "Deduct $23.12"
        """
        try:
            # Look for patterns like "Remove $XX.XX" or "Deduct $XX.XX"
            remove_pattern = re.compile(r'(?:remove|exclude|deduct).*?\$([0-9]+\.?[0-9]*)', re.IGNORECASE)
            match = remove_pattern.search(description)
            
            if match:
                return Decimal(match.group(1))
            
            # Look for patterns with *** around the removal
            asterisk_pattern = re.compile(r'\*+.*?remove.*?\$([0-9]+\.?[0-9]*)', re.IGNORECASE)
            match = asterisk_pattern.search(description)
            
            if match:
                return Decimal(match.group(1))
                
        except Exception:
            pass
        
        return None


def decode_transaction(description: str, amount: Decimal, payer: str = None) -> Dict[str, Any]:
    """
    Convenience function for decoding a single transaction.
    
    Args:
        description: The description field from the transaction
        amount: The transaction amount (for validation)
        payer: Optional - who paid the transaction ("Ryan" or "Jordyn")
    
    Returns:
        dict with decoding results
    """
    decoder = DescriptionDecoder()
    return decoder.decode_transaction(description, amount, payer)


# Example usage and testing
if __name__ == "__main__":
    # Test cases based on actual data patterns
    test_cases = [
        {
            "description": "100% Jordyn (2x to calculate appropriately)",
            "amount": Decimal("11.20"),
            "payer": "Ryan",
            "expected_action": "full_reimbursement"
        },
        {
            "description": "$85.31 (Birthday present portion, 2x to calculate)",
            "amount": Decimal("170.63"),
            "payer": "Ryan", 
            "expected_action": "full_reimbursement"
        },
        {
            "description": "Jordyn Christmas Present",
            "amount": Decimal("6.50"),
            "payer": "Ryan",
            "expected_action": "gift"
        },
        {
            "description": "***Remove $29.99 for Back Stretching Device***",
            "amount": Decimal("100.69"),
            "payer": "Ryan",
            "expected_action": "split_50_50"
        },
        {
            "description": "Lost (I will take half the financial burden as a sign of good faith)",
            "amount": Decimal("220.00"),
            "payer": "Ryan",
            "expected_action": "manual_review"
        },
        {
            "description": "Regular grocery shopping",
            "amount": Decimal("50.00"),
            "payer": "Ryan",
            "expected_action": "split_50_50"
        },
        {
            "description": "Target (45.00 + 12.99 - 5.00)",
            "amount": Decimal("100.00"),
            "payer": "Ryan",
            "expected_action": "split_50_50"
        },
        {
            "description": "Split $139.49 Credit Card / $76.25 EBT",
            "amount": Decimal("215.74"),
            "payer": "Ryan",
            "expected_action": "manual_review"
        }
    ]
    
    decoder = DescriptionDecoder()
    print("Testing Description Decoder...")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        result = decoder.decode_transaction(
            test["description"], 
            test["amount"], 
            test["payer"]
        )
        
        print(f"\nTest {i}:")
        print(f"Description: {test['description']}")
        print(f"Amount: ${test['amount']}")
        print(f"Payer: {test['payer']}")
        print(f"Expected Action: {test['expected_action']}")
        print(f"Actual Action: {result['action']}")
        print(f"Payer Share: ${result['payer_share']}")
        print(f"Other Share: ${result['other_share']}")
        print(f"Reason: {result['reason']}")
        print(f"Confidence: {result['confidence']}")
        
        if result["extracted_data"]:
            print(f"Extracted Data: {result['extracted_data']}")
        
        status = "✓ PASS" if result["action"] == test["expected_action"] else "✗ FAIL"
        print(f"Status: {status}")
        print("-" * 40)
