# API Reference Documentation

**Last Updated:** August 10, 2025  
**Version:** 6.0.0  
**Description:** Complete API specification for the Financial Reconciliation System

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Core APIs](#core-apis)
- [Web Interface APIs](#web-interface-apis)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Overview

The Financial Reconciliation System provides both programmatic APIs for automation and web APIs for user interfaces. The system is designed to be RESTful where applicable, with clear separation between data operations and user interface operations.

### API Types

1. **Core Python APIs**: Direct programmatic access to reconciliation functionality
2. **Web APIs**: HTTP endpoints for web interface interactions
3. **CLI APIs**: Command-line interface for automation and scripting

### Base URLs

- **Web API**: `http://localhost:5000/api/` (development)
- **Web API**: `https://your-domain.com/api/` (production)

## Authentication

### Current Implementation

The current version uses session-based authentication for web interfaces. API keys and token-based authentication are planned for future versions.

```python
# Web session authentication (current)
# Sessions are managed automatically by Flask

# Future: API key authentication
headers = {
    'Authorization': 'Bearer YOUR_API_TOKEN',
    'Content-Type': 'application/json'
}
```

## Core APIs

### ReconciliationEngine

The main reconciliation engine provides programmatic access to all reconciliation functionality.

#### GoldStandardReconciler

```python
from src.core.reconciliation_engine import GoldStandardReconciler

class GoldStandardReconciler:
    """
    Main reconciliation engine with comprehensive transaction processing.
    
    This class orchestrates the entire reconciliation workflow including
    data loading, processing, quality checks, and report generation.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize reconciliation engine.
        
        Args:
            config_path: Path to YAML configuration file
        """
    
    def run_reconciliation(self, 
                          start_date: str = None,
                          end_date: str = None, 
                          mode: str = "from_baseline") -> Dict:
        """
        Execute complete reconciliation process.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            mode: Processing mode ("from_scratch", "from_baseline")
            
        Returns:
            Dict containing reconciliation results and statistics
            
        Example:
            >>> reconciler = GoldStandardReconciler()
            >>> result = reconciler.run_reconciliation(
            ...     start_date="2024-01-01",
            ...     end_date="2024-12-31", 
            ...     mode="from_baseline"
            ... )
            >>> print(f"Final balance: {result['final_balance']}")
        """
    
    def get_reconciliation_summary(self) -> Dict:
        """
        Get summary of last reconciliation run.
        
        Returns:
            Dictionary with summary statistics and results
        """
    
    def export_results(self, format: str = "excel", output_path: str = None) -> str:
        """
        Export reconciliation results to specified format.
        
        Args:
            format: Export format ("excel", "csv", "json")
            output_path: Optional custom output path
            
        Returns:
            Path to generated export file
        """
```

#### AccountingEngine

```python
from src.core.accounting_engine import AccountingEngine

class AccountingEngine:
    """
    Double-entry bookkeeping engine for financial calculations.
    
    Implements GAAP-compliant accounting principles with automatic
    balance validation and audit trail generation.
    """
    
    def __init__(self):
        """Initialize accounting engine with empty ledger."""
    
    def add_transaction(self, 
                       date: datetime,
                       description: str,
                       debit_account: str,
                       credit_account: str,
                       amount: Decimal) -> str:
        """
        Add double-entry transaction to ledger.
        
        Args:
            date: Transaction date
            description: Transaction description
            debit_account: Account to debit
            credit_account: Account to credit
            amount: Transaction amount (positive)
            
        Returns:
            Transaction ID for reference
            
        Raises:
            ValueError: If amount is negative or zero
            AccountingError: If accounts don't balance
        """
    
    def get_balance(self, account: str) -> Decimal:
        """Get current balance for specified account."""
    
    def validate_books(self) -> bool:
        """Validate that all debits equal credits."""
    
    def generate_ledger(self) -> List[Dict]:
        """Generate complete accounting ledger."""
```

### Data Loading APIs

#### BaseLoader

```python
from src.loaders.base_loader import BaseLoader

class BaseLoader:
    """Base class for all data loaders."""
    
    def load_transactions(self, file_path: str) -> List[Dict]:
        """
        Load transactions from file.
        
        Args:
            file_path: Path to data file
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            FileNotFoundError: If file doesn't exist
            DataQualityError: If data quality issues found
        """
    
    def validate_data(self, transactions: List[Dict]) -> List[str]:
        """
        Validate transaction data quality.
        
        Returns:
            List of validation error messages
        """
```

#### ExpenseLoader

```python
from src.loaders.expense_loader import ExpenseLoader

class ExpenseLoader(BaseLoader):
    """Loader for general expense CSV files."""
    
    def __init__(self, encoding: str = "utf-8"):
        """
        Initialize expense loader.
        
        Args:
            encoding: File encoding (auto-detected if not specified)
        """
    
    def load_transactions(self, file_path: str) -> List[Dict]:
        """Load expense transactions with automatic format detection."""
```

### Manual Review APIs

#### ManualReviewSystem

```python
from src.review.manual_review_system import ManualReviewSystem

class ManualReviewSystem:
    """SQLite-based manual review system."""
    
    def __init__(self, db_path: str = "data/manual_reviews.db"):
        """
        Initialize review system.
        
        Args:
            db_path: Path to SQLite database file
        """
    
    def add_review_item(self, 
                       transaction_date: str,
                       description: str, 
                       amount: float,
                       payer: str) -> int:
        """
        Add transaction requiring manual review.
        
        Returns:
            Review item ID
        """
    
    def get_pending_reviews(self) -> List[Dict]:
        """Get all transactions pending review."""
    
    def submit_review(self,
                     review_id: int,
                     category: str,
                     split_type: str = "50_50",
                     allowed_amount: float = None,
                     notes: str = "") -> bool:
        """
        Submit manual review decision.
        
        Args:
            review_id: ID of review item
            category: Transaction category
            split_type: How to split shared expenses
            allowed_amount: Amount allowed for shared expenses
            notes: Optional notes
            
        Returns:
            True if successful
        """
    
    def get_review_statistics(self) -> Dict:
        """Get review session statistics."""
```

## Web Interface APIs

### Transaction APIs

#### GET /api/transactions

Get list of transactions requiring review.

```http
GET /api/transactions?status=pending&limit=50&offset=0
```

**Parameters:**
- `status` (optional): Filter by status ("pending", "reviewed", "all")
- `limit` (optional): Number of transactions to return (default: 25)
- `offset` (optional): Number of transactions to skip (default: 0)

**Response:**
```json
{
  "transactions": [
    {
      "id": 1,
      "date": "2024-08-10",
      "description": "Grocery Store Purchase", 
      "amount": -127.89,
      "payer": "Ryan",
      "source": "Chase Credit Card",
      "status": "pending",
      "created_at": "2024-08-10T10:30:00Z"
    }
  ],
  "total_count": 150,
  "has_more": true
}
```

#### POST /api/transactions/{id}/review

Submit review for specific transaction.

```http
POST /api/transactions/1/review
```

**Request Body:**
```json
{
  "category": "shared_expense",
  "split_type": "50_50", 
  "allowed_amount": 63.95,
  "notes": "Weekly grocery shopping"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Review submitted successfully",
  "transaction_id": 1,
  "updated_at": "2024-08-10T10:35:00Z"
}
```

### Progress APIs

#### GET /api/progress

Get real-time reconciliation progress.

```http
GET /api/progress
```

**Response:**
```json
{
  "status": "running",
  "progress_percent": 75.5,
  "current_step": "Processing transactions",
  "transactions_processed": 151,
  "total_transactions": 200,
  "start_time": "2024-08-10T10:00:00Z",
  "estimated_completion": "2024-08-10T10:15:00Z"
}
```

#### WebSocket /api/progress/stream

Real-time progress updates via WebSocket.

```javascript
const ws = new WebSocket('ws://localhost:5000/api/progress/stream');

ws.onmessage = function(event) {
    const progress = JSON.parse(event.data);
    console.log(`Progress: ${progress.progress_percent}%`);
};
```

### Export APIs

#### GET /api/export/csv

Export reconciliation results as CSV.

```http
GET /api/export/csv?format=transactions&date_range=2024-01-01,2024-12-31
```

**Parameters:**
- `format`: Export format ("transactions", "summary", "ledger")
- `date_range`: Date range in YYYY-MM-DD,YYYY-MM-DD format

**Response:**
```http
Content-Type: text/csv
Content-Disposition: attachment; filename="reconciliation_20240810.csv"

date,description,amount,payer,category
2024-08-10,"Grocery Store",-127.89,Ryan,shared_expense
```

#### POST /api/export/excel

Generate Excel export with multiple sheets.

```http
POST /api/export/excel
```

**Request Body:**
```json
{
  "sheets": ["transactions", "summary", "ledger"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "filters": {
    "category": ["shared_expense", "rent"],
    "payer": ["Ryan", "Jordyn"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "file_url": "/downloads/reconciliation_20240810_143022.xlsx",
  "file_size": 245760,
  "sheets_generated": 3,
  "expires_at": "2024-08-11T14:30:22Z"
}
```

### Configuration APIs

#### GET /api/config

Get current system configuration.

```http
GET /api/config
```

**Response:**
```json
{
  "reconciliation": {
    "amount_tolerance": 0.01,
    "date_tolerance_days": 1,
    "default_mode": "from_baseline"
  },
  "manual_review": {
    "batch_size": 50,
    "auto_categorize": true
  },
  "version": "6.0.0"
}
```

#### PUT /api/config

Update system configuration.

```http
PUT /api/config
```

**Request Body:**
```json
{
  "reconciliation": {
    "amount_tolerance": 0.05
  }
}
```

## Data Models

### Transaction Model

```json
{
  "id": "integer",
  "date": "string (ISO date)",
  "description": "string", 
  "amount": "number (negative for expenses)",
  "payer": "string",
  "source": "string",
  "category": "string (optional)",
  "split_type": "string (optional)",
  "is_personal": "boolean",
  "confidence_score": "number (0-1)",
  "created_at": "string (ISO datetime)",
  "updated_at": "string (ISO datetime)"
}
```

### Review Model

```json
{
  "id": "integer",
  "transaction_id": "integer",
  "category": "string",
  "split_type": "string",
  "allowed_amount": "number (optional)",
  "notes": "string (optional)",
  "reviewed_by": "string",
  "review_timestamp": "string (ISO datetime)",
  "status": "string"
}
```

### Reconciliation Result Model

```json
{
  "final_balance": "number",
  "who_owes_whom": "string",
  "transactions_processed": "integer",
  "manual_reviews_required": "integer",
  "data_quality_issues": "integer",
  "processing_time_seconds": "number",
  "baseline_date": "string (ISO date)",
  "run_timestamp": "string (ISO datetime)"
}
```

## Error Handling

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation errors |
| 500 | Internal Server Error | Server-side error |

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid transaction data provided",
    "details": {
      "field": "amount",
      "issue": "Amount must be a valid number"
    },
    "timestamp": "2024-08-10T10:30:00Z",
    "request_id": "req_12345"
  }
}
```

### Common Error Codes

| Code | Description | Resolution |
|------|-------------|------------|
| `VALIDATION_ERROR` | Request data validation failed | Check request format and required fields |
| `DATA_QUALITY_ERROR` | Data quality issues detected | Review and fix data quality problems |
| `TRANSACTION_NOT_FOUND` | Transaction ID not found | Verify transaction ID exists |
| `REVIEW_ALREADY_SUBMITTED` | Review already completed | Cannot modify completed reviews |
| `INSUFFICIENT_DATA` | Not enough data for processing | Ensure required data files are present |
| `DATABASE_ERROR` | Database operation failed | Check database connectivity and permissions |

### Python Exception Classes

```python
class ReconciliationError(Exception):
    """Base exception for reconciliation errors."""
    
