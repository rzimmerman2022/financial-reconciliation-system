# Deployment Guide

This guide covers deploying the Financial Reconciliation System in various environments, from development to production.

## 🏗️ Deployment Options

### 1. Local Development Deployment

**Best for:** Development, testing, single-user scenarios

```bash
# 1. Clone and setup
git clone https://github.com/yourorg/financial-reconciliation.git
cd financial-reconciliation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Initialize database
python -c "from src.review.manual_review_system import ManualReviewSystem; ManualReviewSystem('data/phase5_manual_reviews.db')"

# 4. Test installation
python bin/review-gui --help
pytest
```

### 2. Server Deployment

**Best for:** Multi-user environments, automated processing

```bash
# 1. System preparation (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.8 python3-pip python3-venv python3-tk
sudo apt-get install sqlite3 git

# 2. Create service user
sudo useradd -r -s /bin/false reconciliation
sudo mkdir -p /opt/financial-reconciliation
sudo chown reconciliation:reconciliation /opt/financial-reconciliation

# 3. Deploy application
sudo -u reconciliation git clone https://github.com/yourorg/financial-reconciliation.git /opt/financial-reconciliation
cd /opt/financial-reconciliation
sudo -u reconciliation python3 -m venv venv
sudo -u reconciliation ./venv/bin/pip install -r requirements.txt

# 4. Configure systemd service (see service configuration below)
```

### 3. Docker Deployment

**Best for:** Containerized environments, cloud deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    python3-tk \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd -r -s /bin/false appuser

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app

# Switch to app user
USER appuser

# Create data directory
RUN mkdir -p data test-data/bank-exports test-data/legacy output

# Expose port (if using web interface)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "from src.core.accounting_engine import AccountingEngine; AccountingEngine()" || exit 1

# Default command
CMD ["python", "bin/run-with-review", "--mode", "from_baseline"]
```

```bash
# Build and run Docker container
docker build -t financial-reconciliation .
docker run -d \
    --name reconciliation \
    -v /host/data:/app/data \
    -v /host/test-data:/app/test-data \
    -v /host/output:/app/output \
    financial-reconciliation
```

### 4. Cloud Deployment (AWS Example)

**Best for:** Scalable, managed cloud environments

```yaml
# docker-compose.yml for AWS ECS
version: '3.8'
services:
  reconciliation:
    image: your-account.dkr.ecr.region.amazonaws.com/financial-reconciliation:latest
    environment:
      - LOG_LEVEL=INFO
      - DATABASE_PATH=/data/phase5_manual_reviews.db
    volumes:
      - reconciliation-data:/app/data
      - reconciliation-output:/app/output
    logging:
      driver: awslogs
      options:
        awslogs-group: /ecs/financial-reconciliation
        awslogs-region: us-west-2
        awslogs-stream-prefix: ecs

volumes:
  reconciliation-data:
  reconciliation-output:
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file or set system environment variables:

```bash
# Core Configuration
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
OUTPUT_DIR=output                 # Output directory path
DATABASE_PATH=data/phase5_manual_reviews.db  # Review database path

# Data Sources
LEGACY_DATA_PATH=test-data/legacy/
BANK_EXPORT_PATH=test-data/bank-exports/
PROCESSED_DATA_PATH=test-data/processed/

# Processing Options
DEFAULT_MODE=from_baseline        # from_baseline, from_scratch
AUTO_REVIEW_ENABLED=false        # Enable automatic categorization
BACKUP_ENABLED=true              # Create backups before processing

# Performance Tuning
MAX_CONCURRENT_PROCESSES=4       # Parallel processing limit
CHUNK_SIZE=1000                  # Records per processing chunk
MEMORY_LIMIT_MB=512             # Memory usage limit

# Security
SECURE_MODE=false               # Enable additional security checks
AUDIT_LOG_ENABLED=true          # Enable detailed audit logging

# Web Interface (if enabled)
WEB_HOST=0.0.0.0               # Web interface host
WEB_PORT=8080                  # Web interface port
WEB_DEBUG=false                # Enable web debug mode

# Database Settings
DB_CONNECTION_TIMEOUT=30        # Database connection timeout (seconds)
DB_QUERY_TIMEOUT=60            # Database query timeout (seconds)
DB_BACKUP_RETENTION_DAYS=30    # Backup retention period
```

### Configuration File

Alternative to environment variables:

