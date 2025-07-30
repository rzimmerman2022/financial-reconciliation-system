# Business Assumptions

## Shared Expense Model

### Core Principle
Ryan and Jordyn split shared expenses 50/50 unless otherwise specified.

### Shared Expense Categories
- **Rent**: Always 50/50 split
- **Utilities**: 50/50 split
- **Groceries**: 50/50 split (when shopping together)
- **Household Items**: 50/50 split
- **Joint Dining**: 50/50 split

### Personal Expenses
- Individual purchases for personal use
- Marked as personal in transaction descriptions
- Not subject to splitting

## Payment Arrangements

### Rent Payments
- **Who Pays**: Jordyn pays full amount upfront
- **Reimbursement**: Ryan owes 50% to Jordyn
- **Frequency**: Monthly

### Utility Payments
- **Who Pays**: Various (whoever receives the bill)
- **Reimbursement**: 50/50 split
- **Frequency**: Monthly

### Settlement Payments
- **Zelle/Venmo**: Used for reimbursements between parties
- **Direction**: Usually Ryan → Jordyn (based on typical balance)
- **Frequency**: As needed when balance grows large

## Data Processing Assumptions

### Phase 4 Data (Through Sept 30, 2024)
- All transactions manually reviewed
- `allowed_amount` field reflects review decisions
- No further categorization needed

### Phase 5+ Data (Oct 1, 2024 onwards)
- Raw bank transaction data
- Requires manual categorization
- System learns patterns for future automation

### Transaction Descriptions
- Custom codes used for complex scenarios
- "2x to calculate" means full reimbursement (not double)
- Mathematical expressions evaluated literally
- Gift transactions excluded from splitting

## Baseline Assumptions

### Starting Point
- **Date**: September 30, 2024
- **Amount**: $1,577.08 (Jordyn owes Ryan)
- **Source**: Manual calculation from Phase 4 data

### Data Integrity
- All amounts in USD
- Dates in consistent format
- No duplicate transactions across sources

## Future Considerations

### Changing Arrangements
- Split percentages may change over time
- New expense categories may emerge
- Payment methods may evolve

### Data Sources
- Bank exports primary source for recent data
- Manual entry for cash transactions
- Receipt scanning possible future enhancement

---

Last Updated: July 30, 2025