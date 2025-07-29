#!/usr/bin/env python3
"""Analyze the Phase 4 discrepancy in the financial reconciliation system."""

import pandas as pd

# Load the raw data
df = pd.read_csv('data/raw/Consolidated_Expense_History_20250622.csv')

# Check if allowed != actual (excluding '$ -')
df[' Actual Amount '] = df[' Actual Amount '].str.replace('$', '').str.replace(',', '').str.strip()
df[' Allowed Amount '] = df[' Allowed Amount '].str.replace('$', '').str.replace(',', '').str.strip()

# Convert to numeric where possible
df['actual_numeric'] = pd.to_numeric(df[' Actual Amount '], errors='coerce')
df['allowed_numeric'] = pd.to_numeric(df[' Allowed Amount '], errors='coerce')

# Find differences (excluding where allowed is '$ -' or similar)
mask = (df['allowed_numeric'].notna()) & (df['actual_numeric'].notna()) & (df['allowed_numeric'] != df['actual_numeric'])
differences = df[mask]

print(f'Transactions where allowed_amount differs from actual_amount: {len(differences)}')
print('\nFirst 20 examples:')
for idx, row in differences.head(20).iterrows():
    diff = row["allowed_numeric"] - row["actual_numeric"]
    print(f'  {row["Date of Purchase"]}: {row["Merchant"]} - Actual: ${row["actual_numeric"]:.2f}, Allowed: ${row["allowed_numeric"]:.2f}, Diff: ${diff:.2f}')

# Calculate total impact
total_actual = differences['actual_numeric'].sum()
total_allowed = differences['allowed_numeric'].sum()
print(f'\nTotal actual amount for these transactions: ${total_actual:.2f}')
print(f'Total allowed amount for these transactions: ${total_allowed:.2f}')
print(f'Total difference (allowed - actual): ${total_allowed - total_actual:.2f}')

# Check 2024 only
df['date'] = pd.to_datetime(df['Date of Purchase'], errors='coerce')
mask_2024 = mask & (df['date'].dt.year == 2024) & (df['date'].dt.month <= 9)
differences_2024 = df[mask_2024]

print(f'\n2024 Phase 4 (Jan-Sep) transactions with differences: {len(differences_2024)}')
total_diff_2024 = differences_2024['allowed_numeric'].sum() - differences_2024['actual_numeric'].sum()
print(f'Total difference for 2024 Phase 4: ${total_diff_2024:.2f}')

# This might explain the discrepancy!
print(f'\nIf the system used actual_amount instead of allowed_amount, the error would be: ${total_diff_2024:.2f}')