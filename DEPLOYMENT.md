# Asset Tracker - Test Server Deployment Guide

This guide covers deploying the Asset Tracker application to a Windows test server.

## Prerequisites

- Windows Server (2016 or later recommended)
- Python 3.11+ installed
- PostgreSQL or use SQLite for testing
- Admin access to the server
- Network access to the server

## Deployment Options

### Option A: Quick Test Deployment (SQLite - Simple)
### Option B: Production-like Deployment (PostgreSQL + IIS - Recommended for test server)

---

## Option A: Quick Test Deployment (SQLite)

### 1. Prepare the Server

1. **Install Python 3.11+**
   ```powershell
   # Download from python.org and install
   # Make sure to check "Add Python to PATH" during installation
   ```

2. **Install Git** (if copying via Git)
   ```powershell
   # Download from git-scm.com and install
   ```

### 2. Copy Project Files

**Method 1: Using Git**
```powershell
cd C:\inetpub\wwwroot
git clone <your-repo-url> asset-tracker
cd asset-tracker
```

**Method 2: Manual Copy**
- Copy your entire project folder to `C:\inetpub\wwwroot\asset-tracker`
- Exclude: `.git`, `__pycache__`, `.hypothesis`, `*.pyc`, `db.sqlite3`

### 3. Set Up Virtual Environment

```powershell
cd C:\inetpub\wwwroot\asset-tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create `.env` file in project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip,your-server-hostname

# Database (SQLite for testing)
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3

# Session Settings
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Security Settings (Keep False for test server without HTTPS)
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0

# Email Settings (Console backend for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery Settings (Optional for testing)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Generate a Secret Key:**
```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Initialize Database

```powershell
# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin user

# Collect static files
python manage.py collectstatic --noinput
```

### 7. Create Required Directories

```powershell
# Create media directories
New-Item -ItemType Directory -Force -Path "media\asset_attachments"
New-Item -ItemType Directory -Force -Path "media\templates"
```

### 8. Run Test Server

```powershell
# Run on all interfaces so other machines can access
python manage.py runserver 0.0.0.0:8000
```

**Access the application:**
- Local: `http://localhost:8000`
- Network: `http://your-server-ip:8000`

### 9. Configure Windows Firewall

```powershell
# Allow port 8000 through firewall
New-NetFirewallRule -DisplayName "Django Test Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

---

## Option B: Production-like Deployment (IIS + PostgreSQL)

### 1. Install Prerequisites

1. **Install Python 3.11+**
2. **Install PostgreSQL**
   - Download from postgresql.org
   - Note down database credentials

3. **Install IIS**
   ```powershell
   # Open PowerShell as Administrator
   Install-WindowsFeature -name Web-Server -IncludeManagementTools
   ```

4. **Install HttpPlatformHandler** for IIS
   - Download from: https://www.iis.net/downloads/microsoft/httpplatformhandler

5. **Install Redis** (Optional, for Celery)
   - Download from: https://github.com/microsoftarchive/redis/releases

### 2. Set Up PostgreSQL Database

```sql
-- Connect to PostgreSQL as postgres user
CREATE DATABASE asset_tracker;
CREATE USER asset_tracker_user WITH PASSWORD 'your_secure_password';
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;
```

### 3. Configure Environment Variables

Update `.env` file:

```env
# Django Settings
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=your-server-ip,your-domain.com,localhost

# Database (PostgreSQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=asset_tracker
DATABASE_USER=asset_tracker_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Session Settings
SESSION_COOKIE_AGE=86400
SESSION_EXPIRE_AT_BROWSER_CLOSE=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Security Settings
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Install Dependencies & Initialize

```powershell
cd C:\inetpub\wwwroot\asset-tracker
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install waitress  # WSGI server for Windows

python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 5. Create IIS Configuration

Create `web.config` in project root:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="httpPlatformHandler" path="*" verb="*" 
           modules="httpPlatformHandler" resourceType="Unspecified" />
    </handlers>
    <httpPlatform processPath="C:\inetpub\wwwroot\asset-tracker\venv\Scripts\python.exe"
                  arguments="C:\inetpub\wwwroot\asset-tracker\venv\Scripts\waitress-serve.exe --listen=*:8000 asset_tracker.wsgi:application"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\inetpub\wwwroot\asset-tracker\logs\stdout.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="PYTHONUNBUFFERED" value="1" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

### 6. Create Logs Directory

```powershell
New-Item -ItemType Directory -Force -Path "logs"
```

### 7. Configure IIS Site

```powershell
# Import IIS module
Import-Module WebAdministration

# Create application pool
New-WebAppPool -Name "AssetTrackerPool"

# Configure application pool
Set-ItemProperty IIS:\AppPools\AssetTrackerPool -name "managedRuntimeVersion" -value ""

# Create website
New-Website -Name "AssetTracker" `
            -Port 80 `
            -PhysicalPath "C:\inetpub\wwwroot\asset-tracker" `
            -ApplicationPool "AssetTrackerPool"

# Start website
Start-Website -Name "AssetTracker"
```

