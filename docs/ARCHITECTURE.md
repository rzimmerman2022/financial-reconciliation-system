# System Architecture Documentation

**Last Updated:** August 10, 2025  
**Version:** 6.0.0  
**Description:** Comprehensive system design and component interactions for the Financial Reconciliation System

## Table of Contents

- [Overview](#overview)
- [System Design Principles](#system-design-principles)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Interface Layer](#interface-layer)
- [Storage Architecture](#storage-architecture)
- [Security Model](#security-model)
- [Deployment Architecture](#deployment-architecture)
- [Extension Points](#extension-points)

## Overview

The Financial Reconciliation System is designed as a modular, extensible platform for automated and manual financial transaction reconciliation. The architecture follows clean separation of concerns with well-defined boundaries between components.

### Core Design Goals

1. **Modularity**: Each component has a single responsibility and clear interfaces
2. **Extensibility**: New banks, file formats, and interfaces can be easily added
3. **Reliability**: Robust error handling and data integrity guarantees
4. **Performance**: Efficient processing of large transaction datasets
5. **Usability**: Multiple interfaces for different user preferences and workflows

## System Design Principles

### 1. **Layered Architecture**
```
┌─────────────────┐
│ Interface Layer │  ← Web GUI, Desktop GUI, CLI
├─────────────────┤
│ Service Layer   │  ← Reconciliation Engine, Manual Review System
├─────────────────┤
│ Core Logic      │  ← Accounting Engine, Description Decoder
├─────────────────┤
│ Data Layer      │  ← Loaders, Processors, Storage
└─────────────────┘
```

### 2. **Separation of Concerns**
- **Data Ingestion**: Isolated from business logic
- **Processing Logic**: Independent of storage mechanisms
- **User Interfaces**: Decoupled from core processing
- **Configuration**: Externalized from code logic

### 3. **Plugin Architecture**
- **Loaders**: Pluggable data source adapters
- **Interfaces**: Multiple UI implementations
- **Processors**: Extensible processing pipeline
- **Exporters**: Configurable output formats

## Component Architecture

### Core Components

#### 1. **Reconciliation Engine** (`src/core/reconciliation_engine.py`)
**Purpose**: Orchestrates the entire reconciliation process

**Responsibilities**:
- Coordinates data loading from multiple sources
- Manages the reconciliation workflow
- Handles baseline calculations and debt tracking
- Generates comprehensive reports and audit trails

**Key Classes**:
- `GoldStandardReconciler`: Main orchestration class
- `ReconciliationWithReview`: Adds manual review capabilities

**Dependencies**:
- Accounting Engine (for double-entry bookkeeping)
- Data Loaders (for transaction ingestion)
- Manual Review System (for human input)

#### 2. **Accounting Engine** (`src/core/accounting_engine.py`)
**Purpose**: Implements double-entry bookkeeping and financial calculations

**Responsibilities**:
- Maintains accounting ledger with debits and credits
- Calculates running balances and debt positions
- Validates accounting invariants (debits = credits)
- Handles settlement transactions and personal expenses

**Key Features**:
- GAAP-compliant double-entry bookkeeping
- Automatic balance validation
- Support for shared expense splitting
- Settlement payment processing

#### 3. **Description Decoder** (`src/core/description_decoder.py`)
**Purpose**: Interprets transaction descriptions using pattern matching

**Responsibilities**:
- Classifies transactions into categories (rent, groceries, personal, etc.)
- Extracts semantic meaning from transaction descriptions
- Provides confidence scores for classifications
- Handles edge cases and ambiguous descriptions

**Pattern Categories**:
- Rent payments and housing costs
- Grocery and shopping expenses
- Personal transactions (gifts, individual purchases)
- Settlement and balance transfers
- Shared expenses requiring splitting

### Data Layer Components

#### 4. **Data Loaders** (`src/loaders/`)
**Purpose**: Ingests transaction data from various sources

**Loaders Available**:
- **ExpenseLoader**: General expense CSV files
- **RentLoader**: Rent allocation and housing cost data
- **ZelleLoader**: Zelle payment platform exports

**Common Features**:
- Automatic encoding detection (UTF-8, CP1252, ISO-8859-1)
- Date format normalization (15+ supported formats)
- Data quality validation and error reporting
- Duplicate detection and handling

#### 5. **Data Processors** (`src/processors/`)
**Purpose**: Processes and normalizes transaction data

**Processing Steps**:
1. **Normalization**: Standardize date, amount, and description formats
2. **Validation**: Check data integrity and flag issues
3. **Enrichment**: Add computed fields and metadata
4. **Quality Assurance**: Generate data quality reports

### Review System Components

#### 6. **Manual Review System** (`src/review/manual_review_system.py`)
**Purpose**: Manages human review of ambiguous transactions

**Database Schema**:
```sql
-- Manual review records
CREATE TABLE manual_reviews (
    id INTEGER PRIMARY KEY,
    transaction_date TEXT,
    description TEXT,
    amount REAL,
    payer TEXT,
    category TEXT,
    split_type TEXT,
    allowed_amount REAL,
    notes TEXT,
    reviewed_by TEXT,
    review_timestamp TEXT,
    status TEXT
);
```

**Features**:
- SQLite-based persistent storage
- Transaction status tracking
- Batch processing capabilities
- Review session management

#### 7. **User Interfaces** (`src/review/`)
**Purpose**: Provides multiple interfaces for transaction review

**Available Interfaces**:
- **Ultra Premium GUI**: Gold-standard design with animations
- **Modern Visual GUI**: Material Design with responsive layout
- **Premium GUI**: CustomTkinter with AI-powered suggestions
- **Web Interface**: Flask-based browser interface

**Common Features**:
- Real-time progress tracking
- Keyboard shortcuts for efficiency
- Category-based color coding
- Export and reporting capabilities

## Data Flow

### 1. **Data Ingestion Flow**
```
Bank CSV Files → Data Loaders → Normalization → Validation → Storage
     ↓              ↓              ↓            ↓         ↓
  Raw Data → Parsed Records → Clean Data → QA Reports → Database
```

### 2. **Processing Flow**
```
Stored Data → Reconciliation Engine → Accounting Engine → Reports
     ↓              ↓                      ↓             ↓
 Transactions → Business Logic → Double Entry → Audit Trail
```

### 3. **Review Flow**
```
Ambiguous → Manual Review → User Decision → Updated Records
Transactions    System        Interface        Database
```

## Interface Layer

### Web Interface Architecture

#### Technology Stack
- **Backend**: Flask web framework
- **Frontend**: Alpine.js for reactivity
- **Styling**: TailwindCSS with custom components
- **Charts**: Chart.js for data visualization

#### API Endpoints
```
GET  /                    # Main dashboard
GET  /api/transactions    # Transaction list API
POST /api/review         # Submit transaction review
GET  /api/progress       # Real-time progress updates
GET  /api/export/csv     # CSV export endpoint
```

### Desktop GUI Architecture

#### Framework: Tkinter/CustomTkinter
- **Theme System**: Consistent color schemes and styling
- **Component Library**: Reusable UI components
- **Animation Engine**: Smooth transitions and interactions
- **Keyboard Shortcuts**: Power user efficiency features

#### GUI Components
- **PremiumCard**: Container with elevation and hover effects
- **CategorySelector**: Interactive category selection
- **ProgressIndicator**: Real-time progress visualization
- **DataChart**: Interactive data visualizations

## Storage Architecture

### Database Design

#### SQLite Database Structure
```
financial_reconciliation.db
├── manual_reviews        # Human review decisions
├── transaction_log       # Audit trail of all changes
├── reconciliation_runs   # Historical reconciliation results
└── system_metadata       # Configuration and state
```

#### Data Integrity
- **ACID Compliance**: Atomic transactions with rollback capability
- **Referential Integrity**: Foreign key constraints
- **Data Validation**: Check constraints for data quality
- **Backup Strategy**: Automated database backups

### File System Organization
```
data/
├── databases/           # SQLite database files
├── imports/            # Raw import files
├── processed/          # Normalized data files
└── exports/           # Generated reports and exports

output/
├── reports/           # Generated reconciliation reports
├── exports/           # Excel and CSV exports
└── audit-logs/       # Audit trail files
```

## Security Model

### Data Protection
1. **Input Validation**: All user inputs are validated and sanitized
2. **SQL Injection Prevention**: Parameterized queries throughout
3. **File Access Control**: Restricted file system access
4. **Error Handling**: No sensitive data in error messages

### Audit Trail
1. **Transaction Logging**: All changes are logged with timestamps
2. **User Attribution**: Review decisions are attributed to users
3. **State Snapshots**: Regular snapshots of system state
4. **Integrity Checks**: Regular validation of data consistency

### Configuration Security
1. **Environment Variables**: Sensitive config in environment variables
2. **Default Security**: Secure defaults for all configurations
3. **Access Control**: File permissions and access restrictions

## Deployment Architecture

### Development Environment
```
Local Machine
├── Python Virtual Environment
├── SQLite Database (local file)
├── Test Data (anonymized)
└── Development Tools (pytest, linting)
```

### Production Deployment
```
Server Environment
├── Application Server (Flask/Gunicorn)
├── Database (SQLite or PostgreSQL)
├── Reverse Proxy (Nginx)
├── Process Manager (systemd/supervisor)
└── Monitoring (logging, metrics)
```

### Container Deployment
```yaml
# docker-compose.yml
services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - FLASK_ENV=production
```

## Extension Points

### Adding New Banks
1. **Create Loader**: Implement new loader in `src/loaders/`
2. **Configure Patterns**: Add bank-specific patterns to config
3. **Add Tests**: Create comprehensive test cases
4. **Update Documentation**: Document new bank support

Example:
```python
class NewBankLoader(BaseLoader):
    def load_transactions(self, file_path: str) -> List[Transaction]:
        # Bank-specific loading logic
        pass
```

### Adding New Interfaces
1. **Create Interface**: Implement in `src/review/`
2. **Follow Patterns**: Use existing interfaces as templates
3. **Add Launcher**: Create launcher script if needed
4. **Update Documentation**: Document new interface

### Adding New Export Formats
1. **Create Exporter**: Implement in `src/exporters/`
2. **Register Format**: Add to export system
3. **Add Configuration**: Support in config system
4. **Create Tests**: Comprehensive test coverage

## Performance Considerations

### Data Processing
- **Lazy Loading**: Load data only when needed
- **Batch Processing**: Process transactions in batches
- **Memory Management**: Efficient memory usage for large datasets
- **Caching**: Cache frequently accessed data

### Database Optimization
- **Indexing**: Appropriate indexes for query performance
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Optimized SQL queries
- **Bulk Operations**: Batch database operations

### User Interface
- **Progressive Loading**: Load UI progressively
- **Responsive Design**: Efficient rendering and updates
- **Lazy Rendering**: Render only visible components
- **Caching**: Cache UI state and data

---

## Conclusion

This architecture provides a solid foundation for the Financial Reconciliation System with clear separation of concerns, extensibility points, and robust design principles. The modular design allows for easy maintenance, testing, and enhancement while providing multiple interfaces for different user needs.

The system successfully balances complexity and usability, providing powerful reconciliation capabilities while maintaining ease of use and reliability.