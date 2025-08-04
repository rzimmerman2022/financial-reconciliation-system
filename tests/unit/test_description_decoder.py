"""
Unit tests for the Description Decoder module.

Tests all the critical patterns identified in the financial reconciliation system.
"""

import unittest
from decimal import Decimal
from src.core.description_decoder import DescriptionDecoder, decode_transaction


class TestDescriptionDecoder(unittest.TestCase):
    
    def setUp(self):
        self.decoder = DescriptionDecoder()
    
    def test_2x_to_calculate_pattern(self):
        """Test the '2x to calculate' pattern for full reimbursement."""
        test_cases = [
            "100% Jordyn (2x to calculate appropriately)",
            "$85.31 (Birthday present portion, 2x to calculate)",
            "Something 2X TO CALCULATE here",  # Case insensitive
            "2x to calculate",
        ]
        
        for description in test_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"), "Ryan")
                self.assertEqual(result["action"], "full_reimbursement")
                self.assertEqual(result["payer_share"], Decimal("0"))
                self.assertEqual(result["other_share"], Decimal("100.00"))
                self.assertEqual(result["confidence"], "high")
    
    def test_gift_patterns(self):
        """Test gift patterns that should result in no reimbursement."""
        gift_cases = [
            "Jordyn Christmas Present",
            "Birthday party supplies",
            "Gift for mom",
            "Valentine's Day presents",
            "Christmas gifts",
            "GIFT card",  # Case insensitive
        ]
        
        for description in gift_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("50.00"), "Ryan")
                self.assertEqual(result["action"], "gift")
                self.assertEqual(result["payer_share"], Decimal("50.00"))
                self.assertEqual(result["other_share"], Decimal("0"))
                self.assertEqual(result["confidence"], "high")
    
    def test_personal_expense_patterns(self):
        """Test 100% personal expense patterns."""
        # Test 100% Jordyn
        result = self.decoder.decode_transaction("100% Jordyn", Decimal("75.00"), "Ryan")
        self.assertEqual(result["action"], "personal_jordyn")
        self.assertEqual(result["payer_share"], Decimal("0"))
        self.assertEqual(result["other_share"], Decimal("75.00"))
        
        # Test 100% Ryan
        result = self.decoder.decode_transaction("100% Ryan", Decimal("75.00"), "Jordyn")
        self.assertEqual(result["action"], "personal_ryan")
        self.assertEqual(result["payer_share"], Decimal("0"))
        self.assertEqual(result["other_share"], Decimal("75.00"))
        
        # Test when person pays their own expense
        result = self.decoder.decode_transaction("100% Jordyn", Decimal("75.00"), "Jordyn")
        self.assertEqual(result["action"], "personal_jordyn")
        self.assertEqual(result["payer_share"], Decimal("75.00"))
        self.assertEqual(result["other_share"], Decimal("0"))
    
    def test_mathematical_expressions(self):
        """Test mathematical expressions in parentheses."""
        test_cases = [
            ("BACtrack (123.87)", Decimal("199.81"), Decimal("123.87")),
            ("Total (343.94 - 240.59)", Decimal("343.94"), Decimal("103.35")),
            ("Items (100.69-32.98)", Decimal("100.69"), Decimal("67.71")),
            ("Simple (50)", Decimal("100.00"), Decimal("50")),
        ]
        
        for description, total_amount, expected_calc in test_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, total_amount, "Ryan")
                self.assertEqual(result["action"], "split_50_50")
                self.assertEqual(result["confidence"], "medium")
                # Check that the calculated amount is split 50/50
                expected_split = expected_calc / 2
                # Use assertAlmostEqual for decimal precision issues
                self.assertAlmostEqual(float(result["payer_share"]), float(expected_split), places=2)
                self.assertAlmostEqual(float(result["other_share"]), float(expected_split), places=2)
    
    def test_exclusion_patterns(self):
        """Test removal/exclusion patterns."""
        test_cases = [
            ("***Remove $29.99 for Back Stretching Device***", Decimal("100.69"), Decimal("29.99")),
            ("Deduct $23.12 for ThereaTeras Dry Eye", Decimal("73.75"), Decimal("23.12")),
            ("Items - exclude $15.50", Decimal("50.00"), Decimal("15.50")),
        ]
        
        for description, total_amount, excluded_amount in test_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, total_amount, "Ryan")
                self.assertEqual(result["action"], "split_50_50")
                self.assertEqual(result["confidence"], "medium")
                
                expected_remaining = total_amount - excluded_amount
                expected_split = expected_remaining / 2
                
                self.assertEqual(result["payer_share"], expected_split)
                self.assertEqual(result["other_share"], expected_split)
                self.assertEqual(result["extracted_data"]["excluded_amount"], excluded_amount)
    
    def test_split_payment_patterns(self):
        """Test split payment patterns that require manual review."""
        test_cases = [
            "10/04 Order (Split $14.33 2463 / $29.06 EBT)",
            "Split $139.49 between accounts",
            "SPLIT $100 payment method",
        ]
        
        for description in test_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"), "Ryan")
                self.assertEqual(result["action"], "manual_review")
                self.assertEqual(result["confidence"], "low")
    
    def test_unclear_patterns(self):
        """Test patterns that require manual review."""
        unclear_cases = [
            "Lost (I will take half the financial burden as a sign of good faith)",
            "??? unclear transaction",
            "Discuss further",
            "Reassess next time",
            "Very difficult to determine who used what",
        ]
        
        for description in unclear_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"), "Ryan")
                self.assertEqual(result["action"], "manual_review")
                self.assertEqual(result["confidence"], "low")
    
    def test_default_split(self):
        """Test default 50/50 split for normal transactions."""
        normal_cases = [
            "Regular grocery shopping",
            "Walmart - household items",
            "Gas station fill-up",
            "",  # Empty description
            "   ",  # Whitespace only
        ]
        
        for description in normal_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"), "Ryan")
                self.assertEqual(result["action"], "split_50_50")
                self.assertEqual(result["payer_share"], Decimal("50.00"))
                self.assertEqual(result["other_share"], Decimal("50.00"))
                self.assertEqual(result["confidence"], "high")
    
    def test_pattern_priority(self):
        """Test that patterns are matched in correct priority order."""
        # "2x to calculate" should override gift patterns
        result = self.decoder.decode_transaction(
            "Birthday gift but 2x to calculate", 
            Decimal("100.00"), 
            "Ryan"
        )
        self.assertEqual(result["action"], "full_reimbursement")
        
        # Gift pattern should override personal patterns when both are present
        result = self.decoder.decode_transaction(
            "100% Jordyn Christmas present", 
            Decimal("100.00"), 
            "Ryan"
        )
        self.assertEqual(result["action"], "gift")  # Gift takes priority
    
    def test_convenience_function(self):
        """Test the convenience decode_transaction function."""
        result = decode_transaction("2x to calculate", Decimal("50.00"), "Ryan")
        self.assertEqual(result["action"], "full_reimbursement")
        self.assertEqual(result["other_share"], Decimal("50.00"))
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Zero amount
        result = self.decoder.decode_transaction("Regular purchase", Decimal("0"), "Ryan")
        self.assertEqual(result["payer_share"], Decimal("0"))
        self.assertEqual(result["other_share"], Decimal("0"))
        
        # Very large amount
        large_amount = Decimal("9999.99")
        result = self.decoder.decode_transaction("Regular purchase", large_amount, "Ryan")
        self.assertEqual(result["payer_share"], large_amount / 2)
        self.assertEqual(result["other_share"], large_amount / 2)
        
        # Invalid mathematical expression should not crash
        result = self.decoder.decode_transaction("Invalid (abc + def)", Decimal("100.00"), "Ryan")
        self.assertEqual(result["action"], "split_50_50")  # Should fall back to default
        
        # Malicious expression should not execute
        result = self.decoder.decode_transaction("Evil (__import__('os').system('echo hack'))", Decimal("100.00"), "Ryan")
        self.assertEqual(result["action"], "split_50_50")  # Should fall back to default
    
    def test_case_insensitivity(self):
        """Test that all patterns work regardless of case."""
        test_cases = [
            ("2X TO CALCULATE", "full_reimbursement"),
            ("BIRTHDAY GIFT", "gift"),
            ("100% JORDYN", "personal_jordyn"),
            ("REMOVE $10", "split_50_50"),
            ("LOST TRANSACTION", "manual_review"),
        ]
        
        for description, expected_action in test_cases:
            with self.subTest(description=description):
                result = self.decoder.decode_transaction(description, Decimal("100.00"), "Ryan")
                self.assertEqual(result["action"], expected_action)


if __name__ == "__main__":
    unittest.main(verbosity=2)
