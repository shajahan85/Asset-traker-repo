# Asset Tracker - Troubleshooting Guide

Common issues and their solutions when deploying Django on IIS.

---

## Table of Contents

1. [HTTP Error Codes](#http-error-codes)
2. [Database Issues](#database-issues)
3. [Static Files Issues](#static-files-issues)
4. [Permission Issues](#permission-issues)
5. [Celery Issues](#celery-issues)
6. [Performance Issues](#performance-issues)
7. [Email Issues](#email-issues)
8. [Common Error Messages](#common-error-messages)

---

## HTTP Error Codes

### HTTP 500 - Internal Server Error

**Symptoms**: White page with "500 - Internal Server Error"

**Causes & Solutions**:

1. **Incorrect web.config**
   ```powershell
   # Verify web.config exists
   Test-Path "C:\inetpub\wwwroot\AssetTracker\web.config"
   
   # Check for syntax errors
   # Ensure all paths are correct (scriptProcessor, PYTHONPATH)
   ```

2. **Wrong wfastcgi path**
   ```powershell
   # Re-run wfastcgi-enable and copy the exact output
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   wfastcgi-enable
   
   # Update the path in web.config
   ```

3. **Django error - Enable DEBUG temporarily**
   ```ini
   # In .env file
   DEBUG=True
   
   # Restart IIS
   iisreset /restart
   
   # IMPORTANT: Set DEBUG=False after troubleshooting
   ```

4. **Check IIS Logs**
   ```powershell
   # View recent IIS logs
   Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" | Select-Object -Last 100
   
   # Look for specific error codes
   ```

5. **Check Django/Application Logs**
   ```powershell
   Get-Content "C:\inetpub\wwwroot\AssetTracker\authentication.log" -Tail 50
   ```

### HTTP 404 - Not Found

**Symptoms**: "Page not found" error

**Solutions**:

1. **URL Rewrite Module missing**
   ```powershell
   # Install URL Rewrite Module
   choco install urlrewrite -y
   # Or download from: https://www.iis.net/downloads/microsoft/url-rewrite
   ```

2. **Check URL patterns in Django**
   ```powershell
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   python manage.py show_urls  # If django-extensions installed
   ```

3. **Verify web.config rewrite rules**
   - Ensure rewrite rules are present in web.config

### HTTP 403 - Forbidden

**Symptoms**: "You do not have permission to view this directory or page"

**Solutions**:

1. **Directory browsing disabled** (This is normal for Django apps)

2. **Incorrect permissions**
   ```powershell
   # Grant IIS_IUSRS full control
   icacls "C:\inetpub\wwwroot\AssetTracker" /grant "IIS_IUSRS:(OI)(CI)F" /T
   ```

3. **Check ALLOWED_HOSTS in .env**
   ```ini
   ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip,yourdomain.com
   ```

### HTTP 502 - Bad Gateway

**Symptoms**: "502 - Web server received an invalid response"

**Solutions**:

1. **FastCGI process crashed**
   ```powershell
   # Restart IIS
   iisreset /restart
   
   # Check FastCGI settings in web.config
   ```

2. **Python process not starting**
   ```powershell
   # Test Python executable
   C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe --version
   
   # Verify wfastcgi installation
   C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe -m wfastcgi
   ```

---

## Database Issues

### Cannot connect to database

**Symptoms**: "OperationalError: could not connect to server"

**Solutions**:

1. **PostgreSQL not running**
   ```powershell
   # Check PostgreSQL service
   Get-Service -Name postgresql*
   
   # Start service if stopped
   Start-Service postgresql-x64-15  # Adjust version number
   ```

2. **Incorrect credentials**
   ```ini
   # Verify in .env file
   DATABASE_USER=asset_tracker_user
   DATABASE_PASSWORD=YourPassword
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   ```

3. **Test database connection**
   ```powershell
   # Test with psql
   psql -h localhost -U asset_tracker_user -d asset_tracker
   ```

4. **Firewall blocking connection**
   ```powershell
   # Allow PostgreSQL through firewall
   New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow
   ```

### Migration errors

**Symptoms**: "django.db.utils.ProgrammingError"

**Solutions**:

```powershell
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1

# Reset migrations (CAUTION: Development only)
python manage.py migrate --fake-initial

# Or rollback and re-apply
python manage.py migrate app_name zero
python manage.py migrate app_name

# For corrupted migrations
# Delete migration files (keep __init__.py)
# Run makemigrations and migrate again
```

---

## Static Files Issues

### CSS/JS not loading

**Symptoms**: Plain HTML pages without styling

**Solutions**:

1. **Static files not collected**
   ```powershell
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   python manage.py collectstatic --noinput
   ```

2. **Incorrect STATIC_URL or STATIC_ROOT**
   ```python
   # In settings.py
   STATIC_URL = '/static/'
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ```

3. **IIS not serving static files**
   ```powershell
   # Check staticfiles folder permissions
   icacls "C:\inetpub\wwwroot\AssetTracker\staticfiles" /grant "IIS_IUSRS:(OI)(CI)R" /T
   ```

4. **Check web.config static file rules**
   - Verify static file rewrite rule is present
   - Ensure static content MIME types are configured

5. **Clear browser cache**
   - Hard refresh: Ctrl + Shift + R
   - Or open in incognito/private mode

### File upload errors

**Symptoms**: "PermissionError: [Errno 13] Permission denied"

**Solutions**:

```powershell
# Grant write permissions to media folder
icacls "C:\inetpub\wwwroot\AssetTracker\media" /grant "IIS_IUSRS:(OI)(CI)F" /T

# Verify MEDIA_ROOT in settings.py
```

---

## Permission Issues

### Permission denied errors

**Symptoms**: "PermissionError" or "Access is denied"

**Solutions**:

1. **Grant IIS_IUSRS permissions**
   ```powershell
   # Full control to application folder
   icacls "C:\inetpub\wwwroot\AssetTracker" /grant "IIS_IUSRS:(OI)(CI)F" /T
   
   # Specific folders
   icacls "C:\inetpub\wwwroot\AssetTracker\media" /grant "IIS_IUSRS:(OI)(CI)F" /T
   icacls "C:\inetpub\wwwroot\AssetTracker\staticfiles" /grant "IIS_IUSRS:(OI)(CI)F" /T
   ```

2. **SQLite database permissions** (if using SQLite)
   ```powershell
   icacls "C:\inetpub\wwwroot\AssetTracker\db.sqlite3" /grant "IIS_IUSRS:F"
   icacls "C:\inetpub\wwwroot\AssetTracker" /grant "IIS_IUSRS:(OI)(CI)F"
   ```

3. **Application Pool Identity**
   - Verify Application Pool is running under correct identity
   - In IIS Manager → Application Pools → AssetTrackerPool → Advanced Settings → Identity

---

## Celery Issues

### Celery worker not starting

**Symptoms**: Tasks not executing, no background processing

**Solutions**:

1. **Check Redis is running**
   ```powershell
   # Test Redis connection
   redis-cli ping
   # Expected output: PONG
   
   # If not running
   redis-server --service-start
   ```

2. **Check Celery service status**
   ```powershell
   # Check service status
   nssm status AssetTrackerCelery
   
   # View service logs
   Get-EventLog -LogName Application -Source AssetTrackerCelery -Newest 20
   ```

3. **Start Celery manually for debugging**
   ```powershell
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   celery -A asset_tracker worker -l debug
   ```

4. **Verify Celery configuration in .env**
   ```ini
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

### Tasks not executing

**Solutions**:

1. **Check Celery Beat is running**
   ```powershell
   nssm status AssetTrackerCeleryBeat
   nssm start AssetTrackerCeleryBeat
   ```

2. **Verify task registration**
   ```powershell
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   celery -A asset_tracker inspect registered
   ```

3. **Check task schedule in settings.py**
   - Verify CELERY_BEAT_SCHEDULE is configured correctly

---

## Performance Issues

### Slow response times

**Solutions**:

1. **Increase FastCGI maxInstances**
   ```xml
   <!-- In web.config -->
   <application ... maxInstances="8">
   ```

2. **Enable Redis cache**
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **Database query optimization**
   ```powershell
   # Enable query logging temporarily
   # Check for N+1 queries
   # Add select_related() and prefetch_related() where needed
   ```

4. **Enable Application Pool preloading**
   - IIS Manager → Application Pools → AssetTrackerPool
   - Advanced Settings → Start Mode → AlwaysRunning

### High memory usage

**Solutions**:

1. **Reduce maxInstances in web.config**
2. **Implement pagination for large querysets**
3. **Monitor with Task Manager or Performance Monitor**
4. **Check for memory leaks in custom code**

---

## Email Issues

### Emails not sending

**Symptoms**: No error but emails don't arrive

**Solutions**:

1. **Check email configuration in .env**
   ```ini
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

2. **Test email manually**
   ```powershell
   cd C:\inetpub\wwwroot\AssetTracker
   .\venv\Scripts\Activate.ps1
   python manage.py shell
   ```
   ```python
   from django.core.mail import send_mail
   send_mail(
       'Test Subject',
       'Test message',
       'from@example.com',
       ['to@example.com'],
       fail_silently=False,
   )
   ```

3. **For Gmail, use App Password**
   - Enable 2FA on Google account
   - Generate App Password
   - Use App Password instead of regular password

4. **Check firewall allows outbound SMTP**
   ```powershell
   Test-NetConnection -ComputerName smtp.gmail.com -Port 587
   ```

---

## Common Error Messages

### "ImproperlyConfigured: The SECRET_KEY setting must not be empty"

**Solution**:
```ini
# In .env file, generate and set SECRET_KEY
SECRET_KEY=your-secret-key-here
```

```powershell
# Generate new SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### "DisallowedHost at / Invalid HTTP_HOST header"

**Solution**:
```ini
# Add your domain/IP to ALLOWED_HOSTS in .env
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip,yourdomain.com
```

### "OperationalError: unable to open database file"

**Solution**:
```powershell
# Grant write permissions to database and parent folder
icacls "C:\inetpub\wwwroot\AssetTracker\db.sqlite3" /grant "IIS_IUSRS:F"
icacls "C:\inetpub\wwwroot\AssetTracker" /grant "IIS_IUSRS:(OI)(CI)M"
```

### "ModuleNotFoundError: No module named 'wfastcgi'"

**Solution**:
```powershell
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1
pip install wfastcgi
wfastcgi-enable
# Update web.config with new path
```

---

## Debugging Tips

### Enable Detailed Error Messages

1. **Temporarily enable DEBUG**
   ```ini
   # In .env
   DEBUG=True
   ```

2. **Configure detailed errors in web.config**
   ```xml
   <httpErrors errorMode="Detailed" existingResponse="PassThrough" />
   ```

3. **Check all log files**
   ```powershell
   # IIS Logs
   Get-ChildItem "C:\inetpub\logs\LogFiles\" -Recurse | Get-Content -Tail 50
   
   # Application Logs
   Get-Content "C:\inetpub\wwwroot\AssetTracker\authentication.log" -Tail 50
   
   # Windows Event Log
   Get-EventLog -LogName Application -Newest 50
   ```

### Testing Components Individually

```powershell
# Test Python
python --version

# Test Django
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1
python manage.py check

# Test database connection
python manage.py dbshell

# Test static files
python manage.py collectstatic --noinput --dry-run

# Test with Django development server
python manage.py runserver 0.0.0.0:8000
```

---

## Getting Help

If you're still experiencing issues after trying these solutions:

1. Check Django documentation: https://docs.djangoproject.com/
2. Check IIS documentation: https://docs.microsoft.com/en-us/iis/
3. Review wfastcgi documentation: https://pypi.org/project/wfastcgi/
4. Search for specific error messages
5. Check Django community forums
6. Review GitHub issues for related packages

---

## Emergency Recovery

### Complete Reset (Last Resort)

```powershell
# Stop IIS
iisreset /stop

# Backup current state
Copy-Item "C:\inetpub\wwwroot\AssetTracker" "C:\AssetTracker_Backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')" -Recurse

# Remove and recreate
Remove-Website -Name "AssetTracker"
Remove-WebAppPool -Name "AssetTrackerPool"

# Follow Quick Start Guide to redeploy
# See QUICK_START.md
```

---

**Keep this guide handy during deployment and maintenance!**
