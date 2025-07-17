# Business Logic Assumptions

## CRITICAL: Rent Payment Logic

**STATUS: UNRESOLVED - MUST CLARIFY BEFORE PROCEEDING**

### Questions needing answers:
1. **Who pays the actual rent?**
   - Does Ryan pay the full rent amount to the landlord each month?
   - Does Jordyn pay the full rent amount to the landlord each month?
   - Or do they split the payment to the landlord?

2. **What do the percentage columns mean?**
   - In `Consolidated_Rent_Allocation_20250527.csv`:
     - "Ryan's Rent (43%)" = ?
     - "Jordyn's Rent (57%)" = ?
   - Are these:
     - a) Reimbursement amounts owed between roommates?
     - b) Actual amounts paid to landlord?
     - c) Calculated allocations for tracking purposes?

3. **Reconciliation expectations**
   - Should the sum of Ryan's % + Jordyn's % = 100% of actual rent?
   - How do Zelle payments from Jordyn relate to these percentages?

### Working Hypothesis (TO BE CONFIRMED):
- Ryan pays full rent to landlord
- Rent is allocated 43% Ryan / 57% Jordyn based on some agreement
- Jordyn reimburses Ryan for her portion via Zelle
- CSV tracks this allocation and reimbursement flow

**THIS MUST BE RESOLVED BEFORE BUILDING RECONCILIATION LOGIC**

## Expense Assumptions

### Shared Expenses
- Expenses in `Consolidated_Expense_History_20250622.csv` are shared expenses
- Need to determine split methodology (50/50? Based on usage? Other?)

### Zelle Payments
- Zelle payments from Jordyn to Ryan are reimbursements
- Could be for rent, expenses, or both
- Need clear mapping of what each payment covers

## Data Quality Assumptions

1. **Date formats**: Assume consistent date formatting within each CSV
2. **Currency**: All amounts in USD
3. **Completeness**: CSVs contain all relevant transactions for their respective periods
4. **Uniqueness**: Each row represents a unique transaction/allocation

## Audit Trail Requirements

1. **Every dollar must be traceable** from source CSV to final reconciliation
2. **No black box calculations** - all logic must be documented and verifiable
3. **Immutable source data** - original CSVs never modified, only processed copies
4. **Version control** - All processing steps and logic changes tracked in Git

---
*This document must be updated as assumptions are clarified and confirmed.*
