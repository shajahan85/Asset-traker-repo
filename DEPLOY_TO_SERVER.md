# Deploy Asset Tracker to 192.168.10.29:8081

## Server Details
- **IP Address**: 192.168.10.29
- **Port**: 8081
- **Location**: E:\Asset-tracker tool
- **Current Dev Location**: D:\Asset tracker

---

## Quick Deployment Steps

### Step 1: Copy Files to Server

On your server (192.168.10.29), create the folder and copy files:

```powershell
# Create folder
New-Item -ItemType Directory -Path "E:\Asset-tracker tool" -Force

# Copy all files from development (on your local machine)
# Option A: Use network share
Copy-Item "D:\Asset tracker\*" -Destination "\\192.168.10.29\E$\Asset-tracker tool\" -Recurse -Exclude "venv","__pycache__",".git","*.pyc"

# Option B: Use RDP and copy manually
# Copy entire "D:\Asset tracker" folder to "E:\Asset-tracker tool" on server
```

### Step 2: On the Server - Install Python Packages

Open PowerShell as Administrator on server (192.168.10.29):

```powershell
# Navigate to project
cd "E:\Asset-tracker tool"

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# Install wfastcgi for IIS
pip install wfastcgi

# Enable wfastcgi
wfastcgi-enable

# IMPORTANT: Copy the output! It looks like:
# E:\Asset-tracker tool\venv\Scripts\python.exe|E:\Asset-tracker tool\venv\Lib\site-packages\wfastcgi.py
```

### Step 3: Configure Environment

```powershell
# Copy .env.example to .env
Copy-Item ".env.example" -Destination ".env"

# Edit .env file and update:
notepad .env

# Update these values:
# DEBUG=False
# ALLOWED_HOSTS=192.168.10.29,localhost,127.0.0.1
# SECRET_KEY=generate-a-new-secret-key-here
# Database settings (if using PostgreSQL/SQL Server)
```

### Step 4: Run Django Setup

```powershell
# Still in E:\Asset-tracker tool with venv activated

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
```

### Step 5: Set Folder Permissions

```powershell
# Grant IIS permissions
icacls "E:\Asset-tracker tool" /grant "IIS_IUSRS:(OI)(CI)F" /T

# Grant permissions to specific folders
icacls "E:\Asset-tracker tool\media" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "E:\Asset-tracker tool\staticfiles" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

### Step 6: Configure IIS

1. **Open IIS Manager** (`inetmgr`)

2. **Create Application Pool:**
   - Right-click **Application Pools** → **Add Application Pool**
   - Name: `AssetTrackerPool`
   - .NET CLR Version: `No Managed Code`
   - Managed Pipeline Mode: `Integrated`
   - Click **OK**

3. **Configure Application Pool:**
   - Right-click `AssetTrackerPool` → **Advanced Settings**
   - Set **Start Mode**: `AlwaysRunning`
   - Set **Idle Time-out (minutes)**: `0`
   - Click **OK**

4. **Create Website:**
   - Right-click **Sites** → **Add Website**
   - Site name: `AssetTracker`
   - Application pool: `AssetTrackerPool`
   - Physical path: `E:\Asset-tracker tool`
   - Binding:
     - Type: `http`
     - IP address: `192.168.10.29` (or All Unassigned)
     - Port: `8081`
   - Click **OK**

5. **Add Handler Mapping:**
   - Select `AssetTracker` site
   - Double-click **Handler Mappings**
   - Click **Add Module Mapping** (right panel)
   - **Request path**: `*`
   - **Module**: `FastCgiModule`
   - **Executable**: Paste the path from wfastcgi-enable output
     ```
     E:\Asset-tracker tool\venv\Scripts\python.exe|E:\Asset-tracker tool\venv\Lib\site-packages\wfastcgi.py
     ```
   - **Name**: `Django Handler`
   - Click **Request Restrictions**
   - **Uncheck**: "Invoke handler only if request is mapped to:"
   - Click **OK** → **Yes**

### Step 7: Verify web.config

The web.config file should already be in `E:\Asset-tracker tool\web.config` with correct paths.

Verify these paths match:
- `E:\Asset-tracker tool\venv\Scripts\python.exe`
- `E:\Asset-tracker tool\venv\Lib\site-packages\wfastcgi.py`
- `E:\Asset-tracker tool` for PYTHONPATH

### Step 8: Restart IIS and Test

```powershell
# Restart IIS
iisreset /restart

# Test the site
Start-Process "http://192.168.10.29:8081/"
```

---

## Troubleshooting

### Issue: HTTP 500 Error

**Solution 1 - Check IIS Logs:**
```powershell
Get-Content "C:\inetpub\logs\LogFiles\W3SVC*\*.log" | Select-Object -Last 50
```

**Solution 2 - Enable Detailed Errors:**
Edit web.config and check:
```xml
<httpErrors errorMode="Detailed" />
```

**Solution 3 - Check FastCGI Configuration:**
Open IIS Manager → Server → FastCGI Settings
Verify the Python path exists

### Issue: Static Files Not Loading

```powershell
cd "E:\Asset-tracker tool"
.\venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput
iisreset /restart
```

### Issue: Permission Errors

```powershell
icacls "E:\Asset-tracker tool" /grant "IIS_IUSRS:(OI)(CI)F" /T
iisreset /restart
```

---

## Quick Commands Reference

```powershell
# On Server: E:\Asset-tracker tool

# Activate venv
.\venv\Scripts\Activate.ps1

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Check for errors
python manage.py check

# Restart IIS
iisreset /restart

# View logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC*\*.log" | Select-Object -Last 50
```

---

## Important Files Checklist

Before starting, ensure these files exist in `E:\Asset-tracker tool`:

- ✅ web.config (with correct paths)
- ✅ .env (configured with production settings)
- ✅ requirements.txt
- ✅ manage.py
- ✅ asset_tracker/settings.py
- ✅ asset_tracker/wsgi.py

---

## After Deployment

1. Access: http://192.168.10.29:8081/
2. Login to admin: http://192.168.10.29:8081/admin/
3. Test all functionality
4. Check logs for errors

---

## Optional: Install Redis (for background tasks)

If you want automatic warranty checks and power monitoring:

```powershell
# Download Redis for Windows
# https://github.com/tporadowski/redis/releases
# Install Redis-x64-5.0.14.1.msi

# Start Redis service
redis-server --service-start

# Test Redis
redis-cli ping
# Should return: PONG
```

Then configure Celery services (see IIS_DEPLOYMENT_GUIDE.md)

---

**Need help? Check:**
- `hosting_requirements\IIS_DEPLOYMENT_GUIDE.md` - Full detailed guide
- `hosting_requirements\TROUBLESHOOTING.md` - Common issues
- `hosting_requirements\DEPLOYMENT_CHECKLIST.md` - Complete checklist
