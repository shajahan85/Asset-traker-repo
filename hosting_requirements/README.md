# Asset Tracker - IIS Hosting Requirements

This folder contains all necessary documentation and configuration files for deploying the Asset Tracker Django application on Windows IIS (Internet Information Services).

## 📁 Folder Contents

### Documentation Files

| File | Description |
|------|-------------|
| **IIS_DEPLOYMENT_GUIDE.md** | Complete step-by-step deployment guide with detailed instructions |
| **QUICK_START.md** | Condensed deployment guide for experienced administrators |
| **DEPLOYMENT_CHECKLIST.md** | Comprehensive checklist to ensure nothing is missed |
| **TROUBLESHOOTING.md** | Common issues and solutions |
| **README.md** | This file - overview of all resources |

### Configuration Files

| File | Description |
|------|-------------|
| **web.config** | IIS configuration file for FastCGI and URL rewriting |
| **.env.production** | Production environment variables template |
| **requirements_production.txt** | Python packages required for production deployment |

### Scripts

| File | Description |
|------|-------------|
| **backup_database.ps1** | PowerShell script for automated database backups |

## 🚀 Quick Navigation

### First Time Deployment?
Start here: **[IIS_DEPLOYMENT_GUIDE.md](IIS_DEPLOYMENT_GUIDE.md)**

### Experienced with IIS and Django?
Use this: **[QUICK_START.md](QUICK_START.md)**

### During Deployment?
Follow this: **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)**

### Encountering Issues?
Check this: **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)**

## 📋 Deployment Overview

### Prerequisites
- Windows Server 2016+ or Windows 10/11 Pro
- IIS 10.0 or later with CGI module
- Python 3.9+ (64-bit recommended)
- PostgreSQL or SQL Server (recommended) or SQLite
- Redis (for background tasks)
- URL Rewrite Module for IIS

### Key Steps
1. Install prerequisites (Python, IIS, Redis, Database)
2. Copy application files to `C:\inetpub\wwwroot\AssetTracker`
3. Create virtual environment and install dependencies
4. Configure `.env` file with production settings
5. Set up database and run migrations
6. Configure IIS (Application Pool, Website, Handler)
7. Deploy `web.config` file
8. Set folder permissions
9. Test deployment
10. Configure SSL/HTTPS (recommended)
11. Set up Celery services
12. Configure backups

## 🔧 Configuration Files Usage

### web.config
```powershell
# Copy to application root
Copy-Item "web.config" -Destination "C:\inetpub\wwwroot\AssetTracker\web.config"

# Update these values:
# - scriptProcessor path (from wfastcgi-enable output)
# - PYTHONPATH
# - Application paths in fastCgi section
```

### .env.production
```powershell
# Copy to application root as .env
Copy-Item ".env.production" -Destination "C:\inetpub\wwwroot\AssetTracker\.env"

# Edit and update:
# - SECRET_KEY (generate new one)
# - DEBUG (set to False)
# - ALLOWED_HOSTS (add your domain/IP)
# - Database credentials
# - Email settings
# - Redis URL
```

### requirements_production.txt
```powershell
# Install in virtual environment
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1
pip install -r hosting_requirements\requirements_production.txt
```

### backup_database.ps1
```powershell
# Test manually first
.\backup_database.ps1

# Then schedule with Task Scheduler
schtasks /create /tn "AssetTracker_DailyBackup" /tr "powershell.exe -ExecutionPolicy Bypass -File C:\inetpub\wwwroot\AssetTracker\hosting_requirements\backup_database.ps1" /sc daily /st 02:00 /ru SYSTEM
```

## 🔐 Security Checklist

Before going live, ensure:
- [ ] DEBUG is set to False
- [ ] SECRET_KEY is unique and strong
- [ ] ALLOWED_HOSTS is properly configured
- [ ] Database uses strong passwords
- [ ] .env file permissions are restricted
- [ ] SSL/HTTPS is configured
- [ ] Firewall rules are in place
- [ ] Regular backups are scheduled
- [ ] Windows updates are applied

## 📊 System Requirements

### Minimum
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 10 GB free space
- **Network**: 10 Mbps

### Recommended
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Disk**: 50+ GB free space (SSD preferred)
- **Network**: 100 Mbps
- **Backup**: Separate backup storage

## 🎯 Key Features

This Asset Tracker application includes:
- Asset management system
- Employee tracking with accessories
- IP address management
- Power monitoring
- Warranty tracking
- Network device tracking
- Hyper-V VM management
- Excel import/export
- Email notifications
- Automated background tasks (Celery)

## 📞 Support Resources

### Official Documentation
- **Django**: https://docs.djangoproject.com/
- **IIS**: https://docs.microsoft.com/en-us/iis/
- **FastCGI**: https://pypi.org/project/wfastcgi/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/documentation

### Useful Commands

```powershell
# Restart IIS
iisreset /restart

# Check service status
Get-Service W3SVC,WAS

# View recent IIS logs
Get-Content "C:\inetpub\logs\LogFiles\W3SVC1\*.log" | Select-Object -Last 50

# Activate virtual environment
cd C:\inetpub\wwwroot\AssetTracker
.\venv\Scripts\Activate.ps1

# Run Django management commands
python manage.py <command>

# Test Redis connection
redis-cli ping

# Check Celery services
nssm status AssetTrackerCelery
nssm status AssetTrackerCeleryBeat
```

## 🔄 Updating the Application

```powershell
# Stop Celery services
nssm stop AssetTrackerCelery
nssm stop AssetTrackerCeleryBeat

# Backup database (run backup script)
.\hosting_requirements\backup_database.ps1

# Pull latest code (if using Git)
git pull origin main

# Activate virtual environment
cd C:\inetpub\wwwroot\AssetTracker
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

## 📅 Maintenance Schedule

### Daily
- Monitor error logs
- Check application availability
- Verify backup completion

### Weekly
- Review detailed error logs
- Check disk space
- Monitor performance

### Monthly
- Update Python packages
- Apply Windows updates
- Test backup restoration
- Review security logs

### Quarterly
- Update Django version
- Security audit
- Database optimization
- Review documentation

## ⚠️ Important Notes

1. **Never commit .env files** to version control
2. **Always backup before updates**
3. **Test in staging environment** first
4. **Keep DEBUG=False** in production
5. **Use HTTPS** in production
6. **Regular backups** are critical
7. **Monitor logs** for security issues
8. **Keep software updated** for security patches

## 📈 Monitoring Recommendations

- Set up Windows Event Log monitoring
- Configure email alerts for critical errors
- Use Windows Performance Monitor for resource tracking
- Implement application performance monitoring (APM) tool
- Regular security audits

## 🆘 Emergency Contacts

Document your emergency contacts:
- **System Administrator**: _______________
- **Database Administrator**: _______________
- **Network Administrator**: _______________
- **Application Developer**: _______________
- **On-Call Support**: _______________

## 📝 Version History

- **v1.0** - Initial deployment documentation
- Created: August 2026

## 📜 License

This deployment documentation is part of the Asset Tracker project.

---

**Need Help?** 
- Start with the troubleshooting guide
- Check Django and IIS documentation
- Review log files for specific errors
- Consult with your system administrator

**Good luck with your deployment! 🚀**
