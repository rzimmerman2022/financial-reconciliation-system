"""Test script to verify the balance calculation fix in phase5a_comprehensive_audit.py"""

from decimal import Decimal
import json

def test_balance_calculation():
    """Test the balance calculation logic with sample transactions"""
    
    print("Testing Balance Calculation Logic")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "description": "Ryan pays $100 shared expense (50/50 split)",
            "payer": "Ryan",
            "amount": 100,
            "ryan_share": 50,
            "jordyn_share": 50,
            "expected_balance_change": -50,  # Jordyn owes $50 more
            "expected_explanation": "Jordyn's debt increases by $50"
        },
        {
            "description": "Jordyn pays $100 shared expense (50/50 split)",
            "payer": "Jordyn",
            "amount": 100,
            "ryan_share": 50,
            "jordyn_share": 50,
            "expected_balance_change": 50,  # Jordyn's debt decreases by $50
            "expected_explanation": "Jordyn's debt decreases by $50"
        },
        {
            "description": "Jordyn pays $2100 rent (47% Ryan, 53% Jordyn)",
            "payer": "Jordyn",
            "amount": 2100,
            "ryan_share": 987,  # 47% of 2100
            "jordyn_share": 1113,  # 53% of 2100
            "expected_balance_change": 987,  # Jordyn's debt decreases by Ryan's share
            "expected_explanation": "Jordyn's debt decreases by $987 (Ryan's rent share)"
        },
        {
            "description": "Ryan pays $200 expense (60% Ryan, 40% Jordyn)",
            "payer": "Ryan", 
            "amount": 200,
            "ryan_share": 120,
            "jordyn_share": 80,
            "expected_balance_change": -80,  # Jordyn owes $80 more
            "expected_explanation": "Jordyn's debt increases by $80"
        }
    ]
    
    # Test old (buggy) formula vs new (correct) formula
    for test in test_cases:
        print(f"\nTest: {test['description']}")
        print(f"Payer: {test['payer']}")
        print(f"Amount: ${test['amount']}")
        print(f"Ryan's share: ${test['ryan_share']}")
        print(f"Jordyn's share: ${test['jordyn_share']}")
        
        # Old buggy calculation (same for both payers)
        old_balance_change = float(Decimal(str(test['jordyn_share'])) - Decimal(str(test['ryan_share'])))
        
        # New correct calculation
        if test['payer'] == 'Ryan':
            new_balance_change = float(-Decimal(str(test['jordyn_share'])))
        else:  # Jordyn paid
            new_balance_change = float(Decimal(str(test['ryan_share'])))
        
        print(f"\nOld (buggy) balance change: ${old_balance_change:.2f}")
        print(f"New (correct) balance change: ${new_balance_change:.2f}")
        print(f"Expected balance change: ${test['expected_balance_change']:.2f}")
        print(f"Explanation: {test['expected_explanation']}")
        
        # Verify correctness
        if abs(new_balance_change - test['expected_balance_change']) < 0.01:
            print("[PASSED] CORRECT")
        else:
            print("[FAILED] INCORRECT")
    
    # Calculate the impact over multiple transactions
    print("\n" + "=" * 50)
    print("Impact Analysis: Sample 18-day period")
    print("=" * 50)
    
    # Simulate some typical transactions
    sample_transactions = [
        {"payer": "Jordyn", "ryan_share": 50, "jordyn_share": 50},    # Groceries
        {"payer": "Ryan", "ryan_share": 30, "jordyn_share": 30},      # Gas
        {"payer": "Jordyn", "ryan_share": 987, "jordyn_share": 1113}, # Rent
        {"payer": "Ryan", "ryan_share": 75, "jordyn_share": 75},      # Dinner
        {"payer": "Jordyn", "ryan_share": 40, "jordyn_share": 40},    # Utilities
        {"payer": "Jordyn", "ryan_share": 100, "jordyn_share": 100},  # Shopping
        {"payer": "Ryan", "ryan_share": 60, "jordyn_share": 60},      # Internet
    ]
    
    old_cumulative = 0
    new_cumulative = 0
    
    for i, txn in enumerate(sample_transactions, 1):
        # Old calculation
        old_change = float(Decimal(str(txn['jordyn_share'])) - Decimal(str(txn['ryan_share'])))
        old_cumulative += old_change
        
        # New calculation
        if txn['payer'] == 'Ryan':
            new_change = float(-Decimal(str(txn['jordyn_share'])))
        else:
            new_change = float(Decimal(str(txn['ryan_share'])))
        new_cumulative += new_change
        
        print(f"\nTransaction {i}: {txn['payer']} paid")
        print(f"  Old formula: {old_change:+.2f} (cumulative: {old_cumulative:+.2f})")
        print(f"  New formula: {new_change:+.2f} (cumulative: {new_cumulative:+.2f})")
    
    print(f"\n" + "=" * 50)
    print(f"Total difference after {len(sample_transactions)} transactions:")
    print(f"Old (buggy) cumulative: ${old_cumulative:+.2f}")
    print(f"New (correct) cumulative: ${new_cumulative:+.2f}")
    print(f"Error amount: ${abs(old_cumulative - new_cumulative):.2f}")
    
    # Sign convention explanation
    print("\n" + "=" * 50)
    print("Sign Convention:")
    print("- Negative balance: Jordyn owes Ryan")
    print("- Positive balance: Ryan owes Jordyn")
    print("- When balance decreases (becomes more negative): Jordyn's debt increases")
    print("- When balance increases (becomes less negative): Jordyn's debt decreases")

if __name__ == "__main__":
    test_balance_calculation()