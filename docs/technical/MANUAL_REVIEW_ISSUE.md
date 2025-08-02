# Manual Review System Issue

**Date Discovered**: July 31, 2025  
**Severity**: HIGH  
**Status**: Documented, Not Fixed

## Issue Description

The manual review export system is incorrectly filtering out transactions with zero amounts, causing a massive discrepancy between flagged transactions and those available for review.

## Current Behavior

1. Reconciliation identifies **158 transactions** requiring manual review
2. Export process filters out all transactions with `amount == 0`
3. Only **2 transactions** are exported to the review database
4. **156 transactions** (mostly Chase encoding errors) are silently dropped

## Code Location

File: `bin/run-with-review`  
Lines: 91-93

```python
# Skip if it's just a data quality issue (missing amount)
if item.get('amount', 0) == 0:
    continue
```

## Impact

- 98.7% of transactions requiring review are not accessible
- Chase Bank transactions with encoding errors cannot be categorized
- Manual review process is incomplete
- Reconciliation accuracy is compromised

## Expected Behavior

ALL transactions flagged for manual review should be exported to the database, regardless of amount. The manual review process should allow users to:

1. View the transaction description
2. Determine the correct amount (if missing)
3. Categorize the transaction appropriately
4. Make decisions on zero-amount transactions

## Temporary Workaround

Users can manually review the CSV file at:
```
output/gold_standard/manual_review_required.csv
```

This file contains all 158 transactions that need review.

## Recommended Fix

Remove the zero-amount filter from `_export_to_review_system()`:

```python
def _export_to_review_system(self):
    """Export flagged transactions to manual review database."""
    print("\nExporting transactions to manual review system...")
    
    count = 0
    for item in self.reconciler.manual_review_items:
        # Export ALL transactions, including zero amounts
        review_id = self.review_system.add_transaction_for_review(
            date=item['date'],
            description=item['description'],
            amount=Decimal(str(item.get('amount', 0))),
            payer=item['payer'],
            source=item.get('source', 'Unknown')
        )
        count += 1
        
    print(f"[DONE] Exported {count} transactions for manual review")
```

## Related Files

- `output/gold_standard/manual_review_required.csv` - Contains all 158 transactions
- `data/phase5_manual_reviews.db` - Currently only has 2 transactions
- `output/gold_standard/data_quality_issues.csv` - Shows the 156 missing amount issues

---

**Note**: This is a critical bug that affects the core functionality of the manual review system.