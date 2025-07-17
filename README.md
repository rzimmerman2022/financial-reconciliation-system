# Financial Reconciliation System

A clean, focused financial reconciliation system built from lessons learned in BALANCE-pyexcel.

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
