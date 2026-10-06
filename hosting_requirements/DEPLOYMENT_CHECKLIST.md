# Asset Tracker - IIS Deployment Checklist

Use this checklist to ensure all deployment steps are completed correctly.

## Pre-Deployment

### Software Installation
- [ ] Windows Server 2016 or later installed
- [ ] IIS 10.0+ installed with CGI module
- [ ] Python 3.9+ (64-bit) installed and added to PATH
- [ ] Microsoft Visual C++ Redistributable installed
- [ ] URL Rewrite Module for IIS installed
- [ ] Redis Server installed and running
- [ ] PostgreSQL or SQL Server installed (if using)
- [ ] Git installed (optional, for updates)

### Server Configuration
- [ ] Static IP address or domain name configured
- [ ] Firewall rules configured (ports 80, 443, 5432/1433)
- [ ] Windows updates installed
- [ ] Antivirus exclusions for application folder configured

## Application Setup

### File Preparation
- [ ] Application files copied to `C:\inetpub\wwwroot\AssetTracker`
- [ ] Unnecessary files removed (.git, __pycache__, *.pyc)
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Virtual environment activated
- [ ] pip upgraded (`python -m pip install --upgrade pip`)
- [ ] Requirements installed (`pip install -r requirements.txt`)
- [ ] wfastcgi installed (`pip install wfastcgi`)
- [ ] wfastcgi enabled (`wfastcgi-enable`) and path copied

### Configuration Files
- [ ] `.env.production` copied to `.env`
- [ ] `.env` file updated with actual values:
  - [ ] SECRET_KEY generated and set
  - [ ] DEBUG set to False
  - [ ] ALLOWED_HOSTS updated with server IP/domain
  - [ ] Database credentials configured
  - [ ] Email settings configured
  - [ ] Redis URL configured
- [ ] `web.config` copied to application root
- [ ] `web.config` updated with correct paths:
  - [ ] scriptProcessor path updated
  - [ ] PYTHONPATH updated
  - [ ] Application path in fastCgi section updated

### Database Setup
- [ ] Database created (PostgreSQL/SQL Server/SQLite)
- [ ] Database user created with appropriate permissions
- [ ] Database connection tested
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Test data loaded (if needed)

### Static Files
- [ ] Static files collected (`python manage.py collectstatic --noinput`)
- [ ] Static files directory created (`C:\inetpub\wwwroot\AssetTracker\staticfiles`)
- [ ] Media files directory created (`C:\inetpub\wwwroot\AssetTracker\media`)

### Permissions
- [ ] IIS_IUSRS granted full control to application folder
- [ ] Permissions set on media folder
- [ ] Permissions set on staticfiles folder
- [ ] Permissions set on database file (if SQLite)
- [ ] Permissions set on logs folder

## IIS Configuration

### Application Pool
- [ ] Application Pool created (`AssetTrackerPool`)
- [ ] .NET CLR Version set to "No Managed Code"
- [ ] Managed Pipeline Mode set to "Integrated"
- [ ] Identity configured
- [ ] Start Mode set to "AlwaysRunning"
- [ ] Idle Time-out set to 0 (disabled)

### Website
- [ ] Website created (`AssetTracker`)
- [ ] Physical path set to `C:\inetpub\wwwroot\AssetTracker`
- [ ] Application Pool assigned (`AssetTrackerPool`)
- [ ] Binding configured (HTTP port 80 or custom)
- [ ] Host name set (if using domain)

### Handler Mapping
- [ ] FastCGI Handler added
- [ ] Request path set to `*`
- [ ] Module set to `FastCgiModule`
- [ ] Executable path set (from wfastcgi-enable output)
- [ ] Request Restrictions: "Invoke handler only if request is mapped to" unchecked

### FastCGI Settings
- [ ] FastCGI application configured in web.config
- [ ] Environment variables set:
  - [ ] DJANGO_SETTINGS_MODULE
  - [ ] PYTHONPATH
  - [ ] WSGI_HANDLER
  - [ ] WSGI_LOG (optional)

## Testing

