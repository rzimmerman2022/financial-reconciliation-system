# Critical Architecture Issues and Solutions
**Date:** July 28, 2025  
**Issue:** Loss of Manual Review Context Between Phases

## The Core Problem

We have two fundamentally different data structures:

### 1. Phase 4 Data (Consolidated Expense History)
- **Has manual review**: `allowed_amount` field contains reviewed amounts
- **Processing rules**: 
  - `allowed_amount = "$ -"` → Personal expense (100% to payer)
  - `allowed_amount < actual_amount` → Partial reimbursement
  - `allowed_amount = actual_amount` → Normal shared expense
- **Example**: Actual=$50, Allowed=$20 → Only $20 is shared

### 2. Phase 5+ Data (Raw Bank Transactions)
- **No manual review**: Only has transaction amount
- **No allowed_amount field**: Can't determine if expense should be shared
- **No processing instructions**: Lost all context about how to split

## How Context Was Lost

1. **Wrong field used**: Enhanced reconciliation used `actual_amount` instead of `allowed_amount`
2. **Pattern mismatch**: Code looked for "2x to calculate" text patterns that don't exist
3. **Data structure change**: Phase 5 uses raw bank data without manual review fields

## Why The Baseline Is Wrong

The $12,836.06 discrepancy occurs because:
- Using `actual_amount` processes ALL expenses as shared
- Using `allowed_amount` correctly excludes personal expenses
- Hundreds of transactions marked as personal (allowed = "$ -") were incorrectly shared

## Solution Architecture

### Immediate Fix for Phase 4
```python
# CORRECT - Use allowed_amount
'allowed_amount': 'amount'

# Process exclusions
if allowed_amount == "$ -" or allowed_amount == 0:
    # Personal expense - 100% to payer
    pass
```

### Long-term Solution for Phase 5+

1. **Manual Review Pipeline**
   ```python
   class TransactionReviewer:
       def review_transaction(self, transaction):
           # Auto-classify obvious patterns
           if self.is_personal_expense(transaction):
               return {'allowed_amount': 0, 'category': 'personal'}
           
           # Flag for manual review
           if self.needs_review(transaction):
               return {'needs_review': True}
           
           # Default to full amount shared
           return {'allowed_amount': transaction['amount']}
   ```

2. **Persistent Review Database**
   ```sql
   CREATE TABLE transaction_reviews (
       transaction_id TEXT PRIMARY KEY,
       date DATE,
       description TEXT,
       actual_amount DECIMAL,
       allowed_amount DECIMAL,
       category TEXT,
       review_notes TEXT,
       reviewed_by TEXT,
       reviewed_date TIMESTAMP
   );
   ```

3. **Review UI Requirements**
   - Show transaction details
   - Allow marking as personal/shared/partial
   - Set allowed_amount
   - Add review notes
   - Track review history

## Preventing Future Context Loss

1. **Data Validation**
   - Assert that Phase 4 calculations match known baseline
   - Flag when actual_amount ≠ allowed_amount
   - Warn when processing raw data without review

2. **Clear Data Flow**
   ```
   Raw Bank Data → Manual Review → Reviewed Data → Reconciliation
                                    (with allowed_amount)
   ```

3. **Testing Strategy**
   - Unit tests for allowed_amount = "$ -" → personal expense
   - Integration tests comparing actual vs allowed processing
   - Regression tests against known baselines

4. **Documentation**
   - Document the allowed_amount convention
   - Explain why "2x to calculate" doesn't appear in data
   - Map business rules to data fields

## Critical Insight

The "2x to calculate" and other manual annotations were a **workaround** for a system limitation. The REAL implementation was through the `allowed_amount` field:
- Setting allowed = 0 achieved full reimbursement
- Setting allowed < actual achieved partial reimbursement
- The text descriptions were just notes, not processing instructions

## Next Steps

1. Fix enhanced reconciliation to use allowed_amount properly
2. Build manual review system for Phase 5+ data
3. Create test suite validating allowed_amount processing
4. Document the review workflow for ongoing use

Without solving this architectural issue, every future reconciliation will be wrong because raw bank data lacks the critical allowed_amount field that captures manual review decisions.