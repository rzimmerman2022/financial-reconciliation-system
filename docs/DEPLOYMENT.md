# Deployment Guide

**Last Updated:** August 10, 2025  
**Version:** 6.0.0  
**Description:** Step-by-step deployment instructions for production environments

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development Setup](#local-development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration Management](#configuration-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

#### Minimum Requirements
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM available
- **Storage**: 1GB free space
- **Network**: Internet access for package installation

#### Recommended Requirements
- **OS**: Latest stable versions
- **Python**: 3.11+ for best performance
- **Memory**: 4GB+ RAM for large datasets
- **Storage**: 5GB+ for data and logs
- **CPU**: Multi-core processor for parallel processing

### Software Dependencies

#### Required Python Packages
```bash
# Core dependencies
flask>=3.1.0
pandas>=1.5.0
customtkinter>=5.2.0
openpyxl>=3.1.0
python-dateutil>=2.8.0

# Optional but recommended
gunicorn>=21.0.0  # For production WSGI server
nginx             # For reverse proxy (Linux/macOS)
```

#### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-dev python3-pip python3-venv
sudo apt-get install sqlite3 libsqlite3-dev

# CentOS/RHEL
sudo yum install python3-devel python3-pip
sudo yum install sqlite sqlite-devel

# macOS (with Homebrew)
brew install python sqlite

# Windows
# Install Python from python.org
# SQLite is included with Python
```

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/rzimmerman2022/financial-reconciliation-system.git
cd financial-reconciliation-system
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -e ".[dev]"
```

### 4. Configure Environment
```bash
# Copy configuration template
cp config/config.yaml config/local.yaml

# Edit configuration for local development
# Set debug mode, local database paths, etc.
```

### 5. Initialize Database
```bash
# Create data directory
mkdir -p data

# Initialize manual review database
python -c "
from src.review.manual_review_system import ManualReviewSystem
db = ManualReviewSystem('data/manual_reviews.db')
print('Database initialized successfully')
"
```

### 6. Verify Installation
```bash
# Run basic reconciliation test
python reconcile.py --help

# Run test suite
python src/scripts/run_tests.py

# Start web interface
python bin/launch_web_interface
```

## Production Deployment

### Linux Server Deployment

#### 1. Server Preparation
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install required system packages
sudo apt-get install -y python3 python3-pip python3-venv
sudo apt-get install -y nginx supervisor
sudo apt-get install -y sqlite3 libsqlite3-dev

# Create application user
sudo adduser --system --group reconciliation
sudo mkdir -p /opt/financial-reconciliation
sudo chown reconciliation:reconciliation /opt/financial-reconciliation
```

#### 2. Application Setup
```bash
# Switch to application user
sudo -u reconciliation -s

# Clone and setup application
cd /opt/financial-reconciliation
git clone https://github.com/rzimmerman2022/financial-reconciliation-system.git .
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### 3. Configuration
```bash
# Create production configuration
sudo -u reconciliation bash -c '
cat > /opt/financial-reconciliation/config/production.yaml << EOF
reconciliation:
  default_mode: "from_baseline"
  
web_interface:
  host: "127.0.0.1"
  port: 5000
  debug: false
  
logging:
  level: "INFO"
  file_logging: true
  log_directory: "/opt/financial-reconciliation/logs"
  
manual_review:
  database_path: "/opt/financial-reconciliation/data/manual_reviews.db"
EOF
'

# Create directories
sudo -u reconciliation mkdir -p /opt/financial-reconciliation/{data,logs,output}
```

#### 4. WSGI Server Setup
```bash
# Create Gunicorn configuration
sudo -u reconciliation bash -c '
cat > /opt/financial-reconciliation/gunicorn.conf.py << EOF
# Gunicorn configuration
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
user = "reconciliation"
group = "reconciliation"
chdir = "/opt/financial-reconciliation"
accesslog = "/opt/financial-reconciliation/logs/access.log"
errorlog = "/opt/financial-reconciliation/logs/error.log"
loglevel = "info"
EOF
'
```

#### 5. Supervisor Configuration
```bash
# Create supervisor configuration
sudo bash -c '
cat > /etc/supervisor/conf.d/financial-reconciliation.conf << EOF
[program:financial-reconciliation]
command=/opt/financial-reconciliation/venv/bin/gunicorn --config gunicorn.conf.py "src.web.reconcile_web:app"
directory=/opt/financial-reconciliation
user=reconciliation
group=reconciliation
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/financial-reconciliation/logs/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=PYTHONPATH="/opt/financial-reconciliation"
EOF
'

# Reload supervisor and start application
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start financial-reconciliation
```

#### 6. Nginx Configuration
```bash
# Create Nginx configuration
sudo bash -c '
cat > /etc/nginx/sites-available/financial-reconciliation << EOF
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static {
        alias /opt/financial-reconciliation/src/review/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000;
    }
}
EOF
'

# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/financial-reconciliation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Windows Server Deployment

#### 1. IIS Setup (Alternative to Nginx)
```powershell
# Install IIS and required features
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServer
Enable-WindowsOptionalFeature -Online -FeatureName IIS-CommonHttpFeatures
Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpRedirect

# Install wfastcgi for Python applications
pip install wfastcgi
wfastcgi-enable
```

#### 2. Windows Service Setup
```powershell
# Create Windows service using NSSM (Non-Sucking Service Manager)
# Download NSSM from https://nssm.cc/

# Install service
nssm install FinancialReconciliation "C:\Python39\python.exe" "-m" "src.review.web_interface"
nssm set FinancialReconciliation AppDirectory "C:\financial-reconciliation"
nssm set FinancialReconciliation DisplayName "Financial Reconciliation System"
nssm set FinancialReconciliation Description "Financial transaction reconciliation web service"

# Start service
nssm start FinancialReconciliation
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
# Create Dockerfile in project root
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install production WSGI server
RUN pip install gunicorn

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash reconciliation
RUN chown -R reconciliation:reconciliation /app
USER reconciliation

# Create necessary directories
RUN mkdir -p data logs output

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "src.web.reconcile_web:app"]
```

### 2. Create Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./output:/app/output
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - RECONCILIATION_CONFIG_FILE=/app/config/production.yaml
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro  # If using SSL
    depends_on:
      - web
    restart: unless-stopped

volumes:
  data:
  logs:
```