### 8. Set Permissions

```powershell
# Give IIS_IUSRS permission to project folder
icacls "C:\inetpub\wwwroot\asset-tracker" /grant "IIS_IUSRS:(OI)(CI)F" /T

# Give permission to media folder
icacls "C:\inetpub\wwwroot\asset-tracker\media" /grant "IIS_IUSRS:(OI)(CI)F" /T

# Give permission to logs folder
icacls "C:\inetpub\wwwroot\asset-tracker\logs" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

---

## Post-Deployment Tasks

### 1. Test the Application

- Access admin panel: `http://your-server/admin/`
- Login with superuser credentials
- Test key features:
  - Create an asset
  - Upload an attachment
  - Import Excel file
  - Export data

### 2. Set Up Celery (Optional)

For background tasks (warranty notifications, power monitoring):

**Create `run_celery.bat`:**
```batch
@echo off
cd C:\inetpub\wwwroot\asset-tracker
call venv\Scripts\activate.bat
celery -A asset_tracker worker -l info --pool=solo
```

**Create `run_celery_beat.bat`:**
```batch
@echo off
cd C:\inetpub\wwwroot\asset-tracker
call venv\Scripts\activate.bat
celery -A asset_tracker beat -l info
```

**Run as Windows Service** (using NSSM):
```powershell
# Download NSSM from nssm.cc
nssm install CeleryWorker "C:\inetpub\wwwroot\asset-tracker\run_celery.bat"
nssm install CeleryBeat "C:\inetpub\wwwroot\asset-tracker\run_celery_beat.bat"

nssm start CeleryWorker
nssm start CeleryBeat
```

### 3. Set Up Backup

**Create `backup_database.ps1`:**
```powershell
$backupDir = "C:\Backups\AssetTracker"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDir

# For SQLite
Copy-Item "C:\inetpub\wwwroot\asset-tracker\db.sqlite3" `
          "$backupDir\db_backup_$timestamp.sqlite3"

# For PostgreSQL
# pg_dump -U asset_tracker_user -d asset_tracker > "$backupDir\db_backup_$timestamp.sql"

# Backup media files
Compress-Archive -Path "C:\inetpub\wwwroot\asset-tracker\media" `
                 -DestinationPath "$backupDir\media_backup_$timestamp.zip"

Write-Host "Backup completed: $timestamp"
```

**Schedule with Task Scheduler:**
```powershell
$action = New-ScheduledTaskAction -Execute 'Powershell.exe' `
  -Argument '-File "C:\inetpub\wwwroot\asset-tracker\backup_database.ps1"'

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask -Action $action -Trigger $trigger `
  -TaskName "AssetTracker Backup" -Description "Daily backup of Asset Tracker"
```

---

## Troubleshooting

### Issue: Can't access from other machines
**Solution:**
```powershell
# Check firewall
Get-NetFirewallRule | Where-Object DisplayName -like "*Django*"

# Add rule if missing
New-NetFirewallRule -DisplayName "Django/IIS" -Direction Inbound -LocalPort 8000,80 -Protocol TCP -Action Allow
```

### Issue: Static files not loading
**Solution:**
```powershell
python manage.py collectstatic --noinput
# Verify STATIC_ROOT in settings.py
```

### Issue: Database connection errors
**Solution:**
- Check PostgreSQL service is running
- Verify credentials in `.env`
- Test connection: `psql -U asset_tracker_user -d asset_tracker`

### Issue: Permission denied errors
**Solution:**
```powershell
# Reset permissions
icacls "C:\inetpub\wwwroot\asset-tracker" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

---

## Security Checklist for Test Server

- [ ] Changed SECRET_KEY from default
- [ ] Set DEBUG=False in production-like environment
- [ ] Configured ALLOWED_HOSTS properly
- [ ] Set strong database password
- [ ] Created admin user with strong password
- [ ] Configured firewall rules
- [ ] Set up regular backups
- [ ] Reviewed file permissions
- [ ] Tested all critical features

---

## Monitoring & Maintenance

### Check Logs
```powershell
# IIS logs
Get-Content "C:\inetpub\wwwroot\asset-tracker\logs\stdout.log" -Tail 50

# Django logs
Get-Content "C:\inetpub\wwwroot\asset-tracker\authentication.log" -Tail 50
```

### Update Application
```powershell
cd C:\inetpub\wwwroot\asset-tracker

# Backup first!
.\backup_database.ps1

# Pull changes (if using Git)
git pull

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Update dependencies
pip install -r requirements.txt --upgrade

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Restart IIS site
Restart-WebAppPool -Name "AssetTrackerPool"
```

---

## Support

For issues or questions:
1. Check logs in `logs\stdout.log`
2. Check Django logs in `authentication.log`
3. Review error messages in browser developer console
4. Check Windows Event Viewer for system-level errors

