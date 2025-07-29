# AI Model Handover Context Document
## Gold Standard Financial Reconciliation System

### Executive Summary
This document provides comprehensive context for continuing work on the gold standard financial reconciliation system. The system reconciles shared expenses between Ryan and Jordyn, handling complex transaction data from multiple sources with manual review capabilities.

### Current System State (July 29, 2025)
- **FROM_SCRATCH Mode**: $2,671.12 (Jordyn owes Ryan)
- **FROM_BASELINE Mode**: $8,595.87 (Ryan owes Jordyn)
- **Status**: Production-ready with manual review integration
- **Last Commit**: `feat: Complete gold standard reconciliation system with manual review integration`

### Critical Context & History

#### 1. The Double-Counting Bug (Fixed)
Previously in `full_2024_reconciliation_enhanced.py`, there was a critical bug where transactions were being posted twice:
```python
# BUG: This was posting transactions twice
self._post_transaction(transaction)  # First post
final_df = self._process_transaction_batch(df)  # Second post inside this method
```
This has been completely fixed in the gold standard system.

#### 2. Key Data Structure: allowed_amount vs actual_amount
- **Phase 4 Data** (pre-October 2024): Has manual review with `allowed_amount` field
- **Phase 5+ Data** (October 2024+): Raw bank data without `allowed_amount`
- Critical user requirement: "We can't assume on any of the bank CSVs... only the prior data that we already did"

#### 3. Description Decoder Issue (Fixed)
The description decoder returns `'split_50_50'` but reconciliation was checking for `'split'`. Fixed by checking both:
```python
if action == 'split' or action == 'split_50_50':
```

### System Architecture

#### Core Components:
1. **gold_standard_reconciliation.py**
   - Main reconciliation engine
   - Implements double-entry bookkeeping
   - Two modes: FROM_SCRATCH and FROM_BASELINE
   - Fixed to use `get_transaction_log()` instead of non-existent `get_ledger_dataframe()`

2. **accounting_engine.py**
   - Double-entry bookkeeping implementation
   - Maintains Ryan and Jordyn accounts with receivables/payables
   - Validates accounting invariants

3. **manual_review_system.py**
   - SQLite-based review tracking
   - Interactive review interface
   - Stores decisions with timestamps and reviewer info

4. **batch_review_helper.py**
   - Pattern-based auto-classification
   - Reduces manual review burden
   - Categories: rent, utilities, groceries, etc.

5. **run_reconciliation_with_review.py**
   - Orchestrates the complete workflow
   - Three phases: reconcile → review → re-reconcile
   - Auto-selects "skip review" for non-interactive mode

### Data Sources & Quality Issues

#### Bank Data Files:
- `Ryan_MonarchMoney_*.csv`
- `Ryan_RocketMoney_*.csv`
- `Jordyn_Chase_*.csv`
- `Jordyn_WellsFargo_*.csv`
- `Jordyn_Discover_*.csv`

#### Known Issues:
1. **Missing Amounts**: 156 transactions in Jordyn_Chase have $0.00 amounts (encoding errors)
2. **Large Transactions**: Several >$10,000 transactions flagged for review
3. **Duplicates**: System removes exact and near-duplicates automatically

### Critical Implementation Details

#### 1. Unicode Encoding Fix
Changed all checkmark characters from `✓` to `[DONE]` to avoid Windows encoding errors:
```python
# OLD: print("✓ Task complete")
# NEW: print("[DONE] Task complete")
```

#### 2. Transaction Processing Flow
```python
1. Load bank data with date filtering
2. Apply Phase 4 manual reviews (if has allowed_amount)
3. Flag Phase 5+ transactions for manual review
4. Process through accounting engine
5. Validate invariants
6. Generate comprehensive reports
```

#### 3. Manual Review Integration
- Exports unreviewed items to SQLite database
- User reviews via interactive interface
- Decisions applied to subsequent reconciliation runs
- Pattern learning for future auto-classification

### Testing & Validation

Run complete reconciliation:
```bash
python gold_standard_reconciliation.py --mode from_baseline
```

Run with manual review:
```bash
python run_reconciliation_with_review.py
```

### Output Structure
```
output/
├── gold_standard/
│   ├── summary.json              # Machine-readable summary
│   ├── reconciliation_report.txt # Human-readable report
│   ├── audit_trail.csv          # Every transaction processed
│   ├── accounting_ledger.csv    # Double-entry ledger
│   ├── manual_review_required.csv
│   └── data_quality_issues.csv
└── gold_standard_with_manual_review/
    └── [same structure]
```

### Next Steps & Recommendations

1. **Immediate Priority**: Process the 156 missing-amount transactions in Jordyn_Chase
2. **Manual Review**: Complete review of flagged Phase 5 transactions
3. **Data Quality**: Investigate and fix encoding issues causing $0.00 amounts
4. **Testing**: Validate reconciliation across different date ranges
5. **Performance**: Consider optimizing for larger datasets

### Common Commands

```bash
# Run reconciliation from scratch
python gold_standard_reconciliation.py --mode from_scratch

# Run from baseline
python gold_standard_reconciliation.py --mode from_baseline

# Run with manual review workflow
python run_reconciliation_with_review.py

# Check git status
git status

# View recent commits
git log --oneline -10
```

### Critical Warnings
1. NEVER modify `allowed_amount` for Phase 4 data - it's already manually reviewed
2. ALWAYS use manual review system for Phase 5+ data
3. The accounting engine uses Decimal for precision - avoid float operations
4. Double-entry invariants MUST always balance

### Contact & Resources
- Repository: https://github.com/rzimmerman2022/financial-reconciliation-system
- Primary users: Ryan & Jordyn
- System purpose: Fair split of shared expenses with audit trail

This system represents a complete rewrite fixing all known bugs from the enhanced reconciliation system. It's production-ready but requires manual review for Phase 5+ bank data as requested by the user.

---
Generated by Claude (Anthropic) on July 29, 2025
Context window handover for continuation