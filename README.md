# Financial Reconciliation System

A clean, focused financial reconciliation system built from lessons learned in BALANCE-pyexcel.

## 🎯 Phase 1 Complete: Description Language Decoder

**Status: ✅ OPERATIONAL**

The core description decoder has been successfully implemented and tested. This system correctly interprets custom transaction description codes that previous attempts failed to understand.

### Key Features:
- **Smart Pattern Recognition**: Automatically detects and interprets custom description codes
- **"2x to calculate" Logic**: Correctly handles full reimbursement patterns (not mathematical doubling)
- **Gift Detection**: Identifies birthday, Christmas, and other gift transactions
- **Mathematical Expressions**: Safely evaluates and processes calculation patterns
- **Exclusion Handling**: Processes "remove" and "deduct" patterns correctly
- **Priority System**: Ensures patterns are applied in correct order of precedence

### Files:
- `description_decoder.py` - Main decoder module
- `test_description_decoder.py` - Comprehensive unit tests (12 test cases)
- `demo_description_decoder.py` - Real data demonstration
- `PHASE1_COMPLETE_SUMMARY.md` - Detailed implementation summary

## Architecture

This project follows a clean, modular approach:

`
â”œâ”€â”€ data/
â”‚   â”œâ”€â”€ raw/           # Original CSV files
â”‚   â””â”€â”€ processed/     # Cleaned data
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ loaders/       # CSV loading modules
â”‚   â”œâ”€â”€ processors/    # Data cleaning/validation  
â”‚   â””â”€â”€ reconcilers/   # Reconciliation logic
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ assumptions.md    # Business logic assumptions
â”‚   â”œâ”€â”€ data_sources.md   # CSV specifications
â”‚   â””â”€â”€ audit_trail.md    # Audit requirements
â”œâ”€â”€ tests/             # Unit tests
â”œâ”€â”€ output/            # Generated reports
â””â”€â”€ scripts/           # Utility scripts
`

## Key Principles

1. **One CSV at a time**: Process each data source independently first
2. **Clear assumptions**: Document all business logic upfront
3. **Full audit trails**: Every transaction must be traceable

## ⚠️ CRITICAL: Rent Payment Rules

**JORDYN ALWAYS PAYS THE FULL RENT UPFRONT**

See [CRITICAL_RENT_RULES.md](CRITICAL_RENT_RULES.md) for detailed explanation. This is a fundamental rule that must be understood by all developers and AI models working on this system.
4. **Clean separation**: Keep old experimental work separate

## Data Sources

### Current Files in data/raw/:
- `Consolidated_Expense_History_20250622.csv` - Shared expenses
- `Consolidated_Rent_Allocation_20250527.csv` - Rent payments and allocations
- `Zelle_From_Jordyn_Final.csv` - Zelle payments from Jordyn

## Critical Questions to Resolve

### Rent Payment Logic (HIGHEST PRIORITY):
1. Does Ryan pay the full rent each month?
2. Does Jordyn pay the full rent each month? 
3. What do the CSV columns "Ryan's Rent (43%)" and "Jordyn's Rent (57%)" actually represent?

## Implementation Plan

### Phase 1: Data Understanding
- [ ] Analyze each CSV structure individually
- [ ] Document field meanings and assumptions
- [ ] Resolve rent payment logic questions

### Phase 2: Single CSV Processors  
- [ ] Build expense CSV processor (simplest)
- [ ] Build rent CSV processor (once assumptions clear)
- [ ] Build Zelle CSV processor

### Phase 3: Integration
- [ ] Combine processors with reconciliation logic
- [ ] Generate comprehensive audit trails
- [ ] Create final reports

## Development Notes

This project was created by migrating essential files from the original BALANCE-pyexcel experiment. The old project remains at `c:\BALANCE\BALANCE-pyexcel` for reference.

Created: July 16, 2025
