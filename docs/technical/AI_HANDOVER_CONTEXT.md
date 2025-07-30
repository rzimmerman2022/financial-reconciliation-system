# AI Handover Context

## System Architecture

### Core Components

1. **Reconciliation Engine** (`src/core/reconciliation_engine.py`)
   - Main orchestration logic
   - Handles both FROM_BASELINE and FROM_SCRATCH modes
   - Coordinates all data loading and processing

2. **Accounting Engine** (`src/core/accounting_engine.py`)
   - Double-entry bookkeeping implementation
   - Maintains accounting invariants
   - Generates comprehensive audit trails

3. **Description Decoder** (`src/core/description_decoder.py`)
   - Parses transaction descriptions
   - Extracts metadata and amounts
   - Handles mathematical expressions

4. **Manual Review System** (`src/review/manual_review_system.py`)
   - SQLite-based review tracking
   - Interactive review interface
   - Persistent review decisions

## Data Processing Pipeline

### Phase 4 Processing (Through Sept 30, 2024)
```
test-data/legacy/ → Data Loader → Description Decoder → Accounting Engine → Output
```
- Uses `allowed_amount` field for manual review decisions
- Pre-processed and validated data

### Phase 5+ Processing (Oct 1, 2024 onwards)
```
test-data/bank-exports/ → Data Loader → Manual Review → Accounting Engine → Output
```
- Requires human categorization
- Pattern matching for automation  
- Review decisions stored in data/phase5_manual_reviews.db

## Key Technical Decisions

### 1. Baseline vs From-Scratch
- **FROM_BASELINE**: Starts from known balance point (Sept 30, 2024)
- **FROM_SCRATCH**: Processes all historical data
- Baseline approach recommended for performance

### 2. Data Quality Handling
- Multiple encoding attempts for problematic files
- Graceful handling of missing amounts
- Comprehensive error logging

### 3. Manual Review Integration
- Async processing with user intervention
- Pattern learning for future automation
- Multiple review interfaces (CLI, web, Excel)

## Critical Implementation Details

### Double-Entry Bookkeeping
```python
# Every transaction creates balanced entries
debit_account = "Shared Expenses"
credit_account = "Personal Account"
amount = transaction_amount / 2  # For 50/50 splits
```

### Balance Calculation
```python
# Ryan's balance = Sum of all debits to Ryan - Sum of all credits to Ryan
balance = sum(ryan_debits) - sum(ryan_credits)
```

### Transaction Processing
1. Load and validate data
2. Apply description decoding
3. Create accounting entries
4. Validate invariants
5. Generate audit trail

## Known Issues and Gotchas

### 1. Unicode Encoding
- Chase bank data has encoding issues
- System tries multiple encodings automatically
- Some transactions may have missing amounts

### 2. Date Handling
- Consistent datetime parsing across all sources
- Timezone handling for bank data

### 3. Decimal Precision
- All monetary amounts use Python Decimal
- Prevents floating-point precision errors
- Critical for accounting accuracy

## Testing Strategy

### Unit Tests
- Core business logic validation
- Accounting invariant checks
- Description decoder patterns

### Integration Tests
- End-to-end data processing
- Manual review workflow
- Report generation

## Monitoring and Observability

### Audit Trail
- Every transaction logged with metadata
- Running balance tracking
- Decision rationale recorded

### Data Quality Reports
- Encoding issues flagged
- Missing data identified
- Processing errors captured

## Performance Considerations

### Memory Usage
- Processes data in chunks for large datasets
- Efficient pandas operations
- Minimal memory footprint

### Processing Speed
- FROM_BASELINE mode for faster runs
- Parallel processing where possible
- Optimized SQL queries for reviews

---

Last Updated: July 30, 2025