# Asset Tracker - Linux Deployment Guide

Complete guide for deploying the Asset Tracker Django application on a Linux server (Ubuntu/Debian).

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Server Setup](#server-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Troubleshooting](#troubleshooting)
7. [Maintenance](#maintenance)

---

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or later (or Debian 10+)
- Minimum 2GB RAM
- 20GB disk space
- Root or sudo access

### Software Requirements
- Python 3.8+
- PostgreSQL 12+ or MySQL 8+
- Nginx
- Git

---

## Server Setup

### 1. Update System Packages

```bash
sudo apt update
sudo apt upgrade -y
```

### 2. Install Required Packages

```bash
# Install Python and development tools
sudo apt install -y python3 python3-pip python3-venv python3-dev

# Install PostgreSQL (recommended)
sudo apt install -y postgresql postgresql-contrib libpq-dev

# OR Install MySQL (alternative)
# sudo apt install -y mysql-server mysql-client libmysqlclient-dev

# Install Nginx
sudo apt install -y nginx

# Install Git
sudo apt install -y git

# Install other dependencies
sudo apt install -y build-essential libssl-dev libffi-dev
```

### 3. Create Application Directory

```bash
sudo mkdir -p /var/www/asset_tracker
sudo mkdir -p /var/log/asset_tracker
sudo mkdir -p /var/run/asset_tracker
```

---

## Database Setup

### Option A: PostgreSQL (Recommended)

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, create database and user:
CREATE DATABASE asset_tracker_db;
CREATE USER asset_tracker_user WITH PASSWORD 'your_secure_password';
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker_db TO asset_tracker_user;
\q
```

### Option B: MySQL

```bash
# Login to MySQL
sudo mysql -u root -p

# In MySQL shell, create database and user:
CREATE DATABASE asset_tracker_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'asset_tracker_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON asset_tracker_db.* TO 'asset_tracker_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## Application Deployment

### 1. Clone/Upload Project Files

**Option A: Using Git**
```bash
cd /var/www
sudo git clone https://your_repo_url/asset_tracker.git
```

**Option B: Upload from Windows**
```bash
# On Windows machine, create a zip file (exclude venv, __pycache__, .git)
# Then upload to server using SCP or FTP
scp -r "D:\Asset tracker" user@your_server:/tmp/

# On server, move to destination
sudo mv /tmp/asset_tracker /var/www/
```

### 2. Set Up Environment Variables

```bash
cd /var/www/asset_tracker
sudo cp linux_hosting/.env.example .env
sudo nano .env  # Edit with your actual values
```

**Important: Update these values in .env:**
- `SECRET_KEY` - Generate a new one: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DB_PASSWORD` - Your database password
- `ALLOWED_HOSTS` - Your domain or IP address
- `EMAIL_*` - Your email settings

### 3. Create Python Virtual Environment

```bash
cd /var/www/asset_tracker
sudo python3 -m venv venv
sudo chown -R www-data:www-data venv
source venv/bin/activate
```

### 4. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r linux_hosting/requirements_production.txt
pip install gunicorn psycopg2-binary  # Add mysqlclient if using MySQL
```

### 5. Update Django Settings

Edit `/var/www/asset_tracker/asset_tracker/settings.py`:

```python
# Add at the top
import os
from dotenv import load_dotenv
load_dotenv()

# Update these settings:
DEBUG = False
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Import production settings
if not DEBUG:
    from .settings_production import *
```

### 6. Run Migrations and Collect Static Files

```bash
cd /var/www/asset_tracker
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Set permissions
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

### 7. Configure Nginx

```bash
# Copy Nginx configuration
sudo cp /var/www/asset_tracker/linux_hosting/nginx.conf /etc/nginx/sites-available/asset_tracker

# Edit the configuration to match your domain
sudo nano /etc/nginx/sites-available/asset_tracker
# Update: server_name your_domain.com;

# Enable the site
sudo ln -s /etc/nginx/sites-available/asset_tracker /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

### 8. Set Up Gunicorn as Systemd Service

```bash
# Copy service files
sudo cp /var/www/asset_tracker/linux_hosting/gunicorn.service /etc/systemd/system/asset_tracker.service
sudo cp /var/www/asset_tracker/linux_hosting/gunicorn.socket /etc/systemd/system/asset_tracker.socket

# Update paths in service file if needed
sudo nano /etc/systemd/system/asset_tracker.service

# Reload systemd daemon
sudo systemctl daemon-reload

# Start and enable services
sudo systemctl start asset_tracker.socket
sudo systemctl enable asset_tracker.socket
sudo systemctl start asset_tracker
sudo systemctl enable asset_tracker

# Check status
sudo systemctl status asset_tracker
```

### 9. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

---

## SSL Certificate Setup (Optional but Recommended)

### Using Let's Encrypt (Free SSL)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your_domain.com -d www.your_domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

The certificate will auto-renew. Certbot will automatically update your Nginx configuration.

---

## Troubleshooting

### Check Service Status

```bash
# Check Gunicorn status
sudo systemctl status asset_tracker

# Check Nginx status
sudo systemctl status nginx

# Check logs
sudo journalctl -u asset_tracker -f
sudo tail -f /var/log/asset_tracker/gunicorn_error.log
sudo tail -f /var/log/nginx/asset_tracker_error.log
```

### Common Issues

**1. 502 Bad Gateway**
```bash
# Check if Gunicorn is running
sudo systemctl status asset_tracker

# Check socket permissions
ls -l /run/asset_tracker.sock

# Restart services
sudo systemctl restart asset_tracker
sudo systemctl restart nginx
```

**2. Static Files Not Loading**
```bash
# Run collectstatic again
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --noinput

# Check permissions
sudo chown -R www-data:www-data /var/www/asset_tracker/staticfiles
```

**3. Database Connection Errors**
```bash
# Check database is running
sudo systemctl status postgresql  # or mysql

# Verify credentials in .env file
cat /var/www/asset_tracker/.env

# Test database connection
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py dbshell
```

**4. Permission Denied Errors**
```bash
# Fix all permissions
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chown -R www-data:www-data /var/log/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

---

## Maintenance

### Update Application

```bash
# Pull latest changes
cd /var/www/asset_tracker
sudo git pull origin main  # or your branch name

# Activate virtual environment
source venv/bin/activate

# Install new dependencies (if any)
pip install -r linux_hosting/requirements_production.txt

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart Gunicorn
sudo systemctl restart asset_tracker
```

### Backup Database

**PostgreSQL:**
```bash
sudo -u postgres pg_dump asset_tracker_db > /tmp/asset_tracker_backup_$(date +%Y%m%d).sql
```

**MySQL:**
```bash
mysqldump -u asset_tracker_user -p asset_tracker_db > /tmp/asset_tracker_backup_$(date +%Y%m%d).sql
```

### Monitor Logs

```bash
# Real-time application logs
sudo journalctl -u asset_tracker -f

# Real-time Nginx logs
sudo tail -f /var/log/nginx/asset_tracker_access.log
sudo tail -f /var/log/nginx/asset_tracker_error.log

# Gunicorn logs
sudo tail -f /var/log/asset_tracker/gunicorn_error.log
```

### Restart Services

```bash
# Restart Gunicorn
sudo systemctl restart asset_tracker

# Restart Nginx
sudo systemctl restart nginx

# Restart both
sudo systemctl restart asset_tracker nginx
```

---

## Security Checklist

- [ ] `DEBUG = False` in settings
- [ ] Strong `SECRET_KEY` set
- [ ] Database uses strong password
- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] Regular backups scheduled
- [ ] Log rotation configured
- [ ] Security updates enabled: `sudo apt install unattended-upgrades`
- [ ] Non-root user for SSH access
- [ ] SSH key authentication enabled
- [ ] Unnecessary ports closed

---

## Performance Optimization

### Enable Caching (Redis)

```bash
# Install Redis
sudo apt install -y redis-server

# Install Python Redis client
pip install redis django-redis

# Update settings.py with Redis cache configuration
```

### Database Optimization

```bash
# PostgreSQL: Add indexes for frequently queried fields
# MySQL: Enable query cache and optimize tables
```

---

## Support

For issues or questions:
1. Check application logs
2. Review Nginx error logs
3. Verify all configuration files
4. Check service status

---

**Last Updated:** December 2024
**Django Version:** 4.2.30
**Python Version:** 3.8+