```json
{
  "core": {
    "log_level": "INFO",
    "output_dir": "output",
    "database_path": "data/phase5_manual_reviews.db"
  },
  "data_sources": {
    "legacy_data_path": "test-data/legacy/",
    "bank_export_path": "test-data/bank-exports/",
    "processed_data_path": "test-data/processed/"
  },
  "processing": {
    "default_mode": "from_baseline",
    "auto_review_enabled": false,
    "backup_enabled": true
  },
  "performance": {
    "max_concurrent_processes": 4,
    "chunk_size": 1000,
    "memory_limit_mb": 512
  },
  "security": {
    "secure_mode": false,
    "audit_log_enabled": true
  },
  "web": {
    "host": "0.0.0.0",
    "port": 8080,
    "debug": false
  }
}
```

### Database Configuration

#### SQLite Configuration

```python
# Database optimization settings
import sqlite3

conn = sqlite3.connect('data/phase5_manual_reviews.db')
conn.execute('PRAGMA journal_mode = WAL')        # Write-Ahead Logging
conn.execute('PRAGMA synchronous = NORMAL')      # Balanced performance/safety
conn.execute('PRAGMA cache_size = 10000')        # 10MB cache
conn.execute('PRAGMA temp_store = MEMORY')       # Temp tables in memory
conn.execute('PRAGMA mmap_size = 268435456')     # 256MB memory-mapped I/O
conn.close()
```

#### Database Maintenance

```bash
# Regular maintenance script
#!/bin/bash
DB_PATH="data/phase5_manual_reviews.db"

# Backup database
cp "$DB_PATH" "$DB_PATH.backup.$(date +%Y%m%d_%H%M%S)"

# Optimize database
sqlite3 "$DB_PATH" "VACUUM;"
sqlite3 "$DB_PATH" "ANALYZE;"

# Check integrity
sqlite3 "$DB_PATH" "PRAGMA integrity_check;" | grep -v "ok" && echo "Database integrity issues found!"

# Clean old backups (keep last 30 days)
find . -name "*.backup.*" -mtime +30 -delete
```

## 🔧 System Service Configuration

### Systemd Service (Linux)

```ini
# /etc/systemd/system/financial-reconciliation.service
[Unit]
Description=Financial Reconciliation System
After=network.target

[Service]
Type=simple
User=reconciliation
Group=reconciliation
WorkingDirectory=/opt/financial-reconciliation
Environment=PYTHONPATH=/opt/financial-reconciliation
Environment=LOG_LEVEL=INFO
ExecStart=/opt/financial-reconciliation/venv/bin/python bin/run-with-review --mode from_baseline
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/financial-reconciliation/data /opt/financial-reconciliation/output

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable financial-reconciliation
sudo systemctl start financial-reconciliation

# Check status
sudo systemctl status financial-reconciliation
sudo journalctl -u financial-reconciliation -f
```

### Windows Service

```python
# windows_service.py
import win32serviceutil
import win32service
import win32event
import subprocess
import os

class FinancialReconciliationService(win32serviceutil.ServiceFramework):
    _svc_name_ = "FinancialReconciliation"
    _svc_display_name_ = "Financial Reconciliation System"
    _svc_description_ = "Automated financial transaction reconciliation service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        while self.is_alive:
            # Run reconciliation process
            try:
                result = subprocess.run([
                    'python', 'bin/run-with-review', '--mode', 'from_baseline'
                ], cwd=r'C:\opt\financial-reconciliation')
                
                if result.returncode != 0:
                    # Log error and retry
                    pass
                    
            except Exception as e:
                # Log exception
                pass
            
            # Wait for stop event or timeout (e.g., daily run)
            win32event.WaitForSingleObject(self.hWaitStop, 86400000)  # 24 hours

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(FinancialReconciliationService)
```

## 📊 Monitoring and Logging

### Logging Configuration

```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        },
        'simple': {
            'format': '%(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'logs/reconciliation.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': 'logs/errors.log'
        }
    },
    'loggers': {
        'src': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
            'propagate': False
        },
        'src.core': {
            'level': 'INFO',
            'handlers': ['file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'WARNING',
        'handlers': ['console', 'error_file']
    }
}

logging.config.dictConfig(LOGGING_CONFIG)
```

### Health Monitoring

```python
# health_check.py
import subprocess
import json
import time
from pathlib import Path

def check_system_health():
    """Comprehensive system health check."""
    health_status = {
        'timestamp': time.time(),
        'status': 'healthy',
        'checks': {}
    }
    
    # Check database connectivity
    try:
        import sqlite3
        conn = sqlite3.connect('data/phase5_manual_reviews.db', timeout=5)
        conn.execute('SELECT 1').fetchone()
        conn.close()
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'error: {e}'
        health_status['status'] = 'unhealthy'
    
    # Check disk space
    try:
        disk_usage = subprocess.check_output(['df', '-h', '.']).decode()
        health_status['checks']['disk_space'] = 'healthy'
    except Exception as e:
        health_status['checks']['disk_space'] = f'error: {e}'
    
    # Check required files
    required_files = [
        'bin/run-with-review',
        'src/core/accounting_engine.py',
        'requirements.txt'
    ]
    
    for file_path in required_files:
        if Path(file_path).exists():
            health_status['checks'][f'file_{file_path}'] = 'exists'
        else:
            health_status['checks'][f'file_{file_path}'] = 'missing'
            health_status['status'] = 'unhealthy'
    
    return health_status

if __name__ == '__main__':
    health = check_system_health()
    print(json.dumps(health, indent=2))
    exit(0 if health['status'] == 'healthy' else 1)
```

