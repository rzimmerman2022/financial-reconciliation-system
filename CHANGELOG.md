# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.2] - 2025-08-06

### Fixed
- Resolved test suite import path issues in unit tests
  - Fixed imports in test_expense_processor.py (changed from `processors` to `src.processors`)
  - Fixed imports in test_gold_standard.py (changed from `gold_standard_reconciliation` to `src.core.reconciliation_engine`)
  - Fixed syntax error in test_modern_gui.py integration test
- Fixed web interface 500 errors on main route
  - Added missing template variables (stats.remaining, progress) to Flask render_template calls
  - Updated both empty state and data state responses with required template context

### Changed
- Updated version numbers from 3.0.0 to 4.0.0 in remaining files:
  - docs/architecture/PIPELINE.md
  - src/review/web_interface.py
  - src/review/ultra_modern_reconciliation_gui.py
- Standardized documentation across the project

### Added
- Comprehensive error handling for missing template variables in web interface

## [4.0.1] - 2025-01-04

### Fixed
- Aligned version numbers across all configuration files (pyproject.toml, setup.py, README.md) to 4.0.0
- Fixed packaging configuration to properly use src layout with correct module paths
- Updated all test imports to use proper src namespace (e.g., `src.utils.data_loader`)
- Added error handling for missing data files in web interface to prevent 500 errors
- Fixed TOML syntax errors in pyproject.toml package configuration

### Added
- Comprehensive GitHub Actions CI/CD pipeline with:
  - Multi-OS (Ubuntu, Windows, macOS) and Python version (3.8-3.11) testing
  - Automated linting, type checking, and test coverage reporting
  - Quick check workflow for feature branches
  - Automated release workflow with PyPI publishing support
- Standardized project documentation

### Changed
- Consolidated packaging configuration to use consistent src layout
- Updated entry points to match actual module structure
- Improved error handling in web interface for missing data files

## [4.0.0] - 2025-01-03

### Added
- Gold Standard Release with complete project overhaul
- Premium Visual GUI Interfaces for Transaction Review
- Modern web interface with Flask backend
- Comprehensive test suite with unit and integration tests
- Double-entry bookkeeping system
- Automated transaction matching algorithms
- Manual review capabilities for ambiguous transactions

### Changed
- Complete restructuring to src layout
- Enhanced data quality management
- Improved reconciliation accuracy

### Fixed
- Windows Unicode encoding issues
- Test runner compatibility issues

## [3.0.0] - 2024-12-15

### Added
- Initial production-ready implementation
- Core reconciliation engine
- Data loaders for multiple formats
- Basic reporting capabilities

## [2.0.0] - 2024-11-01

### Added
- Enhanced data processing capabilities
- Improved matching algorithms
- Better error handling

## [1.0.0] - 2024-10-01

### Added
- Initial release
- Basic reconciliation functionality
- CSV import/export capabilities