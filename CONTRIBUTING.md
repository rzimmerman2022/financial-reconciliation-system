# Contributing to Financial Reconciliation System

Thank you for your interest in contributing to the Financial Reconciliation System! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### Development Setup

1. **Fork and Clone**
   ```bash
   # Fork the repository on GitHub, then:
   git clone https://github.com/yourusername/financial-reconciliation.git
   cd financial-reconciliation
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies in development mode
   pip install -e ".[dev]"
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Test core functionality
   python -c "from src.core.accounting_engine import AccountingEngine; print('Setup OK')"
   
   # Test GUI (if display available)
   python bin/review-gui --help
   ```

## 📋 Development Guidelines

### Code Style

We follow **PEP 8** with some project-specific conventions:

```bash
# Format code (required before commits)
black src/ tests/

# Check linting
flake8 src/ tests/

# Type checking
mypy src/

# Import sorting
isort src/ tests/
```

**Key Standards:**
- **Line Length**: 88 characters (Black default)
- **Imports**: Sort with isort, group by standard/third-party/local
- **Docstrings**: Google style for all public functions/classes
- **Type Hints**: Required for all new code
- **Variable Naming**: `snake_case` for functions/variables, `PascalCase` for classes

### Project Structure Conventions

```
src/
├── core/          # Core business logic (accounting, reconciliation)
├── review/        # Review system components
├── utils/         # Utility functions and helpers
├── loaders/       # Data loading and parsing
├── processors/    # Data processing logic
└── reconcilers/   # Reconciliation engines

tests/
├── unit/          # Unit tests (fast, isolated)
├── integration/   # Integration tests (slower, realistic data)
└── fixtures/      # Test data and utilities

docs/
├── api/           # API reference documentation
├── architecture/  # System design documents
├── business/      # Business logic documentation
├── technical/     # Technical implementation details
└── user-guide/    # User-facing documentation
```

### Git Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/descriptive-name
   git checkout -b fix/issue-description
   git checkout -b docs/documentation-update
   ```

2. **Make Changes**
   - Write tests first (TDD approach recommended)
   - Implement feature/fix
   - Update documentation
   - Ensure all tests pass

3. **Commit Messages**
   Follow conventional commits format:
   ```bash
   # Format: type(scope): description
   
   feat(core): add support for multi-currency transactions
   fix(gui): resolve keyboard shortcut conflicts
   docs(api): update AccountingEngine documentation
   test(integration): add end-to-end reconciliation test
   refactor(review): simplify transaction categorization logic
   ```

4. **Pre-commit Checks**
   ```bash
   # Run before each commit
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   pytest
   ```

5. **Submit Pull Request**
   - Push to your fork
   - Create PR with clear description
   - Link to relevant issues
   - Ensure CI passes

### Testing Requirements

**All contributions must include tests:**

- **Unit Tests**: Fast, isolated tests for individual functions/classes
- **Integration Tests**: Test component interactions with realistic data
- **Documentation Tests**: Ensure examples in docs actually work

```bash
# Run different test categories
pytest tests/unit/                    # Fast unit tests
pytest tests/integration/             # Slower integration tests
pytest -m "not slow"                  # Skip slow tests
pytest --cov=src --cov-report=html    # Coverage report
```

**Test Writing Guidelines:**
```python
# tests/unit/test_accounting_engine.py
import pytest
from decimal import Decimal
from datetime import datetime
from src.core.accounting_engine import AccountingEngine

