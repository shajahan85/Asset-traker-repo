# Asset Tracker - Quick Start Guide for IIS Deployment

This is a condensed guide for experienced administrators. For detailed instructions, see `IIS_DEPLOYMENT_GUIDE.md`.

## Prerequisites Installation (Run as Administrator)

```powershell
# Install IIS with CGI
Install-WindowsFeature -name Web-Server,Web-CGI -IncludeManagementTools

# Install URL Rewrite (download from https://www.iis.net/downloads/microsoft/url-rewrite)
# Or use Chocolatey:
choco install urlrewrite redis-64 -y

# Start Redis
redis-server --service-start
```

## Application Deployment

```powershell
# 1. Copy application files
Copy-Item -Path "D:\Asset tracker\*" -Destination "C:\inetpub\wwwroot\AssetTracker" -Recurse -Force

# 2. Navigate to application
cd C:\inetpub\wwwroot\AssetTracker

# 3. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 4. Install packages
pip install --upgrade pip
pip install -r requirements.txt
pip install wfastcgi

# 5. Enable wfastcgi (SAVE THE OUTPUT PATH!)
wfastcgi-enable
# Example output: C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe|C:\inetpub\wwwroot\AssetTracker\venv\Lib\site-packages\wfastcgi.py

# 6. Configure environment
Copy-Item "hosting_requirements\.env.production" -Destination ".env"
# Edit .env with your settings (SECRET_KEY, database, etc.)

# 7. Setup database (PostgreSQL example)
# psql -U postgres
# CREATE DATABASE asset_tracker;
# CREATE USER asset_tracker_user WITH PASSWORD 'YourPassword';
# GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;

# 8. Run Django setup
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

# 9. Set permissions
icacls "C:\inetpub\wwwroot\AssetTracker" /grant "IIS_IUSRS:(OI)(CI)F" /T
```

## IIS Configuration

```powershell
# 1. Create Application Pool
New-WebAppPool -Name "AssetTrackerPool"
Set-ItemProperty "IIS:\AppPools\AssetTrackerPool" -Name "managedRuntimeVersion" -Value ""
Set-ItemProperty "IIS:\AppPools\AssetTrackerPool" -Name "startMode" -Value "AlwaysRunning"

# 2. Create Website
New-Website -Name "AssetTracker" -PhysicalPath "C:\inetpub\wwwroot\AssetTracker" -ApplicationPool "AssetTrackerPool" -Port 80

# 3. Copy web.config
Copy-Item "hosting_requirements\web.config" -Destination "C:\inetpub\wwwroot\AssetTracker\web.config"

# 4. Edit web.config
# Update the scriptProcessor path with output from wfastcgi-enable

# 5. Restart IIS
iisreset /restart
```

## Test

Open browser: `http://localhost/`

## Celery Services (Optional but Recommended)

```powershell
# Install NSSM
choco install nssm -y

# Create Celery Worker Service
nssm install AssetTrackerCelery "C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe"
nssm set AssetTrackerCelery AppDirectory "C:\inetpub\wwwroot\AssetTracker"
nssm set AssetTrackerCelery AppParameters "-m celery -A asset_tracker worker -l info"
nssm start AssetTrackerCelery

# Create Celery Beat Service
nssm install AssetTrackerCeleryBeat "C:\inetpub\wwwroot\AssetTracker\venv\Scripts\python.exe"
nssm set AssetTrackerCeleryBeat AppDirectory "C:\inetpub\wwwroot\AssetTracker"
nssm set AssetTrackerCeleryBeat AppParameters "-m celery -A asset_tracker beat -l info"
nssm start AssetTrackerCeleryBeat
```

## Troubleshooting

### HTTP 500 Error
```powershell
# Check IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" | Select-Object -Last 50

# Enable detailed errors (temporarily)
# Set DEBUG=True in .env, restart IIS, then set back to False
```

### Static Files Not Loading
```powershell
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1
python manage.py collectstatic --noinput
iisreset /restart
```

### Database Connection Error
- Verify database credentials in `.env`
- Test database connection
- Check firewall rules

## Security Checklist

- [ ] DEBUG=False in .env
- [ ] Strong SECRET_KEY generated
- [ ] ALLOWED_HOSTS configured
- [ ] Strong database password
- [ ] .env file permissions restricted
- [ ] SSL certificate installed (for HTTPS)
- [ ] Firewall configured
- [ ] Regular backups scheduled

## Next Steps

1. Configure SSL/HTTPS (highly recommended)
2. Set up automated backups (see `backup_database.ps1`)
3. Configure monitoring and alerts
4. Review security settings
5. Set up regular maintenance schedule

## Quick Reference

- **Application Path**: `C:\inetpub\wwwroot\AssetTracker`
- **IIS Manager**: Run `inetmgr`
- **Restart IIS**: `iisreset /restart`
- **View Logs**: `C:\inetpub\logs\LogFiles\`
- **Activate Venv**: `.\venv\Scripts\Activate.ps1`
- **Run Migrations**: `python manage.py migrate`
- **Collect Static**: `python manage.py collectstatic --noinput`

For detailed instructions, see `IIS_DEPLOYMENT_GUIDE.md`
