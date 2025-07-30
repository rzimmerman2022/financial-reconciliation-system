# Financial Reconciliation System - Gold Standard

A production-ready financial reconciliation system for tracking shared expenses between Ryan and Jordyn, implementing double-entry bookkeeping with comprehensive audit trails.

## Current Status (July 30, 2025)

### System Overview
The **Gold Standard Reconciliation System** is the authoritative implementation, incorporating all lessons learned from previous phases:
- ✅ **Bug-Free**: Fixed the $6,759.16 double-counting error from earlier versions
- ✅ **Correct Field Usage**: Properly uses `allowed_amount` for Phase 4 manual reviews
- ✅ **Manual Review Integration**: Seamless handling of Phase 5+ bank data
- ✅ **Complete Audit Trail**: Every transaction tracked with full history
- ✅ **Data Quality Handling**: Graceful management of encoding errors

### Current Balance
- **FROM_BASELINE Mode**: $8,595.87 (Ryan owes Jordyn)
- **FROM_SCRATCH Mode**: $2,671.12 (Jordyn owes Ryan)
- **Baseline**: $1,577.08 (Jordyn owes Ryan) as of Sept 30, 2024

## Quick Start

### Basic Reconciliation
```bash
# Run from baseline (recommended)
python gold_standard_reconciliation.py --mode from_baseline

# Run from scratch (full history)
python gold_standard_reconciliation.py --mode from_scratch
```

### With Manual Review (for Phase 5+ data)
```bash
# Complete workflow with manual review
python run_reconciliation_with_review.py
```

## Architecture

### Core Components
- **`gold_standard_reconciliation.py`** - Main reconciliation engine
- **`accounting_engine.py`** - Double-entry bookkeeping implementation
- **`description_decoder.py`** - Transaction pattern recognition
- **`manual_review_system.py`** - SQLite-based review tracking
- **`run_reconciliation_with_review.py`** - Orchestrates complete workflow

### Data Flow
```
Phase 4 Data (with allowed_amount) → Direct Processing → Accounting Engine
Phase 5+ Data (bank CSVs) → Manual Review → User Decision → Accounting Engine
```

## Data Sources

### Phase 4 (Through Sept 30, 2024)
- **Consolidated Expense History**: Pre-reviewed with `allowed_amount` field
- **Status**: Complete with manual annotations

### Phase 5+ (Oct 1, 2024 onwards)
- **Ryan's Data**: MonarchMoney + RocketMoney CSVs
- **Jordyn's Data**: Chase + WellsFargo + Discover CSVs
- **Status**: Requires manual review for categorization

### Known Data Issues
- 156 transactions in Jordyn's Chase data have missing amounts (encoding errors)
- Chase data ends March 13, 2025 (missing recent months)

## Key Features

### 1. Description Decoder
Automatically interprets custom transaction codes:
- "2x to calculate" = Full reimbursement (not doubling)
- Gift detection (birthdays, Christmas)
- Mathematical expression evaluation
- Exclusion patterns ("remove", "deduct")

### 2. Manual Review System
For Phase 5+ bank data:
- Interactive categorization interface
- Custom amount overrides
- Split type selection (50/50, custom, full)
- Personal expense marking
- Pattern learning for future automation

### 3. Comprehensive Audit Trail
Every transaction tracked with:
- Original amount vs allowed amount
- Category and split decisions
- Running balance after each transaction
- Data quality issues flagged

## Output Structure

```
output/
├── gold_standard/
│   ├── summary.json              # Machine-readable results
│   ├── reconciliation_report.txt # Human-readable report
│   ├── audit_trail.csv          # Complete transaction log
│   ├── accounting_ledger.csv    # Double-entry ledger
│   ├── manual_review_required.csv
│   └── data_quality_issues.csv
└── gold_standard_with_manual_review/
    └── [same structure after reviews]
```

## Critical Business Rules

### Rent Payments
**JORDYN ALWAYS PAYS THE FULL RENT UPFRONT**
- See `CRITICAL_RENT_RULES.md` for detailed explanation
- This is fundamental to the reconciliation logic

### Transaction Processing
1. **Phase 4 Data**: Uses `allowed_amount` field directly (pre-reviewed)
2. **Phase 5+ Data**: Requires manual review for categorization
3. **Personal Expenses**: Marked with `allowed_amount = "$ -"` or via review
4. **Settlements**: Zelle/Venmo payments reduce outstanding balances

## Testing

```bash
# Run comprehensive test suite
python test_gold_standard.py

# Test accounting engine
python test_accounting_engine.py

# Test description decoder
python test_description_decoder.py
```

## Documentation

### Current Documentation
- **`GOLD_STANDARD_WORKFLOW_COMPLETE.md`** - Exhaustive workflow documentation
- **`AI_HANDOVER_CONTEXT.md`** - Technical implementation details
- **`CRITICAL_RENT_RULES.md`** - Rent payment business logic
- **`CURRENT_STATUS_AND_ISSUES.md`** - Latest system status
- **`FINAL_RECONCILIATION_REPORT.md`** - Results summary

### Archived Documentation
Old documentation has been moved to the `archive/` folder for reference.

## Troubleshooting

### Common Issues

1. **Unicode Errors in Chase Data**
   - System automatically tries multiple encodings
   - Missing amounts flagged for manual review

2. **Balance Mismatches**
   - Check `audit_trail.csv` for calculation details
   - Verify manual review decisions
   - Ensure no duplicate transactions

3. **Manual Review Not Working**
   - Check `phase5_manual_reviews.db` exists
   - Verify transactions have non-zero amounts
   - Ensure proper date range selection

## Next Steps

1. **Complete Manual Review** of the 156 missing-amount transactions
2. **Obtain Missing Data** for Jordyn's Chase account (March-July 2025)
3. **Monthly Reconciliation** going forward to prevent backlogs
4. **Pattern Training** to reduce manual review burden

## Support

For questions about:
- Business logic → See `CRITICAL_RENT_RULES.md`
- Technical details → See `AI_HANDOVER_CONTEXT.md`
- Workflow → See `GOLD_STANDARD_WORKFLOW_COMPLETE.md`

---
Last Updated: July 30, 2025  
System Version: GOLD STANDARD 1.0.0