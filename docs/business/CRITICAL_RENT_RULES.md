# Critical Rent Rules

## Core Business Rule

**JORDYN ALWAYS PAYS THE FULL RENT UPFRONT**

This is the fundamental business rule that drives all rent-related reconciliation logic.

## Why This Rule Exists

1. **Practical Arrangement**: Jordyn handles the rent payment to the landlord
2. **Simplifies Accounting**: Single source of rent payment records
3. **Consistent Process**: Same approach used throughout the relationship

## Implementation Details

### Phase 4 Data (Pre-Oct 2024)
- Rent payments already processed and annotated
- `allowed_amount` field reflects 50/50 split decisions
- No additional processing needed

### Phase 5+ Data (Oct 2024 onwards)  
- Bank records show Jordyn's full rent payments
- System automatically applies 50/50 split
- Ryan's portion calculated as liability to Jordyn

## Reconciliation Impact

When Jordyn pays rent:
1. **Debit**: Rent Expense (full amount)
2. **Credit**: Jordyn's Personal Account (full amount)
3. **Accounting Entry**: Ryan owes 50% to Jordyn

## Example

If monthly rent is $2,000:
- Jordyn pays $2,000 to landlord
- System records $1,000 as Ryan's share
- Running balance increases Ryan's debt to Jordyn by $1,000

## Important Notes

- This rule applies to ALL rent payments
- No exceptions or special cases
- Critical for accurate balance calculations
- Must be maintained in any system modifications

---

Last Updated: July 30, 2025