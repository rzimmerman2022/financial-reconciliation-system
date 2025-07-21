# VERBOSE AUDIT TRAIL GUIDE

## File Location: `output/VERBOSE_AUDIT_TRAIL.csv`

## Overview
This is the **most detailed audit trail** available, containing every single transaction from January 2, 2024 through September 30, 2024 with complete explanations.

## Final Result: **Jordyn owes Ryan $9,967.98**

---

## Column Descriptions

| Column | Description |
|--------|-------------|
| **Transaction_ID** | Unique ID (TX_0001 to TX_1143) |
| **Date** | Transaction date (YYYY-MM-DD) |
| **Description** | Transaction description with decoded action |
| **Paid_By** | Who paid the expense (Ryan/Jordyn) |
| **Total_Amount** | Full transaction amount |
| **Ryan_Share** | How much Ryan owes for this transaction |
| **Jordyn_Share** | How much Jordyn owes for this transaction |
| **Running_Balance** | Current balance after this transaction |
| **Balance_Direction** | Who owes whom at this point |
| **Transaction_Type** | expense/rent/zelle |
| **Decoded_Action** | How the expense was categorized |
| **Category** | Transaction category |
| **Detailed_Explanation** | **VERBOSE explanation of what happened** |
| **Balance_Change** | How much the balance changed (+/-) |
| **Previous_Balance** | Balance before this transaction |

---

## How to Read the Balance

- **Positive Balance** (Jordyn → Ryan): Jordyn owes Ryan money
- **Negative Balance** (Ryan → Jordyn): Ryan owes Jordyn money
- **Running_Balance** shows the current total after each transaction

## Example Transactions

### Expense Example (TX_0001):
- Ryan paid $37.04 for groceries
- Split 50/50: Ryan already paid his $18.52 share
- Jordyn owes Ryan $18.52
- **Result**: Balance goes from $0.00 to $18.52 (Jordyn owes Ryan)

### Zelle Example (TX_1143):
- Jordyn sent $800 to Ryan via Zelle
- This is a settlement payment
- **Result**: Balance goes from $10,767.98 to $9,967.98
- Jordyn still owes Ryan, but $800 less now

## Key Insights

1. **Every Transaction Tracked**: 1,143 transactions from 2024 only
2. **Running Balance**: Shows how debt evolved over time
3. **Detailed Explanations**: Plain English explanation for each transaction
4. **Mathematical Verification**: Every balance change is calculated and shown

## How Splits Work

- **split_50_50**: Each person owes half, payer gets reimbursed for other's share
- **full_reimbursement**: Non-payer owes entire amount to payer
- **gift**: Payer covers full cost, no reimbursement
- **personal_X**: Individual expense, that person responsible
- **rent**: Jordyn pays full amount, Ryan owes his percentage share

---

**This file provides complete transparency into how we arrived at the final balance of $9,967.98.**