### Performance Monitoring

```bash
# monitoring_script.sh
#!/bin/bash

LOG_FILE="logs/performance.log"
mkdir -p logs

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # CPU and Memory usage
    CPU_USAGE=$(ps aux | grep python | grep financial-reconciliation | awk '{print $3}')
    MEM_USAGE=$(ps aux | grep python | grep financial-reconciliation | awk '{print $4}')
    
    # Database size
    DB_SIZE=$(du -h data/phase5_manual_reviews.db | cut -f1)
    
    # Log metrics
    echo "$TIMESTAMP,CPU:$CPU_USAGE%,MEM:$MEM_USAGE%,DB:$DB_SIZE" >> $LOG_FILE
    
    # Sleep for 5 minutes
    sleep 300
done
```

## 🚀 Production Deployment Checklist

### Pre-deployment

- [ ] **Environment Setup**
  - [ ] Python 3.8+ installed
  - [ ] Virtual environment created
  - [ ] Dependencies installed
  - [ ] Database initialized

- [ ] **Configuration**
  - [ ] Environment variables set
  - [ ] Configuration file created
  - [ ] Logging configured
  - [ ] Security settings applied

- [ ] **Testing**
  - [ ] Unit tests pass
  - [ ] Integration tests pass
  - [ ] End-to-end tests pass
  - [ ] Performance benchmarks meet requirements

### Deployment

- [ ] **System Preparation**
  - [ ] Service user created
  - [ ] File permissions set
  - [ ] System service configured
  - [ ] Firewall rules applied (if needed)

- [ ] **Application Deployment**
  - [ ] Code deployed to target directory
  - [ ] Configuration files copied
  - [ ] Database migrations applied
  - [ ] Static files deployed (if applicable)

- [ ] **Service Configuration**
  - [ ] Service definition created
  - [ ] Service enabled and started
  - [ ] Service status verified
  - [ ] Logs rotation configured

### Post-deployment

- [ ] **Verification**
  - [ ] Health check passes
  - [ ] Core functionality tested
  - [ ] Performance monitoring active
  - [ ] Error alerting configured

- [ ] **Documentation**
  - [ ] Deployment documented
  - [ ] Runbook updated
  - [ ] Contact information updated
  - [ ] Backup procedures documented

- [ ] **Monitoring Setup**
  - [ ] Log aggregation configured
  - [ ] Metrics collection active
  - [ ] Alerting rules configured
  - [ ] Dashboard created

## 🔐 Security Considerations

### Access Control

```bash
# File permissions
chmod 750 /opt/financial-reconciliation
chmod 640 /opt/financial-reconciliation/data/*.db
chmod 644 /opt/financial-reconciliation/*.py

# User permissions
sudo usermod -a -G reconciliation backup_user
```

### Network Security

```bash
# Firewall configuration (if web interface enabled)
sudo ufw allow 8080/tcp
sudo ufw enable

# SSL/TLS configuration for web interface
# Use reverse proxy (nginx/Apache) with SSL certificates
```

### Data Protection

```bash
# Database encryption (if sensitive data)
# Use SQLCipher or full-disk encryption

# Backup encryption
gpg --symmetric --cipher-algo AES256 backup_file.db
```

## 🔄 Backup and Recovery

### Automated Backup

```bash
#!/bin/bash
# backup_script.sh

BACKUP_DIR="/opt/backups/financial-reconciliation"
DATE=$(date +%Y%m%d_%H%M%S)
DB_PATH="data/phase5_manual_reviews.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/database_$DATE.db'"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env config/

# Backup code (optional, if local changes)
tar -czf "$BACKUP_DIR/code_$DATE.tar.gz" --exclude=venv --exclude=__pycache__ .

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Recovery Procedures

```bash
# Database recovery
cp /opt/backups/financial-reconciliation/database_YYYYMMDD_HHMMSS.db data/phase5_manual_reviews.db

# Configuration recovery
tar -xzf /opt/backups/financial-reconciliation/config_YYYYMMDD_HHMMSS.tar.gz

# Service restart
sudo systemctl restart financial-reconciliation
```

---

**Need Help?** Check the [Troubleshooting Guide](TROUBLESHOOTING.md) or open an issue on GitHub.

**Last Updated:** July 31, 2025