class TestAccountingEngine:
    """Test suite for AccountingEngine class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.engine = AccountingEngine()
        
    def test_post_expense_valid_transaction(self):
        """Test posting a valid expense transaction."""
        # Arrange
        date = datetime(2024, 10, 15)
        payer = "Jordyn"
        ryan_share = Decimal("25.00")
        jordyn_share = Decimal("25.00")
        description = "Test expense"
        
        # Act
        self.engine.post_expense(
            date=date,
            payer=payer,
            ryan_share=ryan_share,
            jordyn_share=jordyn_share,
            description=description
        )
        
        # Assert
        balance = self.engine.get_current_balance()
        assert balance[0] == "Ryan owes Jordyn"
        assert balance[1] == Decimal("25.00")
        assert len(self.engine.transactions) == 1
        
    def test_post_expense_invalid_payer(self):
        """Test posting expense with invalid payer raises ValueError."""
        with pytest.raises(ValueError, match="Invalid payer"):
            self.engine.post_expense(
                date=datetime.now(),
                payer="Invalid",
                ryan_share=Decimal("10.00"),
                jordyn_share=Decimal("10.00"),
                description="Test"
            )
```

## 🏗️ Architecture Guidelines

### Core Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Double-Entry Accounting**: All financial operations must maintain accounting invariants
3. **Data Integrity**: Comprehensive validation and audit trails
4. **Error Handling**: Graceful degradation with clear error messages
5. **Testability**: All components designed for easy testing

### Design Patterns

- **Factory Pattern**: For creating different reconciliation engines
- **Strategy Pattern**: For different review interfaces (GUI, CLI, web)
- **Observer Pattern**: For progress tracking and notifications
- **Template Method**: For common reconciliation workflows
- **Command Pattern**: For undoable operations

### Database Design

```sql
-- Review system database schema
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    date TEXT NOT NULL,
    description TEXT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payer TEXT NOT NULL,
    source TEXT,
    category TEXT,
    allowed_amount DECIMAL(10,2),
    notes TEXT,
    status TEXT DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON transactions(status);
CREATE INDEX idx_date ON transactions(date);
CREATE INDEX idx_category ON transactions(category);
```

## 🧪 Testing Strategy

### Test Pyramid

1. **Unit Tests (70%)**
   - Fast execution (< 1ms per test)
   - No external dependencies
   - Test individual functions/methods
   - Mock external services

2. **Integration Tests (20%)**
   - Test component interactions
   - Use test databases and files
   - Verify end-to-end workflows
   - Acceptable slower execution

3. **End-to-End Tests (10%)**
   - Full system tests
   - Real data scenarios
   - GUI automation where applicable
   - Performance and stress tests

### Test Data Management

```python
# tests/fixtures/sample_data.py
from decimal import Decimal
from datetime import datetime

SAMPLE_TRANSACTIONS = [
    {
        'date': datetime(2024, 10, 15),
        'description': 'Groceries - Whole Foods',
        'amount': Decimal('127.43'),
        'payer': 'Jordyn',
        'category': 'expense'
    },
    {
        'date': datetime(2024, 10, 1),
        'description': 'October Rent',
        'amount': Decimal('2000.00'),
        'payer': 'Jordyn',
        'category': 'rent'
    }
]

def create_test_database():
    """Create temporary database with sample data."""
    # Implementation
    pass
```

### Continuous Integration

Our CI pipeline runs:
1. **Code Quality**: Black, flake8, mypy, isort
2. **Security**: bandit security linting
3. **Tests**: Full test suite with coverage
4. **Documentation**: Build and validate documentation
5. **Performance**: Benchmark critical operations

## 📚 Documentation Standards

### Code Documentation

```python
def post_expense(
    self,
    date: datetime,
    payer: str,
    ryan_share: Decimal,
    jordyn_share: Decimal,
    description: str,
    metadata: Optional[Dict] = None
) -> None:
    """Post a shared expense transaction to the accounting system.
    
    This method records a shared expense where one person pays upfront
    and owes reimbursement from the other party. Updates account balances
    according to double-entry bookkeeping principles.
    
    Args:
        date: When the expense occurred
        payer: Who paid for the expense ("Ryan" or "Jordyn")
        ryan_share: Ryan's portion of the expense
        jordyn_share: Jordyn's portion of the expense
        description: Human-readable description of the expense
        metadata: Optional additional transaction data
        
    Raises:
        ValueError: If payer is not "Ryan" or "Jordyn"
        ValueError: If any amount is negative
        ValueError: If accounting invariants would be violated
        
    Example:
        >>> engine = AccountingEngine()
        >>> engine.post_expense(
        ...     date=datetime(2024, 10, 15),
        ...     payer="Jordyn",
        ...     ryan_share=Decimal("25.00"),
        ...     jordyn_share=Decimal("25.00"),
        ...     description="Shared dinner"
        ... )
        >>> balance = engine.get_current_balance()
        >>> print(balance)  # ('Ryan owes Jordyn', Decimal('25.00'))
    """
```

### API Documentation

- **Reference**: Complete API docs in `docs/api/`
- **Examples**: Working code examples for all public APIs
- **Changelog**: Document breaking changes and migration guides
- **Architecture**: High-level design documents

### User Documentation

- **Getting Started**: Step-by-step setup and first use
- **User Guide**: Complete workflows and feature explanations
- **Troubleshooting**: Common issues and solutions
- **FAQ**: Frequently asked questions

## 🚨 Security Considerations

### Data Protection

- **No Hardcoded Secrets**: Use environment variables
- **Input Validation**: Sanitize all user inputs
- **SQL Injection**: Use parameterized queries
- **File Access**: Validate file paths and permissions

### Code Security

```python
# Good: Parameterized query
cursor.execute(
    "SELECT * FROM transactions WHERE date = ?",
    (date_param,)
)

# Bad: String interpolation
cursor.execute(
    f"SELECT * FROM transactions WHERE date = '{date_param}'"
)
```

### Dependency Security

```bash
# Check for known vulnerabilities
pip audit

# Update vulnerable packages
pip install --upgrade package-name
```

## 🐛 Issue Guidelines

### Reporting Bugs

**Use the bug report template:**

```markdown
**Bug Description**
Clear description of the issue

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Version: [e.g., 1.0.0]

**Additional Context**
- Error messages
- Log files
- Screenshots (for GUI issues)
```

### Feature Requests

**Use the feature request template:**

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Mockups, examples, references
```

## 📈 Performance Guidelines

### Optimization Principles

1. **Measure First**: Profile before optimizing
2. **Algorithmic Efficiency**: Choose appropriate algorithms
3. **Memory Management**: Avoid memory leaks and excessive usage
4. **Database Optimization**: Use indexes and efficient queries
5. **Caching**: Cache expensive computations appropriately

### Performance Testing

```python
import time
import cProfile
from src.core.reconciliation_engine import GoldStandardReconciler

def benchmark_reconciliation():
    """Benchmark reconciliation performance."""
    start_time = time.time()
    
    reconciler = GoldStandardReconciler(...)
    reconciler.run_reconciliation()
    
    end_time = time.time()
    print(f"Reconciliation took {end_time - start_time:.2f} seconds")

# Profile with cProfile
cProfile.run('benchmark_reconciliation()', 'profile_output.prof')
```

## 🔄 Release Process

### Version Management

We use **Semantic Versioning** (semver):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)  
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. **Pre-release**
   - [ ] All tests pass
   - [ ] Documentation updated
   - [ ] Changelog updated
   - [ ] Version bumped
   - [ ] Performance benchmarks run

2. **Release**
   - [ ] Tag release in Git
   - [ ] Build distribution packages
   - [ ] Upload to PyPI (if applicable)
   - [ ] Create GitHub release
   - [ ] Update documentation

3. **Post-release**
   - [ ] Announce release
   - [ ] Monitor for issues
   - [ ] Plan next iteration

## 🤝 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment:

- **Be Respectful**: Treat everyone with respect and kindness
- **Be Collaborative**: Work together constructively
- **Be Patient**: Help newcomers learn and grow
- **Be Professional**: Keep discussions focused and productive

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions and reviews
- **Discussions**: General questions and community chat

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes
- GitHub contributors list
- Project documentation

---

**Questions?** Open an issue or start a discussion. We're here to help!

**Ready to contribute?** Fork the repository and submit your first PR!

---

**Last Updated:** January 4, 2025  
**Version:** 4.0.1