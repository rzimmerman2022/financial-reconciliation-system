#!/usr/bin/env python3
"""
Batch Review Helper for Financial Reconciliation
===============================================

This tool helps quickly review and classify multiple transactions
based on patterns, making the manual review process more efficient.

Author: Claude (Anthropic)
Date: July 29, 2025
"""

import pandas as pd
from decimal import Decimal
from datetime import datetime
from pathlib import Path
import re
from typing import List, Dict, Tuple

from manual_review_system import (
    ManualReviewSystem, TransactionCategory, SplitType
)


class BatchReviewHelper:
    """Helper for efficiently reviewing multiple transactions."""
    
    def __init__(self, review_db_path: str = "phase5_manual_reviews.db"):
        self.review_system = ManualReviewSystem(review_db_path)
        
        # Define common patterns for auto-classification
        self.patterns = {
            # Rent
            'rent': {
                'keywords': ['san palmas', 'rent', 'yardi'],
                'category': TransactionCategory.RENT,
                'split_type': SplitType.RENT_SPLIT,
                'confidence': 0.9
            },
            
            # Utilities
            'utilities': {
                'keywords': ['salt river', 'srp', 'cox', 'at&t', 'electric'],
                'category': TransactionCategory.UTILITIES,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.9
            },
            
            # Groceries
            'groceries': {
                'keywords': ['fry\'s', 'frys', 'safeway', 'whole foods', 'sprouts', 
                           'trader joe', 'albertson'],
                'category': TransactionCategory.GROCERIES,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.85
            },
            
            # Dining
            'dining': {
                'keywords': ['doordash', 'uber eats', 'grubhub', 'restaurant',
                           'starbucks', 'coffee', 'pizza', 'sushi', 'culver'],
                'category': TransactionCategory.DINING,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.85
            },
            
            # Personal - Credit cards and loans
            'personal_credit': {
                'keywords': ['autopay', 'payment thank you', 'credit card', 
                           'chase card', 'capital one', 'discover', 'apple card',
                           'affirm', 'uplift', 'avant', 'sallie mae', 'best buy',
                           'annual fee'],
                'category': TransactionCategory.PERSONAL_RYAN,  # Will be updated based on payer
                'split_type': SplitType.RYAN_FULL,  # Will be updated based on payer
                'confidence': 0.95
            },
            
            # Income
            'income': {
                'keywords': ['direct deposit', 'payroll', 'salary', 'interest',
                           'dividend', 'refund', 'cashback', 'reward', 'credit one reward'],
                'category': TransactionCategory.INCOME_RYAN,  # Will be updated based on payer
                'split_type': SplitType.RYAN_FULL,  # Will be updated based on payer
                'confidence': 0.95
            },
            
            # Settlements
            'settlement': {
                'keywords': ['zelle to ryan', 'zelle to jordyn', 'zelle from'],
                'category': TransactionCategory.SETTLEMENT,
                'split_type': SplitType.RYAN_FULL,  # Settlements don't split
                'confidence': 0.95
            },
            
            # Shopping
            'shopping': {
                'keywords': ['amazon', 'target', 'walmart', 'costco'],
                'category': TransactionCategory.SHOPPING,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.7  # Lower confidence - needs review
            },
            
            # Entertainment
            'entertainment': {
                'keywords': ['netflix', 'spotify', 'blizzard', 'harkins', 
                           'talking stick', 'casino'],
                'category': TransactionCategory.ENTERTAINMENT,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.8
            },
            
            # Healthcare
            'healthcare': {
                'keywords': ['cvs', 'walgreens', 'insurance', 'medical', 'pharmacy'],
                'category': TransactionCategory.HEALTHCARE,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.75
            },
            
            # Transportation
            'transportation': {
                'keywords': ['chevron', 'shell', 'gas', 'fuel', 'uber', 'lyft',
                           'progressive', 'insurance'],
                'category': TransactionCategory.TRANSPORTATION,
                'split_type': SplitType.SPLIT_50_50,
                'confidence': 0.8
            }
        }
    
    def auto_classify_pending(self, confidence_threshold: float = 0.8) -> Dict[str, List]:
        """Auto-classify pending transactions based on patterns."""
        pending = self.review_system.get_pending_reviews()
        
        if pending.empty:
            print("No pending transactions to classify")
            return {}
        
        results = {
            'auto_classified': [],
            'needs_review': [],
            'pattern_matches': {}
        }
        
        for _, row in pending.iterrows():
            desc_lower = str(row['description']).lower()
            payer = row['payer']
            
            best_match = None
            best_confidence = 0
            
            # Check each pattern
            for pattern_name, pattern_info in self.patterns.items():
                # Check if any keyword matches
                matches = sum(1 for keyword in pattern_info['keywords'] 
                            if keyword in desc_lower)
                
                if matches > 0:
                    # Calculate confidence based on keyword matches
                    keyword_confidence = matches / len(pattern_info['keywords'])
                    pattern_confidence = pattern_info['confidence']
                    total_confidence = keyword_confidence * pattern_confidence
                    
                    if total_confidence > best_confidence:
                        best_confidence = total_confidence
                        best_match = pattern_name
            
            if best_match and best_confidence >= confidence_threshold:
                pattern = self.patterns[best_match]
                category = pattern['category']
                split_type = pattern['split_type']
                
                # Adjust for payer-specific categories
                if best_match == 'personal_credit':
                    if payer == 'Ryan':
                        category = TransactionCategory.PERSONAL_RYAN
                        split_type = SplitType.RYAN_FULL
                    else:
                        category = TransactionCategory.PERSONAL_JORDYN
                        split_type = SplitType.JORDYN_FULL
                
                elif best_match == 'income':
                    if payer == 'Ryan':
                        category = TransactionCategory.INCOME_RYAN
                        split_type = SplitType.RYAN_FULL
                    else:
                        category = TransactionCategory.INCOME_JORDYN
                        split_type = SplitType.JORDYN_FULL
                
                results['auto_classified'].append({
                    'review_id': row['review_id'],
                    'description': row['description'],
                    'amount': row['amount'],
                    'payer': payer,
                    'category': category,
                    'split_type': split_type,
                    'pattern': best_match,
                    'confidence': best_confidence
                })
                
                # Track pattern usage
                if best_match not in results['pattern_matches']:
                    results['pattern_matches'][best_match] = 0
                results['pattern_matches'][best_match] += 1
            else:
                results['needs_review'].append({
                    'review_id': row['review_id'],
                    'description': row['description'],
                    'amount': row['amount'],
                    'payer': payer,
                    'best_match': best_match,
                    'confidence': best_confidence
                })
        
        return results
    
    def apply_auto_classifications(self, classifications: List[Dict],
                                 dry_run: bool = True) -> int:
        """Apply auto-classifications to transactions."""
        if dry_run:
            print("\nDRY RUN - No changes will be made")
            print("="*60)
        
        count = 0
        for item in classifications:
            if dry_run:
                print(f"\n{item['description']}")
                print(f"  Amount: ${item['amount']:,.2f}")
                print(f"  Payer: {item['payer']}")
                print(f"  → Category: {item['category'].value}")
                print(f"  → Split: {item['split_type'].value}")
                print(f"  → Pattern: {item['pattern']} (confidence: {item['confidence']:.2%})")
            else:
                success = self.review_system.review_transaction(
                    review_id=item['review_id'],
                    category=item['category'],
                    split_type=item['split_type'],
                    notes=f"Auto-classified: {item['pattern']} pattern",
                    reviewed_by='Batch Auto-Classifier'
                )
                if success:
                    count += 1
        
        if not dry_run:
            print(f"\n✓ Applied {count} auto-classifications")
        
        return count
    
    def review_by_pattern(self, pattern_name: str) -> pd.DataFrame:
        """Get all pending transactions matching a specific pattern."""
        if pattern_name not in self.patterns:
            print(f"Unknown pattern: {pattern_name}")
            print(f"Available patterns: {', '.join(self.patterns.keys())}")
            return pd.DataFrame()
        
        pattern = self.patterns[pattern_name]
        pending = self.review_system.get_pending_reviews()
        
        matches = []
        for _, row in pending.iterrows():
            desc_lower = str(row['description']).lower()
            if any(keyword in desc_lower for keyword in pattern['keywords']):
                matches.append(row)
        
        if matches:
            return pd.DataFrame(matches)
        else:
            return pd.DataFrame()
    
    def bulk_apply_pattern(self, pattern_name: str, 
                          override_category: TransactionCategory = None,
                          override_split: SplitType = None) -> int:
        """Apply a pattern classification to all matching transactions."""
        matches_df = self.review_by_pattern(pattern_name)
        
        if matches_df.empty:
            print(f"No transactions match pattern: {pattern_name}")
            return 0
        
        pattern = self.patterns[pattern_name]
        category = override_category or pattern['category']
        split_type = override_split or pattern['split_type']
        
        print(f"\nFound {len(matches_df)} transactions matching '{pattern_name}'")
        print(f"Will classify as: {category.value} with {split_type.value}")
        
        confirm = input("\nProceed? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled")
            return 0
        
        count = 0
        for _, row in matches_df.iterrows():
            # Adjust for payer-specific categories
            final_category = category
            final_split = split_type
            
            if pattern_name in ['personal_credit', 'income']:
                if row['payer'] == 'Ryan':
                    final_category = TransactionCategory.PERSONAL_RYAN if pattern_name == 'personal_credit' else TransactionCategory.INCOME_RYAN
                    final_split = SplitType.RYAN_FULL
                else:
                    final_category = TransactionCategory.PERSONAL_JORDYN if pattern_name == 'personal_credit' else TransactionCategory.INCOME_JORDYN
                    final_split = SplitType.JORDYN_FULL
            
            success = self.review_system.review_transaction(
                review_id=row['review_id'],
                category=final_category,
                split_type=final_split,
                notes=f"Batch classified: {pattern_name} pattern",
                reviewed_by='Batch Pattern Classifier'
            )
            if success:
                count += 1
        
        print(f"\n✓ Classified {count} transactions")
        return count
    
    def show_classification_summary(self):
        """Show summary of pending classifications."""
        results = self.auto_classify_pending()
        
        print("\n" + "="*60)
        print("AUTO-CLASSIFICATION SUMMARY")
        print("="*60)
        
        print(f"\nTotal pending: {len(results['auto_classified']) + len(results['needs_review'])}")
        print(f"Can auto-classify: {len(results['auto_classified'])}")
        print(f"Need manual review: {len(results['needs_review'])}")
        
        if results['pattern_matches']:
            print("\nPattern matches:")
            for pattern, count in sorted(results['pattern_matches'].items(), 
                                       key=lambda x: x[1], reverse=True):
                print(f"  {pattern}: {count}")
        
        if results['needs_review']:
            print(f"\nTop 10 needing manual review:")
            for item in results['needs_review'][:10]:
                print(f"\n  {item['description']}")
                print(f"    Amount: ${item['amount']:,.2f}")
                print(f"    Payer: {item['payer']}")
                if item['best_match']:
                    print(f"    Best match: {item['best_match']} ({item['confidence']:.2%})")


