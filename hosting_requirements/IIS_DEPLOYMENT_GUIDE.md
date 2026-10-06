# Asset Tracker - IIS Deployment Guide

## Complete Step-by-Step Guide to Deploy Django Asset Tracker on IIS

This guide provides comprehensive instructions for deploying your Django Asset Tracker application on Windows IIS (Internet Information Services).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Step-by-Step Deployment](#step-by-step-deployment)
4. [Post-Deployment Configuration](#post-deployment-configuration)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

---

## Prerequisites

### Required Software

1. **Windows Server 2016 or later** (or Windows 10/11 Pro)
2. **IIS (Internet Information Services) 10.0 or later**
3. **Python 3.9 or later** (64-bit recommended)
4. **Microsoft Visual C++ Redistributable** (for Python packages)
5. **URL Rewrite Module** for IIS
6. **WFastCGI** (Python package for IIS integration)
7. **Redis Server** (for Celery tasks)
8. **PostgreSQL** or **SQL Server** (recommended for production) or **SQLite** (development only)

### Minimum Server Requirements

- **CPU**: 2 cores (4 cores recommended)
- **RAM**: 4 GB minimum (8 GB recommended)
- **Disk Space**: 10 GB free space
- **Network**: Static IP address or domain name

---

## Pre-Deployment Checklist

### 1. Install Python

```powershell
# Download Python from https://www.python.org/downloads/
# During installation, check:
# ☑ Add Python to PATH
# ☑ Install pip
# ☑ Install for all users

# Verify installation
python --version
pip --version
```

### 2. Install IIS with Required Features

Open PowerShell as Administrator and run:

```powershell
# Install IIS with all required features
Install-WindowsFeature -name Web-Server -IncludeManagementTools
Install-WindowsFeature -name Web-CGI
Install-WindowsFeature -name Web-Http-Redirect
Install-WindowsFeature -name Web-Custom-Logging
Install-WindowsFeature -name Web-Log-Libraries
```

Or install via GUI:
- Open **Server Manager**
- Click **Add Roles and Features**
- Select **Web Server (IIS)**
- Under **Application Development**, check:
  - ☑ CGI
  - ☑ ISAPI Extensions
  - ☑ ISAPI Filters

### 3. Install IIS URL Rewrite Module

```powershell
# Download and install from:
# https://www.iis.net/downloads/microsoft/url-rewrite

# Or use Chocolatey:
choco install urlrewrite -y
```

### 4. Install Redis (for Celery)

```powershell
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases

# Or use Chocolatey:
choco install redis-64 -y

# Start Redis service
redis-server --service-start
```

### 5. Install PostgreSQL (Optional, but recommended)

```powershell
# Download from: https://www.postgresql.org/download/windows/
# Or use Chocolatey:
choco install postgresql -y
```

---

## Step-by-Step Deployment

### Step 1: Prepare Application Files

1. **Create deployment directory:**
   ```powershell
   New-Item -ItemType Directory -Path "C:\inetpub\wwwroot\AssetTracker" -Force
   ```

2. **Copy application files:**
   ```powershell
   # Copy entire application to deployment directory
   Copy-Item -Path "D:\Asset tracker\*" -Destination "C:\inetpub\wwwroot\AssetTracker" -Recurse -Force
   
   # Exclude unnecessary files
   Remove-Item "C:\inetpub\wwwroot\AssetTracker\.git" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item "C:\inetpub\wwwroot\AssetTracker\*.pyc" -Recurse -Force -ErrorAction SilentlyContinue
   Remove-Item "C:\inetpub\wwwroot\AssetTracker\__pycache__" -Recurse -Force -ErrorAction SilentlyContinue
   ```

### Step 2: Set Up Virtual Environment

```powershell
# Navigate to application directory
cd C:\inetpub\wwwroot\AssetTracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install wfastcgi (CRITICAL for IIS)
pip install wfastcgi

# Enable wfastcgi
wfastcgi-enable
```

**IMPORTANT**: Copy the output path from `wfastcgi-enable`. You'll need it later.
Example: `C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe|C:\inetpub\wwwroot\AssetTracker\venv\Lib\site-packages\wfastcgi.py`

### Step 3: Configure Environment Variables

1. **Create production .env file:**
   ```powershell
   Copy-Item "C:\inetpub\wwwroot\AssetTracker\.env.example" -Destination "C:\inetpub\wwwroot\AssetTracker\.env"
   ```

2. **Edit .env file** with production settings:
   ```ini
   # Use the provided .env.production template
   # Update with your actual values
   ```

### Step 4: Configure Database

**For PostgreSQL:**

```powershell
# Create database
psql -U postgres
```

```sql
CREATE DATABASE asset_tracker;
CREATE USER asset_tracker_user WITH PASSWORD 'YourSecurePassword123!';
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;
\q
```

Update `.env`:
```ini
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=asset_tracker
DATABASE_USER=asset_tracker_user
DATABASE_PASSWORD=YourSecurePassword123!
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### Step 5: Run Django Setup Commands

```powershell
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 6: Set Folder Permissions

```powershell
# Grant IIS_IUSRS full control
$path = "C:\inetpub\wwwroot\AssetTracker"
$acl = Get-Acl $path
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule("IIS_IUSRS", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.AddAccessRule($rule)
Set-Acl $path $acl

# Grant specific permissions to critical folders
icacls "C:\inetpub\wwwroot\AssetTracker\media" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\inetpub\wwwroot\AssetTracker\staticfiles" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "C:\inetpub\wwwroot\AssetTracker\db.sqlite3" /grant "IIS_IUSRS:F" /T
```

### Step 7: Create IIS Website

1. **Open IIS Manager** (`inetmgr`)

2. **Create Application Pool:**
   - Right-click **Application Pools** → **Add Application Pool**
   - **Name**: `AssetTrackerPool`
   - **.NET CLR Version**: `No Managed Code`
   - **Managed Pipeline Mode**: `Integrated`
   - Click **OK**
   
3. **Configure Application Pool:**
   - Right-click `AssetTrackerPool` → **Advanced Settings**
   - Set **Identity** → **Custom account** → `IIS_IUSRS` (or specific service account)
   - Set **Start Mode**: `AlwaysRunning`
   - Set **Idle Time-out (minutes)**: `0` (disable timeout)
   - Click **OK**

4. **Create Website:**
   - Right-click **Sites** → **Add Website**
   - **Site name**: `AssetTracker`
   - **Application pool**: `AssetTrackerPool`
   - **Physical path**: `C:\inetpub\wwwroot\AssetTracker`
   - **Binding**:
     - Type: `http`
     - IP: `All Unassigned` or your server IP
     - Port: `80` (or your preferred port)
     - Host name: `assettracker.yourdomain.com` (optional)
   - Click **OK**

### Step 8: Configure FastCGI Handler

1. **Open IIS Manager** → Select `AssetTracker` site

2. **Add Handler Mapping:**
   - Double-click **Handler Mappings**
   - Click **Add Module Mapping** (right panel)
   - **Request path**: `*`
   - **Module**: `FastCgiModule`
   - **Executable**: `C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe|C:\inetpub\wwwroot\AssetTracker\venv\Lib\site-packages\wfastcgi.py`
     (Use the path from `wfastcgi-enable` output)
   - **Name**: `Django Handler`
   - Click **Request Restrictions**:
     - Uncheck **Invoke handler only if request is mapped to:**
   - Click **OK** → **Yes** to confirm

### Step 9: Configure web.config

Copy the provided `web.config` file to `C:\inetpub\wwwroot\AssetTracker\web.config`

**CRITICAL**: Update the following values in `web.config`:
- `PYTHONPATH` → Your application path
- `WSGI_HANDLER` → `asset_tracker.wsgi.application`
- `DJANGO_SETTINGS_MODULE` → `asset_tracker.settings`

### Step 10: Test the Deployment

1. **Restart IIS:**
   ```powershell
   iisreset /restart
   ```

2. **Access the application:**
   - Open browser: `http://your-server-ip/` or `http://assettracker.yourdomain.com/`

3. **Check for errors:**
   - View IIS logs: `C:\inetpub\logs\LogFiles\`
   - View Django logs: `C:\inetpub\wwwroot\AssetTracker\authentication.log`

---

## Post-Deployment Configuration

### 1. Configure SSL/HTTPS (Recommended)

```powershell
# Install SSL certificate
# Option 1: Use IIS Manager to bind SSL certificate
# Option 2: Use Let's Encrypt with Certify The Web

# Update .env for HTTPS:
```
```ini
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
```

### 2. Set Up Celery as Windows Service

```powershell
# Install NSSM (Non-Sucking Service Manager)
choco install nssm -y

# Create Celery Worker Service
nssm install AssetTrackerCelery "C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe"
nssm set AssetTrackerCelery AppDirectory "C:\inetpub\wwwroot\AssetTracker"
nssm set AssetTrackerCelery AppParameters "-m celery -A asset_tracker worker -l info"
nssm set AssetTrackerCelery DisplayName "Asset Tracker Celery Worker"
nssm set AssetTrackerCelery Description "Celery worker for Asset Tracker background tasks"
nssm set AssetTrackerCelery Start SERVICE_AUTO_START
nssm start AssetTrackerCelery

# Create Celery Beat Service
nssm install AssetTrackerCeleryBeat "C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe"
nssm set AssetTrackerCeleryBeat AppDirectory "C:\inetpub\wwwroot\AssetTracker"
nssm set AssetTrackerCeleryBeat AppParameters "-m celery -A asset_tracker beat -l info"
nssm set AssetTrackerCeleryBeat DisplayName "Asset Tracker Celery Beat"
nssm set AssetTrackerCeleryBeat Description "Celery beat scheduler for Asset Tracker"
nssm set AssetTrackerCeleryBeat Start SERVICE_AUTO_START
nssm start AssetTrackerCeleryBeat
```

### 3. Configure Automatic Backups

Create a scheduled task for database backups:

```powershell
# Create backup script (see backup_database.ps1)
# Schedule it with Task Scheduler

schtasks /create /tn "AssetTracker_DailyBackup" /tr "C:\inetpub\wwwroot\AssetTracker\hosting_requirements\backup_database.ps1" /sc daily /st 02:00 /ru SYSTEM
```

### 4. Configure Monitoring

- Set up Windows Event Log monitoring
- Configure email alerts for errors
- Set up performance counters

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: HTTP 500 Error

**Solution:**
```powershell
# Enable detailed errors in web.config
# Check FastCGI settings
# Review IIS logs
```

#### Issue 2: Static Files Not Loading

**Solution:**
```powershell
# Re-run collectstatic
python manage.py collectstatic --noinput

# Check IIS static file handling
# Verify folder permissions
```

#### Issue 3: Database Connection Failed

**Solution:**
```powershell
# Verify database credentials in .env
# Check database service is running
# Test connection with psql or SQL Server Management Studio
```

#### Issue 4: Celery Tasks Not Running

**Solution:**
```powershell
# Check Redis is running
redis-cli ping

# Check Celery service status
nssm status AssetTrackerCelery

# Review Celery logs
```

### Debug Mode (Temporary)

```ini
# In .env, temporarily enable debug
DEBUG=True

# View detailed error messages
# IMPORTANT: Disable after troubleshooting
```

---

## Maintenance

### Regular Maintenance Tasks

1. **Weekly:**
   - Review error logs
   - Check disk space
   - Monitor application performance

2. **Monthly:**
   - Update Python packages
   - Review security updates
   - Test backup restoration

3. **Quarterly:**
   - Update Django version
   - Review and optimize database
   - Security audit

### Updating the Application

```powershell
# Stop Celery services
nssm stop AssetTrackerCelery
nssm stop AssetTrackerCeleryBeat

# Backup database
# (See backup_database.ps1)

# Pull latest code
cd C:\inetpub\wwwroot\AssetTracker
git pull origin main

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Update dependencies
pip install -r requirements.txt --upgrade

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart IIS
iisreset /restart

# Start Celery services
nssm start AssetTrackerCelery
nssm start AssetTrackerCeleryBeat
```

---

## Security Best Practices

1. **Never expose .env file** to the web
2. **Use strong SECRET_KEY** in production
3. **Enable HTTPS** with valid SSL certificate
4. **Regular security updates** for Python, Django, and Windows
5. **Implement rate limiting** for API endpoints
6. **Regular backups** with off-site storage
7. **Monitor access logs** for suspicious activity
8. **Use firewall** to restrict access
9. **Disable DEBUG** in production
10. **Use environment variables** for sensitive data

---

## Support and Resources

- **Django Documentation**: https://docs.djangoproject.com/
- **IIS Documentation**: https://docs.microsoft.com/en-us/iis/
- **FastCGI for IIS**: https://pypi.org/project/wfastcgi/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

## Checklist Summary

- [ ] Python 3.9+ installed
- [ ] IIS installed with CGI module
- [ ] URL Rewrite Module installed
- [ ] Redis installed and running
- [ ] Database (PostgreSQL/SQL Server) set up
- [ ] Application files copied to `C:\inetpub\wwwroot\AssetTracker`
- [ ] Virtual environment created and packages installed
- [ ] wfastcgi installed and enabled
- [ ] .env file configured with production settings
- [ ] Database migrations run
- [ ] Static files collected
- [ ] Folder permissions set
- [ ] IIS Application Pool created
- [ ] IIS Website created
- [ ] FastCGI Handler configured
- [ ] web.config file configured
- [ ] Application tested and working
- [ ] SSL certificate installed (recommended)
- [ ] Celery services configured
- [ ] Backup system configured
- [ ] Monitoring set up

---

**Last Updated**: August 2026
**Version**: 1.0