class DataQualityError(ReconciliationError):
    """Raised when data quality issues are detected."""
    
class AccountingError(ReconciliationError):
    """Raised when accounting rules are violated."""
    
class ReviewError(ReconciliationError):
    """Raised when manual review operations fail."""
    
class ConfigurationError(ReconciliationError):
    """Raised when configuration is invalid."""
```

## Rate Limiting

### Current Implementation

Rate limiting is not currently implemented but is planned for future versions.

### Planned Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/transactions` | 100 requests | 1 minute |
| `/api/export/*` | 10 requests | 5 minutes |
| `/api/progress` | 60 requests | 1 minute |
| All other endpoints | 1000 requests | 1 hour |

### Rate Limit Headers

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1628097600
X-RateLimit-Window: 60
```

## Examples

### Python API Usage

#### Basic Reconciliation

```python
from src.core.reconciliation_engine import GoldStandardReconciler

# Initialize reconciler
reconciler = GoldStandardReconciler()

# Run reconciliation
result = reconciler.run_reconciliation(
    start_date="2024-01-01",
    end_date="2024-12-31",
    mode="from_baseline"
)

print(f"Final balance: {result['final_balance']}")
print(f"Processing time: {result['processing_time_seconds']}s")

# Export results
excel_path = reconciler.export_results(
    format="excel",
    output_path="output/reconciliation.xlsx"
)
print(f"Results exported to: {excel_path}")
```

#### Manual Review Processing

```python
from src.review.manual_review_system import ManualReviewSystem

