"""
Comprehensive Test Suite for Description Decoder

This test suite validates all the patterns and edge cases for the
financial reconciliation description decoder.
"""

import unittest
from decimal import Decimal
from src.core.description_decoder import DescriptionDecoder, decode_transaction


class TestDescriptionDecoder(unittest.TestCase):
    
    def setUp(self):
        self.decoder = DescriptionDecoder()
    
    def test_standard_50_50_split(self):
        """Test 1: Standard 50/50 split (no special pattern)"""
        result = self.decoder.decode_transaction("Groceries at Whole Foods", Decimal("100.00"))
        self.assertEqual(result["action"], "split_50_50")
        self.assertEqual(result["payer_share"], Decimal("50.00"))
        self.assertEqual(result["other_share"], Decimal("50.00"))
        self.assertEqual(result["confidence"], "high")
    
    def test_full_reimbursement_2x_pattern(self):
        """Test 2: Full reimbursement (2x pattern) - CRITICAL TEST"""
        result = self.decoder.decode_transaction("Gas - 2x to calculate appropriately", Decimal("50.00"))
        self.assertEqual(result["action"], "full_reimbursement")
        self.assertEqual(result["payer_share"], Decimal("0.00"))
        self.assertEqual(result["other_share"], Decimal("50.00"))
        self.assertIn("2x workaround", result["reason"])
        self.assertEqual(result["confidence"], "high")
    
    def test_gift_no_reimbursement(self):
        """Test 3: Gift (no reimbursement)"""
        result = self.decoder.decode_transaction("Birthday present for Mom", Decimal("75.00"))
        self.assertEqual(result["action"], "gift")
        self.assertEqual(result["payer_share"], Decimal("75.00"))
        self.assertEqual(result["other_share"], Decimal("0.00"))
        self.assertEqual(result["confidence"], "high")
    
    def test_personal_expense_jordyn(self):
        """Test 4: Personal expense - Jordyn"""
        result = self.decoder.decode_transaction("Clothes shopping - 100% Jordyn", Decimal("120.00"), "Ryan")
        self.assertEqual(result["action"], "personal_jordyn")
        self.assertEqual(result["payer_share"], Decimal("0.00"))
        self.assertEqual(result["other_share"], Decimal("120.00"))
    
    def test_personal_expense_ryan(self):
        """Test 5: Personal expense - Ryan"""
        result = self.decoder.decode_transaction("Video game (100% Ryan)", Decimal("60.00"), "Jordyn")
        self.assertEqual(result["action"], "personal_ryan")
        self.assertEqual(result["payer_share"], Decimal("0.00"))
        self.assertEqual(result["other_share"], Decimal("60.00"))
    
    def test_math_expression_extraction(self):
        """Test 6: Math expression extraction"""
        result = self.decoder.decode_transaction("Target (45.00 + 12.99 - 5.00)", Decimal("100.00"))
        self.assertEqual(result["action"], "split_50_50")
        self.assertEqual(result["extracted_data"]["calculated_amount"], Decimal("52.99"))
        self.assertEqual(result["payer_share"], Decimal("26.495"))
        self.assertEqual(result["other_share"], Decimal("26.495"))
    
    def test_manual_review_split_payment(self):
        """Test 7: Manual review triggers - Split payment"""
        result = self.decoder.decode_transaction("Split $139.49 Credit Card / $76.25 EBT", Decimal("215.74"))
        self.assertEqual(result["action"], "manual_review")
        self.assertEqual(result["confidence"], "low")
    
    def test_exclusion_pattern(self):
        """Test 8: Exclusion pattern with amount extraction"""
        result = self.decoder.decode_transaction("***Remove $29.99 for Back Stretching Device***", Decimal("100.69"))
        self.assertEqual(result["action"], "split_50_50")
        self.assertEqual(result["extracted_data"]["excluded_amount"], Decimal("29.99"))
        self.assertEqual(result["extracted_data"]["remaining_amount"], Decimal("70.70"))
        self.assertEqual(result["payer_share"], Decimal("35.35"))
    
    def test_actual_data_patterns(self):
        """Test with actual data from your examples"""
        # Test case from your data: "100% Jordyn (2x to calculate appropriately)"
        result = self.decoder.decode_transaction("100% Jordyn (2x to calculate appropriately)", Decimal("11.20"), "Ryan")
        self.assertEqual(result["action"], "full_reimbursement")
        
        # Test case: "$85.31 (Birthday present portion, 2x to calculate)"
        result = self.decoder.decode_transaction("$85.31 (Birthday present portion, 2x to calculate)", Decimal("170.63"), "Ryan")
        self.assertEqual(result["action"], "full_reimbursement")
        
        # Test case: "Jordyn Christmas Present"
        result = self.decoder.decode_transaction("Jordyn Christmas Present", Decimal("6.50"), "Ryan")
        self.assertEqual(result["action"], "gift")
    
    def test_edge_cases(self):
        """Test edge cases"""
        # Empty description
        result = self.decoder.decode_transaction("", Decimal("50.00"))
        self.assertEqual(result["action"], "split_50_50")
        
        # None description
        result = self.decoder.decode_transaction(None, Decimal("50.00"))
        self.assertEqual(result["action"], "split_50_50")
        
        # Complex case with multiple patterns - 2x should take priority
        result = self.decoder.decode_transaction("Birthday gift - 2x to calculate", Decimal("100.00"))
        self.assertEqual(result["action"], "full_reimbursement")  # 2x should take priority over gift
    
    def test_gift_pattern_variations(self):
        """Test various gift patterns"""
        gift_tests = [
            ("Birthday cake", "birthday"),
            ("Christmas gift for mom", "christmas"),
            ("Valentine's dinner", "valentine"),
            ("Anniversary present", "anniversary"),
            ("Wedding gift", "gift"),
            ("Birthday present", "birthday")  # "birthday" is longer and more specific than "present"
        ]
        
        for description, pattern in gift_tests:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("50.00"))
                self.assertEqual(result["action"], "gift")
                self.assertIn(pattern, result["reason"])
    
    def test_personal_expense_variations(self):
        """Test personal expense patterns with different payers"""
        # Jordyn pays her own expense
        result = self.decoder.decode_transaction("Nail salon - 100% Jordyn", Decimal("80.00"), "Jordyn")
        self.assertEqual(result["action"], "personal_jordyn")
        self.assertEqual(result["payer_share"], Decimal("80.00"))
        self.assertEqual(result["other_share"], Decimal("0.00"))
        
        # Ryan pays Jordyn's expense
        result = self.decoder.decode_transaction("Nail salon - 100% Jordyn", Decimal("80.00"), "Ryan")
        self.assertEqual(result["action"], "personal_jordyn")
        self.assertEqual(result["payer_share"], Decimal("0.00"))
        self.assertEqual(result["other_share"], Decimal("80.00"))
    
    def test_mathematical_expressions(self):
        """Test various mathematical expressions"""
        math_tests = [
            ("Store (10.50 + 5.25)", Decimal("15.75")),
            ("Gas (25.00 - 2.50)", Decimal("22.50")),
            ("Food (15.00 * 2)", Decimal("30.00")),
            ("Bills (100.00 / 4)", Decimal("25.00")),
        ]
        
        for description, expected_calc in math_tests:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"))
                self.assertEqual(result["action"], "split_50_50")
                self.assertEqual(result["extracted_data"]["calculated_amount"], expected_calc)
                self.assertEqual(result["payer_share"], expected_calc / 2)
    
    def test_exclusion_patterns(self):
        """Test exclusion patterns"""
        exclusion_tests = [
            ("Store - Remove $10.00 for personal item", Decimal("10.00")),
            ("***Exclude $25.50 from split***", Decimal("25.50")),
            ("Deduct $5.99 for Ryan's coffee", Decimal("5.99")),
        ]
        
        for description, excluded_amount in exclusion_tests:
            with self.subTest(description=description):
                total = Decimal("100.00")
                result = self.decoder.decode_transaction(description, total)
                self.assertEqual(result["action"], "split_50_50")
                self.assertEqual(result["extracted_data"]["excluded_amount"], excluded_amount)
                expected_remaining = total - excluded_amount
                self.assertEqual(result["extracted_data"]["remaining_amount"], expected_remaining)
                self.assertEqual(result["payer_share"], expected_remaining / 2)
    
    def test_unclear_patterns(self):
        """Test unclear/discussion patterns"""
        unclear_tests = [
            "Lost receipt - discuss later",
            "Amount is confusing - ???",
            "Need to reassess this charge",
            "Difficult to determine split",
            "Unsure about this one"
        ]
        
        for description in unclear_tests:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("50.00"))
                self.assertEqual(result["action"], "manual_review")
                self.assertEqual(result["confidence"], "low")
    
    def test_priority_order(self):
        """Test that patterns are processed in correct priority order"""
        # 2x pattern should override gift pattern
        result = self.decoder.decode_transaction("Birthday gift (2x to calculate)", Decimal("100.00"))
        self.assertEqual(result["action"], "full_reimbursement")
        
        # 2x pattern should override personal patterns
        result = self.decoder.decode_transaction("100% Ryan stuff (2x to calculate)", Decimal("50.00"))
        self.assertEqual(result["action"], "full_reimbursement")
    
    def test_convenience_function(self):
        """Test the standalone convenience function"""
        result = decode_transaction("Test transaction", Decimal("100.00"))
        self.assertEqual(result["action"], "split_50_50")
        self.assertEqual(result["payer_share"], Decimal("50.00"))
        self.assertEqual(result["other_share"], Decimal("50.00"))
    
    def test_negative_prevention(self):
        """Test that exclusions don't create negative amounts"""
        # Exclusion larger than total should not go negative
        result = self.decoder.decode_transaction("Remove $150.00 from total", Decimal("100.00"))
        self.assertEqual(result["action"], "split_50_50")
        self.assertEqual(result["extracted_data"]["remaining_amount"], Decimal("0.00"))
        self.assertEqual(result["payer_share"], Decimal("0.00"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