def main():
    """Run the batch review helper."""
    helper = BatchReviewHelper()
    
    while True:
        print("\n" + "="*60)
        print("BATCH REVIEW HELPER")
        print("="*60)
        print("\nOptions:")
        print("1. Show classification summary")
        print("2. Auto-classify with high confidence")
        print("3. Review by pattern")
        print("4. Apply pattern to all matches")
        print("5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == '1':
            helper.show_classification_summary()
            
        elif choice == '2':
            results = helper.auto_classify_pending(confidence_threshold=0.85)
            if results['auto_classified']:
                print(f"\nFound {len(results['auto_classified'])} high-confidence matches")
                
                # Show preview
                helper.apply_auto_classifications(
                    results['auto_classified'][:10], 
                    dry_run=True
                )
                
                if len(results['auto_classified']) > 10:
                    print(f"\n... and {len(results['auto_classified']) - 10} more")
                
                confirm = input("\nApply all classifications? (y/n): ").strip().lower()
                if confirm == 'y':
                    count = helper.apply_auto_classifications(
                        results['auto_classified'], 
                        dry_run=False
                    )
                    print(f"✓ Applied {count} classifications")
            else:
                print("No high-confidence matches found")
                
        elif choice == '3':
            print("\nAvailable patterns:")
            for i, pattern in enumerate(helper.patterns.keys(), 1):
                print(f"{i}. {pattern}")
            
            pattern_idx = input("\nSelect pattern number: ").strip()
            try:
                pattern_name = list(helper.patterns.keys())[int(pattern_idx) - 1]
                matches = helper.review_by_pattern(pattern_name)
                
                if not matches.empty:
                    print(f"\nFound {len(matches)} matches:")
                    print(matches[['description', 'amount', 'payer']].to_string())
                else:
                    print("No matches found")
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == '4':
            print("\nAvailable patterns:")
            for i, pattern in enumerate(helper.patterns.keys(), 1):
                print(f"{i}. {pattern}")
            
            pattern_idx = input("\nSelect pattern number: ").strip()
            try:
                pattern_name = list(helper.patterns.keys())[int(pattern_idx) - 1]
                helper.bulk_apply_pattern(pattern_name)
            except (ValueError, IndexError):
                print("Invalid selection")
                
        elif choice == '5':
            print("\nExiting batch review helper")
            break
        else:
            print("Invalid option")


if __name__ == "__main__":
    main()