# Initialize review system
review_system = ManualReviewSystem()

# Get pending reviews
pending = review_system.get_pending_reviews()
print(f"Pending reviews: {len(pending)}")

# Process first review
if pending:
    review = pending[0]
    success = review_system.submit_review(
        review_id=review['id'],
        category="shared_expense",
        split_type="50_50",
        allowed_amount=review['amount'] / 2,
        notes="Split grocery cost"
    )
    print(f"Review submitted: {success}")
```

### Web API Usage

#### JavaScript/AJAX

```javascript
// Get transactions requiring review
async function getTransactions() {
    const response = await fetch('/api/transactions?status=pending');
    const data = await response.json();
    return data.transactions;
}

// Submit transaction review
async function submitReview(transactionId, reviewData) {
    const response = await fetch(`/api/transactions/${transactionId}/review`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData)
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Usage
getTransactions().then(transactions => {
    console.log(`Found ${transactions.length} transactions`);
});

submitReview(1, {
    category: 'shared_expense',
    split_type: '50_50',
    allowed_amount: 63.95,
    notes: 'Weekly groceries'
}).then(result => {
    console.log('Review submitted successfully');
}).catch(error => {
    console.error('Error submitting review:', error);
});
```

#### cURL Examples

```bash
# Get pending transactions
curl -X GET "http://localhost:5000/api/transactions?status=pending" \
     -H "Accept: application/json"

# Submit transaction review
curl -X POST "http://localhost:5000/api/transactions/1/review" \
     -H "Content-Type: application/json" \
     -d '{
       "category": "shared_expense",
       "split_type": "50_50",
       "allowed_amount": 63.95,
       "notes": "Weekly grocery shopping"
     }'

