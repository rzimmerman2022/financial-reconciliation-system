# CRITICAL RENT PAYMENT RULES - MUST READ

## IMPORTANT: How Rent Works in This System

### The Key Rule: JORDYN ALWAYS PAYS FULL RENT

1. **Jordyn pays 100% of the rent every month** to the landlord/property management
2. **Ryan owes Jordyn his portion** (usually 43% or 47% as specified in the CSV)
3. **This is NOT a split payment** - Jordyn fronts the entire amount

### Why This Matters for Reconciliation

Since Jordyn pays the full rent upfront:
- When processing rent transactions, Ryan OWES his portion to Jordyn
- Jordyn does NOT owe anything for rent (she already paid)
- This effectively reduces what Jordyn owes Ryan from other expenses

### Example
- Total rent: $2,119.72
- Ryan's portion (43%): $911.48
- Jordyn's portion (57%): $1,208.24

**What happens:**
1. Jordyn pays $2,119.72 to landlord
2. Ryan now owes Jordyn $911.48
3. This $911.48 is added to Ryan's balance (what he owes)

### In the Code

In `transaction_processor.py`, the `process_rent()` method:
```python
ryan_owes=rent['ryan_amount'],  # Ryan owes his portion
jordyn_owes=0,  # Jordyn owes nothing (she paid)
paid_by='Jordyn',  # ALWAYS Jordyn
```

### DO NOT CHANGE THIS BEHAVIOR

This is a fundamental rule of how Ryan and Jordyn handle their finances. Any AI model or developer working on this system must maintain this logic.

## Summary for AI Models

When you see rent transactions:
1. Jordyn is ALWAYS the payer
2. Ryan ALWAYS owes his portion to Jordyn
3. Never treat rent as a "split" expense
4. Never assign any rent amount to what Jordyn owes

This has been explicitly confirmed by the user and must not be changed.