### 3. Nginx Configuration for Docker
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 4. Deploy with Docker Compose
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Update deployment
docker-compose pull
docker-compose up -d --force-recreate
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Security group: Allow HTTP (80), HTTPS (443), SSH (22)

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update and install dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx supervisor git

# Clone and setup application (follow Linux deployment steps above)
```

#### 2. RDS Database (Optional)
```bash
# If using RDS PostgreSQL instead of SQLite
pip install psycopg2-binary

# Update configuration for PostgreSQL
# DATABASE_URL=postgresql://user:password@endpoint:5432/database
```

#### 3. S3 for File Storage (Optional)
```bash
# Install AWS SDK
pip install boto3

# Configure S3 for file uploads/exports
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# AWS_BUCKET_NAME=your-bucket
```

### Google Cloud Platform

#### 1. App Engine Deployment
```yaml
# app.yaml
runtime: python311

env_variables:
  FLASK_ENV: production
  RECONCILIATION_CONFIG_FILE: config/production.yaml

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
```

#### 2. Deploy to App Engine
```bash
# Install Google Cloud SDK
# Follow: https://cloud.google.com/sdk/docs/install

# Deploy application
gcloud app deploy
gcloud app browse
```

### Heroku Deployment

#### 1. Create Heroku Configuration
```python
# Create Procfile
web: gunicorn --bind 0.0.0.0:$PORT src.web.reconcile_web:app
```

```python
# Create runtime.txt
python-3.11.9
```

#### 2. Deploy to Heroku
```bash
# Install Heroku CLI
# Follow: https://devcenter.heroku.com/articles/heroku-cli

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set RECONCILIATION_CONFIG_FILE=config/production.yaml

# Deploy
git push heroku main

# Open application
heroku open
```

## Configuration Management

### Environment Variables

#### Production Environment Variables
```bash
# Core application settings
export FLASK_ENV=production
export FLASK_APP=src.web.reconcile_web
export RECONCILIATION_CONFIG_FILE=/path/to/production.yaml

# Database settings
export RECONCILIATION_DB_PATH=/path/to/production.db

# Logging settings
export RECONCILIATION_LOG_LEVEL=INFO
export RECONCILIATION_LOG_DIR=/path/to/logs

# Security settings
export SECRET_KEY=your-secret-key-here
export WTF_CSRF_SECRET_KEY=your-csrf-secret-here

# Web server settings
export GUNICORN_WORKERS=2
export GUNICORN_TIMEOUT=120
export GUNICORN_BIND=127.0.0.1:5000
```

#### Docker Environment File
```bash
# Create .env file for docker-compose
cat > .env << EOF
FLASK_ENV=production
RECONCILIATION_CONFIG_FILE=/app/config/production.yaml
SECRET_KEY=your-production-secret-key
WTF_CSRF_SECRET_KEY=your-csrf-secret-key
GUNICORN_WORKERS=2
EOF
```

### Configuration Files

#### Production Configuration Template
```yaml
# config/production.yaml
reconciliation:
  default_mode: "from_baseline"
  amount_tolerance: 0.01
  date_tolerance_days: 1