# Export CSV
curl -X GET "http://localhost:5000/api/export/csv?format=transactions" \
     -H "Accept: text/csv" \
     -o reconciliation.csv

# Get system status
curl -X GET "http://localhost:5000/health" \
     -H "Accept: application/json"
```

### Error Handling Examples

#### Python

```python
from src.core.reconciliation_engine import GoldStandardReconciler
from src.core.exceptions import DataQualityError, AccountingError

try:
    reconciler = GoldStandardReconciler()
    result = reconciler.run_reconciliation()
    
except DataQualityError as e:
    print(f"Data quality issue: {e}")
    print("Please review and fix data quality problems")
    
except AccountingError as e:
    print(f"Accounting error: {e}")
    print("Check transaction data for accounting inconsistencies")
    
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error and notify administrators
```

#### JavaScript

```javascript
async function handleTransactionReview(transactionId, reviewData) {
    try {
        const result = await submitReview(transactionId, reviewData);
        console.log('Success:', result.message);
        
    } catch (error) {
        if (error.status === 400) {
            console.error('Validation error:', error.message);
            // Show validation errors to user
            
        } else if (error.status === 404) {
            console.error('Transaction not found');
            // Refresh transaction list
            
        } else if (error.status >= 500) {
            console.error('Server error occurred');
            // Show generic error message to user
            
        } else {
            console.error('Unexpected error:', error);
        }
    }
}
```

---

## Conclusion

This API reference provides comprehensive documentation for both programmatic and web APIs. The system is designed to be intuitive and consistent, with clear error handling and comprehensive examples.

For additional support or questions about API usage, please refer to the troubleshooting guide or create an issue in the project repository.