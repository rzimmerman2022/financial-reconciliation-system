#!/usr/bin/env python3
"""
Manual Review Helper - Interactive Resolution of Complex Cases

This tool helps you manually review and resolve ambiguous financial entries
to ensure 100% accuracy in the reconciliation.
"""

import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from decimal import Decimal
import re

class ManualReviewHelper:
    """Interactive helper for resolving complex financial calculations."""
    
    def __init__(self):
        self.review_queue = []
        self.resolutions = []
        self.review_log = []
        
    def load_manual_review_items(self, filepath: Path):
        """Load items requiring manual review."""
        if filepath.exists():
            df = pd.read_csv(filepath)
            self.review_queue = df.to_dict('records')
            print(f"Loaded {len(self.review_queue)} items for manual review from {filepath}")
        else:
            print(f"No manual review file found at {filepath}")
            print("Please run the main reconciliation engine first to generate this file.")
    
    def analyze_complex_description(self, description: str) -> dict:
        """Analyze description for complex patterns and suggest resolutions."""
        
        analysis = {
            'original_description': description,
            'detected_patterns': [],
            'suggested_actions': [],
            'extracted_values': {}
        }
        
        if not isinstance(description, str):
            return analysis

        desc_lower = description.lower()
        
        # Check for 2x calculation pattern
        if '2x to calculate' in desc_lower or '2 x to calculate' in desc_lower:
            analysis['detected_patterns'].append('2x_calculation')
            analysis['suggested_actions'].append(
                "This may be a case where one person paid for two. The budgeted amount might need to be doubled."
            )
            
            # Try to extract the multiplier
            multiplier_match = re.search(r'(\d+)\s*x\s*to\s*calculate', desc_lower)
            if multiplier_match:
                analysis['extracted_values']['multiplier'] = int(multiplier_match.group(1))
        
        # Check for gift/present pattern
        if 'birthday present' in desc_lower or 'gift' in desc_lower:
            analysis['detected_patterns'].append('gift_allocation')
            
            # Try to extract gift amount
            amount_match = re.search(r'\$([0-9,]+\.?\d*)', description)
            if amount_match:
                analysis['extracted_values']['gift_amount'] = amount_match.group(1)
                analysis['suggested_actions'].append(
                    f"Gift amount detected: ${amount_match.group(1)}. This should likely be allocated 100% to the gift giver."
                )
        
        # Check for split payment
        if 'split' in desc_lower:
            analysis['detected_patterns'].append('split_payment')
            
            # Try to extract split amounts
            split_match = re.search(r'split\s*\$([0-9,]+\.?\d*)\s*[^/]*/\s*\$([0-9,]+\.?\d*)', desc_lower)
            if split_match:
                analysis['extracted_values']['payment_1'] = split_match.group(1)
                analysis['extracted_values']['payment_2'] = split_match.group(2)
                analysis['suggested_actions'].append(
                    f"Split payment detected: ${split_match.group(1)} / ${split_match.group(2)}. Verify allocation."
                )
        
        # Check for exclusions
        if 'remove' in desc_lower or 'exclude' in desc_lower or 'deduct' in desc_lower:
            analysis['detected_patterns'].append('exclusion')
            
            # Try to extract what to exclude
            exclude_match = re.search(r'(remove|exclude|deduct)\s+([^,.\n]+)', desc_lower)
            if exclude_match:
                item_to_exclude = exclude_match.group(2).strip()
                analysis['extracted_values']['exclude_item'] = item_to_exclude
                analysis['suggested_actions'].append(
                    f"Exclusion requested for: '{item_to_exclude}'. Determine its dollar value."
                )
        
        # Check for percentage allocations
        percent_match = re.search(r'(\d+)%\s*(ryan|jordyn)', desc_lower)
        if percent_match:
            analysis['detected_patterns'].append('percentage_allocation')
            analysis['extracted_values']['allocation_percent'] = int(percent_match.group(1))
            analysis['extracted_values']['allocation_person'] = percent_match.group(2).title()
            analysis['suggested_actions'].append(
                f"{percent_match.group(1)}% should be allocated to {percent_match.group(2).title()}"
            )
        
        # Check for mathematical expressions
        math_expr = re.search(r'\(([0-9\.\+\-\*\/\s]+)\)', description)
        if math_expr:
            analysis['detected_patterns'].append('math_expression')
            analysis['extracted_values']['math_expression'] = math_expr.group(1)
            analysis['suggested_actions'].append(
                f"Mathematical expression found: '{math_expr.group(1)}'. Evaluate to find the final amount."
            )
        
        return analysis
    
    def interactive_review_session(self):
        """Run an interactive session to review each item."""
        
        print("\n" + "="*60)
        print("MANUAL REVIEW SESSION")
        print("="*60)
        print(f"Total items to review: {len(self.review_queue)}")
        print("For each item, you'll see the details and can make a decision.")
        print("="*60)
        
        for idx, item in enumerate(self.review_queue):
            print(f"\n[{idx+1}/{len(self.review_queue)}] Reviewing Entry: {item.get('entry_id', 'Unknown')}")
            print("-" * 60)
            
            # Display basic info
            print(f"  Date: {item.get('date', 'Unknown')}")
            print(f"  Person: {item.get('person', 'Unknown')}")
            print(f"  Amount: ${item.get('amount', 0):.2f}")
            print(f"  Description: {item.get('description', 'No description')}")
            print(f"  Review Reasons: {item.get('review_reasons', 'Unknown')}")
            
            # Analyze the description
            analysis = self.analyze_complex_description(item.get('description'))
            
            if analysis['detected_patterns']:
                print("\n  ?? PATTERN ANALYSIS:")
                print(f"  Detected patterns: {', '.join(analysis['detected_patterns'])}")
                
                if analysis['extracted_values']:
                    print("\n  Extracted values:")
                    for key, value in analysis['extracted_values'].items():
                        print(f"    - {key}: {value}")
                
                if analysis['suggested_actions']:
                    print("\n  ?? SUGGESTIONS:")
                    for suggestion in analysis['suggested_actions']:
                        print(f"    • {suggestion}")
            
            # Get user decision
            print("\n  ?? RESOLUTION OPTIONS:")
            print("  1. Allocate 100% to Ryan")
            print("  2. Allocate 100% to Jordyn")
            print("  3. Split 50/50")
            print("  4. Custom allocation")
            print("  5. Mark as gift/present (100% to giver)")
            print("  6. Exclude from reconciliation")
            print("  7. Skip for now")
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            resolution = self.process_resolution(item, choice)
            if resolution:
                self.resolutions.append(resolution)
                self.review_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'entry_id': item.get('entry_id'),
                    'action': resolution['action'],
                    'notes': resolution.get('notes', '')
                })
                print(f"? Resolution recorded: {resolution['action']}")
            
            # Ask if user wants to continue
            if idx < len(self.review_queue) - 1:
                cont = input("\nContinue to next item? (y/n): ").strip().lower()
                if cont != 'y':
                    break
        
        print("\n" + "="*60)
        print(f"Review session complete. Resolved {len(self.resolutions)} items.")
        
    def process_resolution(self, item: dict, choice: str) -> dict:
        """Process user's resolution choice."""
        
        resolution = {
            'entry_id': item.get('entry_id'),
            'original_amount': item.get('amount'),
            'action': '',
            'ryan_allocation': 0.0,
            'jordyn_allocation': 0.0,
            'exclude': False,
            'notes': ''
        }
        
        amount = float(item.get('amount', 0))
        
        if choice == '1':
            resolution['action'] = 'allocate_100_ryan'
            resolution['ryan_allocation'] = amount
            resolution['jordyn_allocation'] = 0.0
            
        elif choice == '2':
            resolution['action'] = 'allocate_100_jordyn'
            resolution['ryan_allocation'] = 0.0
            resolution['jordyn_allocation'] = amount
            
        elif choice == '3':
            resolution['action'] = 'split_50_50'
            resolution['ryan_allocation'] = amount / 2
            resolution['jordyn_allocation'] = amount / 2
            
        elif choice == '4':
            try:
                ryan_pct = float(input("Enter Ryan's percentage (0-100): ").strip())
                jordyn_pct = 100 - ryan_pct
                
                resolution['action'] = f'custom_split_{ryan_pct}_{jordyn_pct}'
                resolution['ryan_allocation'] = amount * (ryan_pct / 100)
                resolution['jordyn_allocation'] = amount * (jordyn_pct / 100)
                resolution['notes'] = f"Custom split: Ryan {ryan_pct}%, Jordyn {jordyn_pct}%"
            except ValueError:
                print("Invalid percentage. Skipping.")
                return None

        elif choice == '5':
            giver = input("Who gave the gift? (Ryan/Jordyn): ").strip().title()
            if giver == 'Ryan':
                resolution['action'] = 'gift_from_ryan'
                resolution['ryan_allocation'] = amount
                resolution['jordyn_allocation'] = 0.0
            else:
                resolution['action'] = 'gift_from_jordyn'
                resolution['ryan_allocation'] = 0.0
                resolution['jordyn_allocation'] = amount
            resolution['notes'] = f"Gift from {giver}"
            
        elif choice == '6':
            resolution['action'] = 'exclude'
            resolution['exclude'] = True
            resolution['notes'] = input("Reason for exclusion: ").strip()
            
        elif choice == '7':
            print("Skipping item.")
            return None
        
        else:
            print("Invalid choice. Skipping.")
            return None
        
        # Add any additional notes
        additional_notes = input("Any additional notes? (press Enter to skip): ").strip()
        if additional_notes:
            resolution['notes'] = (resolution['notes'] + " | " + additional_notes) if resolution['notes'] else additional_notes
        
        return resolution
    
    def save_resolutions(self, output_dir: Path):
        """Save resolutions to file."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save resolutions as CSV
        if self.resolutions:
            resolutions_df = pd.DataFrame(self.resolutions)
            resolutions_df.to_csv(output_dir / 'manual_resolutions.csv', index=False)
            print(f"Saved {len(self.resolutions)} resolutions to manual_resolutions.csv")
        
        # Save review log
        if self.review_log:
            with open(output_dir / 'manual_review_log.json', 'w') as f:
                json.dump(self.review_log, f, indent=2)
            print(f"Saved review log with {len(self.review_log)} entries")
        
        # Generate summary report
        self.generate_summary_report(output_dir)
    
    def generate_summary_report(self, output_dir: Path):
        """Generate a summary of the manual review session."""
        
        summary = {
            'session_date': datetime.now().isoformat(),
            'total_reviewed': len(self.resolutions),
            'total_pending': len(self.review_queue) - len(self.resolutions),
            'resolution_breakdown': {},
            'allocation_totals': {
                'ryan_total': 0.0,
                'jordyn_total': 0.0,
                'excluded_total': 0.0
            }
        }
        
        # Analyze resolutions
        for res in self.resolutions:
            action = res['action']
            summary['resolution_breakdown'][action] = summary['resolution_breakdown'].get(action, 0) + 1
            
            if not res.get('exclude', False):
                summary['allocation_totals']['ryan_total'] += res['ryan_allocation']
                summary['allocation_totals']['jordyn_total'] += res['jordyn_allocation']
            else:
                summary['allocation_totals']['excluded_total'] += res['original_amount']
        
        # Save summary
        with open(output_dir / 'manual_review_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Print summary
        print("\n" + "="*60)
        print("MANUAL REVIEW SUMMARY")
        print("="*60)
        print(f"Total items reviewed: {summary['total_reviewed']}")
        print(f"Items still pending: {summary['total_pending']}")
        print("\nResolution breakdown:")
        for action, count in summary['resolution_breakdown'].items():
            print(f"  - {action}: {count}")
        print(f"\nAllocation totals:")
        print(f"  - Ryan: ${summary['allocation_totals']['ryan_total']:,.2f}")
        print(f"  - Jordyn: ${summary['allocation_totals']['jordyn_total']:,.2f}")
        print(f"  - Excluded: ${summary['allocation_totals']['excluded_total']:,.2f}")

def main():
    """Run the manual review helper."""
    
    helper = ManualReviewHelper()
    
    # Load items requiring manual review from the previous script's output
    review_file = Path("output/master_reconciliation/manual_review_required.csv")
    helper.load_manual_review_items(review_file)
    
    if helper.review_queue:
        # Run interactive review
        helper.interactive_review_session()
        
        # Save results
        helper.save_resolutions(Path("output/manual_review_results"))
    else:
        print("No items found for manual review.")

if __name__ == "__main__":
    main()