web_interface:
  host: "127.0.0.1"
  port: 5000
  debug: false
  auto_open_browser: false

logging:
  level: "INFO"
  file_logging: true
  log_directory: "/var/log/financial-reconciliation"
  max_file_size: "10MB"
  backup_count: 5

manual_review:
  database_path: "/opt/financial-reconciliation/data/manual_reviews.db"
  batch_size: 50

export:
  excel_format: "xlsx"
  csv_encoding: "utf-8"
```

## Monitoring and Logging

### Application Logging
```python
# Configure logging in production
import logging
from logging.handlers import RotatingFileHandler

# Setup rotating file handler
handler = RotatingFileHandler(
    '/var/log/financial-reconciliation/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)

# Setup formatter
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s %(name)s: %(message)s'
)
handler.setFormatter(formatter)

# Configure logger
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)
```

### System Monitoring
```bash
# Monitor application processes
sudo supervisorctl status financial-reconciliation

# Monitor system resources
htop
df -h
free -h

# Monitor logs in real-time
tail -f /opt/financial-reconciliation/logs/app.log
tail -f /opt/financial-reconciliation/logs/access.log
tail -f /opt/financial-reconciliation/logs/error.log
```

### Health Check Endpoint
```python
# Add health check to your Flask app
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check database connectivity
        db = ManualReviewSystem()
        db.get_connection()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '6.0.0'
        }, 200
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500
```

### Monitoring with Prometheus (Optional)
```bash
# Install prometheus client
pip install prometheus-client

# Add metrics endpoint
from prometheus_client import Counter, Histogram, generate_latest

# Create metrics
request_count = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## Security Considerations

### Basic Security Measures
```bash
# Create secure configuration
chmod 600 config/production.yaml

# Set up firewall (UFW on Ubuntu)
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# Keep system updated
sudo apt-get update && sudo apt-get upgrade -y

# Install security updates automatically
sudo apt-get install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### SSL/TLS Setup with Let's Encrypt
```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Verify auto-renewal
sudo certbot renew --dry-run

# Crontab entry for auto-renewal (usually added automatically)
# 0 12 * * * /usr/bin/certbot renew --quiet
```

### Security Headers
```nginx
# Add to Nginx configuration
server {
    # ... existing configuration ...
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options "nosniff";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";
}
```

## Troubleshooting

### Common Issues

#### 1. Permission Errors
```bash
# Fix file permissions
sudo chown -R reconciliation:reconciliation /opt/financial-reconciliation
sudo chmod -R 755 /opt/financial-reconciliation
sudo chmod 600 /opt/financial-reconciliation/config/production.yaml
```

#### 2. Database Connection Issues
```bash
# Check SQLite database
sqlite3 /path/to/manual_reviews.db ".tables"

# Check database permissions
ls -la /path/to/manual_reviews.db

# Recreate database if needed
rm /path/to/manual_reviews.db
python -c "
from src.review.manual_review_system import ManualReviewSystem
db = ManualReviewSystem('/path/to/manual_reviews.db')
"
```

#### 3. Web Server Issues
```bash
# Check Gunicorn process
sudo supervisorctl status financial-reconciliation

# Restart application
sudo supervisorctl restart financial-reconciliation

# Check application logs
tail -f /opt/financial-reconciliation/logs/app.log

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

#### 4. Port Conflicts
```bash
# Check what's using port 5000
sudo netstat -tlnp | grep :5000

# Kill process using port
sudo kill -9 <process_id>

# Use different port
export PORT=5001
```

### Debug Mode
```bash
# Enable debug mode for troubleshooting (NOT for production)
export FLASK_ENV=development
export FLASK_DEBUG=1

# Run in debug mode
python bin/launch_web_interface
```

### Performance Issues
```bash
# Check system resources
htop
iotop
df -h

# Check application performance
python -m cProfile -m src.review.web_interface

# Monitor database queries
sqlite3 /path/to/manual_reviews.db
.timer on
-- Run your queries here
```

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Financial Reconciliation System in various environments. Choose the deployment method that best fits your infrastructure requirements and security needs.

For production deployments, always:
1. Use environment-specific configurations
2. Implement proper monitoring and logging
3. Set up automated backups
4. Follow security best practices
5. Keep systems updated
6. Test deployments thoroughly

If you encounter issues not covered in this guide, check the troubleshooting section or create an issue in the project repository.