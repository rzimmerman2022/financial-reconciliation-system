# Configuration Guide

This guide covers all configuration options for the Financial Reconciliation System.

## Table of Contents

- [Overview](#overview)
- [Configuration File Location](#configuration-file-location)
- [Configuration Sections](#configuration-sections)
- [Environment Variables](#environment-variables)
- [Command Line Options](#command-line-options)
- [Advanced Configuration](#advanced-configuration)

## Overview

The Financial Reconciliation System uses a hierarchical configuration system:

1. **Default Configuration**: Built-in defaults
2. **Configuration File**: `config/config.yaml`
3. **Environment Variables**: Override file settings
4. **Command Line Arguments**: Highest priority

## Configuration File Location

The main configuration file is located at:
```
config/config.yaml
```

You can specify a custom configuration file using:
```bash
reconcile --config /path/to/custom/config.yaml
```

## Configuration Sections

### Application Settings

```yaml
app:
  name: "Financial Reconciliation System"
  version: "2.0.0"
  environment: "production"  # production, staging, development
  debug: false               # Enable debug logging
```

### Database Configuration

```yaml
database:
  # Main reconciliation database
  reconciliation:
    path: "data/reconciliation.db"
    backup_enabled: true
    backup_frequency: "daily"  # daily, weekly, monthly
  
  # Manual review database
  manual_review:
    path: "data/phase5_manual_reviews.db"
    auto_backup: true
```

### Processing Settings

```yaml
processing:
  # Transaction processing
  batch_size: 1000           # Number of transactions per batch
  parallel_processing: true   # Enable parallel processing
  max_workers: 4             # Maximum parallel workers
  
  # Date handling
  date_formats:
    - "%Y-%m-%d"
    - "%m/%d/%Y"
    - "%d/%m/%Y"
    - "%Y-%m-%d %H:%M:%S"
  
  # Amount handling
  decimal_places: 2
  currency: "USD"
```

### Reconciliation Rules

```yaml
reconciliation:
  # Matching tolerances
  amount_tolerance: 0.01      # Dollar amount tolerance
  date_tolerance_days: 1      # Days tolerance for matching
  
  # Fuzzy matching
  description_similarity_threshold: 0.85  # 0.0 to 1.0
  enable_fuzzy_matching: true
  
  # Advanced matching
  use_machine_learning: false
  ml_confidence_threshold: 0.90
```

### Data Quality Settings

```yaml
data_quality:
  # Quality checks
  enable_quality_checks: true
  flag_missing_amounts: true
  flag_invalid_dates: true
  flag_duplicate_transactions: true
  
  # Encoding handling
  fix_encoding_issues: true
  encoding_fallbacks:
    - "utf-8"
    - "latin-1"
    - "cp1252"
  
  # Validation rules
  min_transaction_amount: 0.01
  max_transaction_amount: 1000000.00
  valid_date_range:
    start: "2020-01-01"
    end: "2030-12-31"
```

### Output Configuration

```yaml
output:
  # Directories
  reports_directory: "output/reports"
  excel_directory: "output/excel"
  
  # Report settings
  default_report_format: "excel"  # excel, csv, json
  include_visualizations: true
  include_summary_stats: true
  
  # Excel specific
  excel:
    include_charts: true
    include_pivot_tables: true
    color_coding: true
  
  # Email settings
  email_reports: false
  email_recipients:
    - "finance@company.com"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
```

### GUI Configuration

```yaml
gui:
  # Theme settings
  theme: "material"          # material, classic, dark
  auto_save: true
  animation_duration: 300    # milliseconds
  
  # Window settings
  default_width: 1200
  default_height: 800
  min_width: 1000
  min_height: 700
  
  # Review settings
  show_keyboard_shortcuts: true
  confirm_before_save: true
  auto_advance: true         # Auto-advance after decision
```

### Logging Configuration

```yaml
logging:
  # General settings
  level: "INFO"              # DEBUG, INFO, WARNING, ERROR
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  
  # File logging
  file: "logs/reconciliation.log"
  max_file_size: "10MB"
  backup_count: 5
  
  # Component-specific levels
  components:
    loader: "INFO"
    processor: "INFO"
    reconciler: "INFO"
    gui: "DEBUG"
    api: "WARNING"
```

### API Configuration

```yaml
api:
  # API settings
  enabled: true
  host: "0.0.0.0"
  port: 5000
  
  # CORS settings
  cors_enabled: true
  cors_origins:
    - "http://localhost:3000"
    - "https://app.company.com"
  
  # Rate limiting
  rate_limiting: true
  rate_limit: "100/hour"
  
  # Authentication
  require_authentication: false
  api_key: null              # Set to enable API key auth
  jwt_secret: null           # Set to enable JWT auth
```

### Performance Tuning

```yaml
performance:
  # Caching
  cache_enabled: true
  cache_size: 1000           # Number of items to cache
  cache_ttl: 3600           # Cache time-to-live in seconds
  
  # Memory management
  max_memory_usage: "2GB"
  gc_threshold: 1000         # Garbage collection threshold
  
  # Database optimization
  db_connection_pool_size: 5
  db_query_timeout: 30       # seconds
```

## Environment Variables

Environment variables override configuration file settings:

```bash
# Application settings
export RECON_ENV=production
export RECON_DEBUG=false

# Database paths
export RECON_DB_PATH=/custom/path/to/db
export RECON_REVIEW_DB_PATH=/custom/path/to/review.db

# Processing settings
export RECON_BATCH_SIZE=2000
export RECON_MAX_WORKERS=8

# API settings
export RECON_API_PORT=8080
export RECON_API_KEY=your-secret-key
```

## Command Line Options

Command line arguments have the highest priority:

```bash
# Basic options
reconcile --config custom-config.yaml
reconcile --debug
reconcile --batch-size 500

# Date range
reconcile --start-date 2024-01-01 --end-date 2024-12-31

# Mode selection
reconcile --mode baseline
reconcile --mode from-baseline

# Output options
reconcile --output-format excel
reconcile --output-dir /custom/output

# Processing options
reconcile --no-parallel
reconcile --workers 2
```

## Advanced Configuration

### Custom Loaders

Add custom data loaders in the configuration:

```yaml
loaders:
  custom:
    - name: "CustomBankLoader"
      module: "src.loaders.custom_bank"
      class: "CustomBankLoader"
      file_pattern: "*_custom.csv"
      enabled: true
```

### Webhook Integration

Configure webhooks for events:

```yaml
webhooks:
  enabled: true
  endpoints:
    - url: "https://api.company.com/webhook"
      events:
        - "reconciliation.completed"
        - "manual_review.required"
      auth_header: "Bearer your-token"
```

### Plugin System

Enable plugins for extended functionality:

```yaml
plugins:
  enabled: true
  directory: "plugins/"
  auto_load: true
  allowed_plugins:
    - "export_plugin"
    - "notification_plugin"
```

## Configuration Best Practices

1. **Environment-Specific Configs**
   ```
   config/
   ├── config.yaml          # Base configuration
   ├── config.dev.yaml      # Development overrides
   ├── config.staging.yaml  # Staging overrides
   └── config.prod.yaml     # Production overrides
   ```

2. **Sensitive Data**
   - Never commit API keys or passwords
   - Use environment variables for secrets
   - Consider using a secrets manager

3. **Version Control**
   - Track configuration changes in git
   - Document configuration changes
   - Use meaningful commit messages

4. **Validation**
   - Test configuration changes locally
   - Validate YAML syntax before deploying
   - Keep backups of working configurations

## Troubleshooting

### Common Issues

1. **Configuration Not Loading**
   ```bash
   # Check file path
   reconcile --config config/config.yaml --debug
   
   # Validate YAML syntax
   python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"
   ```

2. **Environment Variables Not Working**
   ```bash
   # Check variable is set
   echo $RECON_API_PORT
   
   # Run with debug to see loaded config
   reconcile --debug
   ```

3. **Performance Issues**
   - Reduce batch_size for memory constraints
   - Increase max_workers for faster processing
   - Enable caching for repeated operations

## Migration Guide

### From Version 1.x to 2.0

1. **Configuration File Format**
   - Old: INI format
   - New: YAML format
   - Migration tool: `tools/migrate_config.py`

2. **Path Changes**
   ```yaml
   # Old
   database_path = "manual_reviews.db"
   
   # New
   database:
     manual_review:
       path: "data/phase5_manual_reviews.db"
   ```

3. **New Required Settings**
   - `app.version`
   - `processing.date_formats`
   - `data_quality.encoding_fallbacks`

---

For more information, see the [Technical Documentation](../technical/SYSTEM_STATUS.md) or contact support.