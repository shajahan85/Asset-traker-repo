# 🎯 Visual Guide: Django on IIS - Configuration Editor

## Step 1: Open IIS Manager Configuration Editor

1. Open **IIS Manager**
2. Select your site: **"Assettracker"**
3. Double-click **"Configuration Editor"**

---

## Step 2: Navigate to FastCGI Settings

In Configuration Editor:
- **Section dropdown:** Select `system.webServer/fastCgi`
- You should see a screen like your screenshot

---

## Step 3: Find Your Python Application

Look for the tree structure on the left:

```
system.webServer/fastCgi
└── (Collection) ← Click here to expand
    └── application ← Find your Python entry
        ├── fullPath: "E:\Asset-tracker tool\venv\Scripts\python.exe"
        ├── arguments: "E:\Asset-tracker tool\venv\Lib\site-packages\wfastcgi.py"
        ├── maxInstances: 4
        ├── idleTimeout: 1800
        └── environmentVariables (Collection) ← THIS IS WHERE YOU ADD VARIABLES
```

---

## Step 4: Add Environment Variables

### Method A: Using Configuration Editor (Your Current Screen)

1. **Navigate to the application entry:**
   - Click on `(Collection)` under `system.webServer/fastCgi`
   - Find the entry with your Python path
   - Click to expand it

2. **Find `environmentVariables`:**
   - Scroll down in the properties
   - Click on `environmentVariables (Collection)`
   - It should show `(Count=0)` or existing variables

3. **Click "Add" in Actions panel (right side)**

4. **Add these 3 variables one by one:**

   | Name | Value |
   |------|-------|
   | `PYTHONPATH` | `E:\Asset-tracker tool` |
   | `DJANGO_SETTINGS_MODULE` | `asset_tracker.settings` |
   | `WSGI_HANDLER` | `asset_tracker.wsgi.application` |

5. **Click "Apply"** in Actions panel

### Method B: Using PowerShell (Easier Alternative)

Run this in PowerShell as Administrator:

```powershell
# Set FastCGI environment variables
$configPath = "MACHINE/WEBROOT/APPHOST"
$filter = "system.webServer/fastCgi/application[@fullPath='E:\Asset-tracker tool\venv\Scripts\python.exe']"

# Add PYTHONPATH
C:\Windows\system32\inetsrv\appcmd.exe set config "$configPath" /section:system.webServer/fastCgi /+"[$filter]/environmentVariables.[name='PYTHONPATH',value='E:\Asset-tracker tool']"

# Add DJANGO_SETTINGS_MODULE  
C:\Windows\system32\inetsrv\appcmd.exe set config "$configPath" /section:system.webServer/fastCgi /+"[$filter]/environmentVariables.[name='DJANGO_SETTINGS_MODULE',value='asset_tracker.settings']"

# Add WSGI_HANDLER
C:\Windows\system32\inetsrv\appcmd.exe set config "$configPath" /section:system.webServer/fastCgi /+"[$filter]/environmentVariables.[name='WSGI_HANDLER',value='asset_tracker.wsgi.application']"
```

---

## Step 5: Verify web.config Location

Your `web.config` file should be at:
```
E:\Asset-tracker tool\web.config
```

**Important:** The web.config file must be in the **physical path** of your IIS site, not in a subdirectory.

To verify in IIS Manager:
1. Right-click "Assettracker" site
2. Select "Manage Website" → "Advanced Settings"
3. Check "Physical Path" → Should be `E:\Asset-tracker tool`
4. Confirm `web.config` exists in that folder

---

## Step 6: Configure Handler Mapping

1. In IIS Manager, select "Assettracker" site
2. Double-click **"Handler Mappings"**
3. Look for **"Python FastCGI"** or **"Django FastCGI"**

If it doesn't exist:
1. Click "Add Module Mapping"
2. Fill in:
   - **Request path:** `*`
   - **Module:** `FastCgiModule`
   - **Executable:** `"E:\Asset-tracker tool\venv\Scripts\python.exe"|"E:\Asset-tracker tool\venv\Lib\site-packages\wfastcgi.py"`
   - **Name:** `Django FastCGI`
3. Click OK

---

## Step 7: Set Permissions

Run in PowerShell as Administrator:

```powershell
# Grant IIS users access to the project folder
icacls "E:\Asset-tracker tool" /grant "IIS_IUSRS:(OI)(CI)F" /T
icacls "E:\Asset-tracker tool" /grant "IUSR:(OI)(CI)F" /T

# Grant access to database (if using SQLite)
icacls "E:\Asset-tracker tool\db.sqlite3" /grant "IIS_IUSRS:F"
```

---

## Step 8: Restart IIS and Start Site

```powershell
# Restart IIS
iisreset /restart

# Start your site
Start-WebSite -Name "Assettracker"

# Check status
Get-WebSite -Name "Assettracker"

# Open browser
Start-Process "http://192.168.10.29:8082/"
```

---

## 🔍 Troubleshooting Commands

### Check if port is free:
```powershell
netstat -ano | Select-String ":8082"
```
- **No output** = Port is free ✅
- **Shows output** = Port is in use ❌

### Check IIS Application Pool status:
```powershell
Get-WebAppPoolState -Name "Assettracker"
```

### View IIS logs:
```powershell
Get-Content "C:\inetpub\logs\LogFiles\W3SVC*\*.log" -Tail 50
```

### Test Django directly (bypass IIS):
```powershell
cd "E:\Asset-tracker tool"
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8082
```

---

## 📚 Additional Resources

1. **Medium Tutorial:** https://medium.com/@ayushi21095/steps-to-deploy-python-django-web-application-on-windows-iis-server-379b2b87fcf9
2. **Another Guide:** https://medium.com/@Jonny_Waffles/deploy-django-on-iis-def658beae92
3. **GitHub Example:** https://github.com/dancar97/Django-Simple-Deploy--IIS

---

## ❓ Common Issues

### Issue 1: "Cannot add duplicate collection entry"
**Solution:** FastCGI is already configured. Skip `wfastcgi-enable` and just configure environment variables.

### Issue 2: HTTP 500 Error
**Solution:** 
- Check IIS logs
- Verify Python path is correct
- Ensure DJANGO_SETTINGS_MODULE is correct
- Check file permissions

### Issue 3: Port already in use
**Solution:**
```powershell
# Find process using the port
netstat -ano | Select-String ":8082"
# Stop it (replace PID with actual process ID)
Stop-Process -Id <PID> -Force
```

### Issue 4: Site won't start
**Solution:**
- Check Application Pool is running
- Verify web.config syntax
- Check Windows Event Viewer for errors

---

## ✅ Success Checklist

- [ ] Python virtual environment created at `E:\Asset-tracker tool\venv`
- [ ] wfastcgi installed: `pip install wfastcgi`
- [ ] web.config exists at `E:\Asset-tracker tool\web.config`
- [ ] FastCGI configured in IIS with environment variables
- [ ] Handler mapping added for `*` path
- [ ] Permissions granted to IIS_IUSRS and IUSR
- [ ] Port 8082 is free
- [ ] IIS restarted: `iisreset /restart`
- [ ] Site started: `Start-WebSite -Name "Assettracker"`
- [ ] Site accessible at http://192.168.10.29:8082/

---

**Last Updated:** August 2026