### Basic Tests
- [ ] IIS restarted (`iisreset /restart`)
- [ ] Website accessible via browser (http://server-ip/)
- [ ] Admin panel accessible (/admin/)
- [ ] Login functionality tested
- [ ] Static files loading correctly (CSS, JS, images)
- [ ] Media files uploading and displaying correctly

### Functionality Tests
- [ ] Create new asset tested
- [ ] Edit asset tested
- [ ] Delete/Free asset tested
- [ ] File upload tested
- [ ] Excel export tested
- [ ] Email notifications tested (if configured)
- [ ] Search and filter functionality tested

### Error Handling
- [ ] 404 page displays correctly
- [ ] 500 error page displays correctly
- [ ] Error logs reviewed (`C:\inetpub\logs\LogFiles\`)
- [ ] Application logs reviewed

## Post-Deployment

### Security Configuration
- [ ] DEBUG=False verified
- [ ] SECRET_KEY is unique and secure
- [ ] .env file permissions restricted
- [ ] SSL certificate installed (if using HTTPS)
- [ ] HTTPS redirect configured (if using SSL)
- [ ] Security headers configured in web.config
- [ ] Firewall rules reviewed and configured
- [ ] Strong database passwords set
- [ ] Windows Firewall enabled

### SSL/HTTPS Setup (If Applicable)
- [ ] SSL certificate obtained
- [ ] SSL certificate installed in IIS
- [ ] HTTPS binding added to website
- [ ] HTTP to HTTPS redirect enabled
- [ ] .env updated with HTTPS settings:
  - [ ] SECURE_SSL_REDIRECT=True
  - [ ] SESSION_COOKIE_SECURE=True
  - [ ] CSRF_COOKIE_SECURE=True
  - [ ] SECURE_HSTS_SECONDS=31536000

### Background Services
- [ ] Redis service running and auto-start enabled
- [ ] Celery Worker service created (AssetTrackerCelery)
- [ ] Celery Worker service started and tested
- [ ] Celery Beat service created (AssetTrackerCeleryBeat)
- [ ] Celery Beat service started and tested
- [ ] Celery tasks tested (warranty checks, power monitoring)

### Backup Configuration
- [ ] Backup directory created (`C:\AssetTracker_Backups`)
- [ ] Backup script configured (`backup_database.ps1`)
- [ ] Backup script tested manually
- [ ] Scheduled task created for automatic backups
- [ ] Backup restoration tested
- [ ] Off-site backup solution configured (optional)

### Monitoring and Logging
- [ ] Windows Event Log configured
- [ ] Application logging configured
- [ ] IIS logs location verified
- [ ] Log rotation configured
- [ ] Monitoring solution configured (optional)
- [ ] Alert notifications configured
- [ ] Performance counters configured (optional)

### Documentation
- [ ] Server credentials documented (securely)
- [ ] Database credentials documented (securely)
- [ ] Application URLs documented
- [ ] Backup procedures documented
- [ ] Restoration procedures documented
- [ ] Maintenance schedule documented
- [ ] Contact information for support documented

## Maintenance Plan

### Daily Tasks
- [ ] Monitor error logs
- [ ] Check application availability
- [ ] Verify backup completion

### Weekly Tasks
- [ ] Review error logs in detail
- [ ] Check disk space
- [ ] Monitor application performance
- [ ] Review security logs

### Monthly Tasks
- [ ] Update Python packages
- [ ] Review and apply Windows updates
- [ ] Test backup restoration
- [ ] Review access logs
- [ ] Performance optimization

### Quarterly Tasks
- [ ] Update Django version
- [ ] Security audit
- [ ] Database optimization
- [ ] Review and update documentation
- [ ] Disaster recovery drill

## Sign-Off

### Completed By
- **Name**: ____________________
- **Date**: ____________________
- **Signature**: ____________________

### Verified By
- **Name**: ____________________
- **Date**: ____________________
- **Signature**: ____________________

### Notes and Issues
```
(Record any issues encountered during deployment and their resolutions)




```

---

**Deployment Status**: 
- [ ] Development
- [ ] Staging
- [ ] Production

**Go-Live Date**: ____________________

**Next Review Date**: ____________________
