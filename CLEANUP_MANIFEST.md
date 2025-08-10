# Repository Cleanup Manifest

**Date:** August 10, 2025  
**Purpose:** Comprehensive analysis of repository structure for systematic cleanup and reorganization

## File Analysis and Classification

### CORE Files (Essential for Operation)

#### **Main Entry Points**
- `reconcile.py` - PRIMARY PIPELINE ENTRY POINT - Main reconciliation script
- `run_accurate_reconciliation.py` - Enhanced reconciliation entry point with accuracy improvements
- `comprehensive_analysis.py` - Comprehensive analysis and reporting entry point

#### **Core System Components**
- `src/core/accounting_engine.py` - Core accounting logic and calculations
- `src/core/reconciliation_engine.py` - Main reconciliation processing engine
- `src/core/accuracy_improvements.py` - Accuracy enhancement algorithms
- `src/core/description_decoder.py` - Transaction description parsing and interpretation

#### **Data Loading System**
- `src/loaders/expense_loader.py` - Expense data loading functionality
- `src/loaders/rent_loader.py` - Rent payment data loading
- `src/loaders/zelle_loader.py` - Zelle transaction data loading
- `src/utils/data_loader.py` - Core data loading utilities

#### **Processing System**
- `src/processors/expense_processor.py` - Expense transaction processing logic

#### **Review System**
- `src/review/manual_review_system.py` - Manual review database and logic
- `src/review/batch_review_helper.py` - Batch review processing utilities
- `src/review/manual_review_helper.py` - Manual review assistance tools

#### **GUI Applications**
- `src/review/ultra_premium_gui.py` - **RECOMMENDED GUI** - Ultra-premium interface with gold-standard design
- `src/review/modern_visual_review_gui.py` - Modern Material Design GUI
- `src/review/premium_reconciliation_gui.py` - Premium CustomTkinter GUI
- `src/review/web_interface.py` - Web-based review interface

#### **Utility Scripts**
- `src/scripts/export_to_excel.py` - Excel export functionality
- `src/scripts/review_interface.py` - Command-line review interface
- `src/utils/__init__.py` - Utility package initialization

#### **Package Structure**
- `src/__init__.py` - Main source package initialization
- `src/core/__init__.py` - Core package initialization
- `src/loaders/__init__.py` - Loaders package initialization
- `src/processors/__init__.py` - Processors package initialization
- `src/reconcilers/__init__.py` - Reconcilers package initialization
- `src/review/__init__.py` - Review package initialization
- `setup.py` - Package installation configuration
- `requirements.txt` - Python dependencies

### DOCUMENTATION Files (Important Knowledge)

#### **Primary Documentation**
- `README.md` - **PRIMARY** - Main project documentation
- `QUICKSTART.md` - Quick start guide for users
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Version history and changes

#### **Architecture Documentation**
- `docs/architecture/GOLD_STANDARD_STRUCTURE.md` - System architecture specification
- `docs/architecture/PIPELINE.md` - Processing pipeline documentation
- `docs/technical/AI_HANDOVER_CONTEXT.md` - Technical context for development handover
- `docs/technical/SYSTEM_STATUS.md` - Current system status and health

#### **User Guides**
- `docs/user-guide/GETTING_STARTED.md` - Comprehensive getting started guide
- `docs/user-guide/CONFIGURATION.md` - Configuration options and settings
- `docs/user-guide/DEPLOYMENT.md` - Deployment instructions
- `docs/user-guide/TROUBLESHOOTING.md` - Troubleshooting guide

#### **Business Documentation**
- `docs/business/CRITICAL_RENT_RULES.md` - Critical business rules for rent processing
- `docs/business/assumptions.md` - Business assumptions and constraints

#### **Technical Documentation**
- `docs/api/API_REFERENCE.md` - API reference documentation
- `docs/technical/CURRENT_STATUS_AND_ISSUES.md` - Technical status and known issues
- `docs/technical/MANUAL_REVIEW_ISSUE.md` - Manual review system documentation
- `docs/GUI_DOCUMENTATION.md` - GUI usage documentation

#### **Status and Quality Documentation**
- `docs/ACCURACY.md` - Accuracy metrics and improvements
- `docs/TESTING_STATUS.md` - Testing status and coverage
- `docs/CURRENT_STATE.md` - Current state of the project
- `docs/CLEANUP_LOG.md` - Previous cleanup activities
- `GUI_IMPROVEMENTS.md` - GUI enhancement documentation (newly created)
- `ISSUES_RESOLVED.md` - Record of resolved issues

### DEPRECATED Files (Old/Unused - Move to Archive)

#### **Legacy GUI Implementations**
- `modern_aesthetic_gui.py` - **ROOT LEVEL** - Older GUI implementation, superseded by src/review/ultra_premium_gui.py
- `ultra_modern_dashboard.py` - **ROOT LEVEL** - Dashboard implementation, superseded by better organized versions

#### **Legacy Launchers**
- `launch_gui.py` - **ROOT LEVEL** - Generic GUI launcher, superseded by specific launchers
- `launch_modern_gui.py` - **ROOT LEVEL** - Modern GUI launcher, functionality integrated elsewhere
- `launch_dashboard.py` - **ROOT LEVEL** - Dashboard launcher, superseded by premium version

#### **Root Level Scripts** (should be in src/)
- `reconcile_web.py` - **ROOT LEVEL** - Web interface launcher, should be in src/
- `chronological_viewer.py` - **ROOT LEVEL** - Transaction viewer, should be in src/scripts/
- `view_all_transactions.py` - **ROOT LEVEL** - Transaction viewer, should be in src/scripts/

### EXPERIMENTAL Files (Unfinished Features - Review for Archive)

#### **Advanced GUI Implementations**
- `src/review/ultra_modern_reconciliation_gui.py` - Advanced GUI implementation, may be incomplete
- `src/review/spreadsheet_review_system.py` - Spreadsheet-based review system

#### **Testing Utilities**
- `src/scripts/run_tests.py` - Test runner script
- `tests/unit/test_tkinter.py` - GUI testing utilities

### REDUNDANT Files (Duplicate Functionality - Archive)

#### **Multiple Launcher Files**
- `launch_premium_dashboard.py` - **ROOT LEVEL** - Premium dashboard launcher (multiple dashboard launchers exist)

#### **Generated Data Files** (should be in data/ or output/)
- Multiple `monthly_summary_*.json` files in root - Generated output files, should be in output/
- Output files in root directory that should be organized

### TEST Files (Keep in tests/)

#### **Unit Tests**
- `tests/unit/test_accounting_engine.py` - Accounting engine unit tests
- `tests/unit/test_data_loader.py` - Data loader unit tests
- `tests/unit/test_description_decoder.py` - Description decoder tests
- `tests/unit/test_description_decoder_comprehensive.py` - Comprehensive decoder tests
- `tests/unit/test_expense_processor.py` - Expense processor tests
- `tests/unit/test_gold_standard.py` - Gold standard validation tests
- `tests/unit/test_gui_state.py` - GUI state management tests
- `tests/unit/test_loaders.py` - Loader functionality tests

#### **Integration Tests**
- `tests/integration/test_db_access.py` - Database access integration tests
- `tests/integration/test_modern_gui.py` - GUI integration tests

### CONFIGURATION Files (Keep in config/)

#### **Environment Configuration**
- `.claude/settings.local.json` - Claude AI configuration (keep in place)
- `.vscode/tasks.json` - VS Code tasks configuration (keep in place)

#### **Output and Generated Files**
- `output/gold_standard/` - Contains generated reports and analysis
- `htmlcov/status.json` - Test coverage data

## Dependencies Analysis

### Critical Dependencies
- **Core Engine Dependencies:**
  - `reconcile.py` → `src/core/reconciliation_engine.py`
  - `reconcile.py` → `src/core/accounting_engine.py`
  - `reconcile.py` → `src/loaders/*`

- **GUI Dependencies:**
  - All GUI files → `src/review/manual_review_system.py`
  - GUI launchers → specific GUI implementations

- **Processing Pipeline:**
  - `comprehensive_analysis.py` → `src/core/*`
  - `run_accurate_reconciliation.py` → `src/core/accuracy_improvements.py`

### Import Statement Updates Required
When moving files, these import statements will need updates:
1. **Root-level script imports** - Any imports from root-level scripts
2. **Relative imports in moved files** - Path adjustments needed
3. **GUI launcher imports** - Update paths to GUI implementations

## Recommended Actions

### Phase 1: Safety
- ✅ **COMPLETED:** Backup branch `pre-cleanup-backup-2025-08-10` created

### Phase 2: Archive Candidates
**Move to `/archive/deprecated/`:**
- `modern_aesthetic_gui.py`
- `ultra_modern_dashboard.py` 
- `launch_gui.py`
- `launch_modern_gui.py`
- `launch_dashboard.py`

**Move to `/archive/experimental/`:**
- `src/review/ultra_modern_reconciliation_gui.py` (if incomplete)
- `src/review/spreadsheet_review_system.py` (if unused)

**Move to `/archive/redundant/`:**
- Root-level scripts that should be in src/
- Duplicate launcher implementations

### Phase 3: Reorganization
**Move to `/src/` (main entry points):**
- Keep `reconcile.py`, `run_accurate_reconciliation.py`, `comprehensive_analysis.py` as main entry points
- Move `reconcile_web.py` → `src/web/`
- Move utility scripts to appropriate `src/` subdirectories

**Move to `/scripts/`:**
- `chronological_viewer.py`
- `view_all_transactions.py`
- Keep active launcher files (`launch_ultra_premium_gui.py`, `launch_premium_dashboard.py`)

**Move to `/data/` or `/output/`:**
- All `monthly_summary_*.json` files
- Generated report files

### Phase 4: Documentation
**Standardize structure:**
- Ensure all `.md` files follow consistent format
- Update cross-references after file moves
- Create missing critical documentation

## Entry Point Identification

### Primary Entry Points (Main Pipeline)
1. **`reconcile.py`** - Main reconciliation processing
2. **`run_accurate_reconciliation.py`** - Enhanced reconciliation with accuracy improvements  
3. **`comprehensive_analysis.py`** - Comprehensive analysis and reporting

### Secondary Entry Points (User Interfaces)
1. **`launch_ultra_premium_gui.py`** - Launch ultra-premium GUI (recommended)
2. **`launch_premium_dashboard.py`** - Launch premium dashboard
3. **`reconcile_web.py`** - Web interface entry point

### Utility Entry Points
1. **`src/scripts/export_to_excel.py`** - Excel export utility
2. **`src/scripts/review_interface.py`** - Command-line review interface

## Notes and Considerations

### Preservation Strategy
- All files marked for archiving will be moved to `/archive/` rather than deleted
- Archive will have subdirectories for different reasons (deprecated, experimental, redundant)
- Archive contents will be fully documented in `/archive/ARCHIVE_CONTENTS.md`

### Import Update Strategy
- All import statements will be systematically updated during reorganization
- Testing will be performed after each major move to ensure functionality remains intact
- Entry point functionality will be validated throughout the process

### Risk Assessment
- **LOW RISK:** Documentation moves and archive operations
- **MEDIUM RISK:** Moving root-level scripts (requires import updates)
- **HIGH RISK:** Moving core system files (requires careful testing)

**Next Phase:** Create standardized directory structure and begin systematic reorganization.