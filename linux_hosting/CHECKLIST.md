# Linux Deployment Checklist

Use this checklist to ensure a successful deployment of the Asset Tracker application.

## Pre-Deployment

### Server Requirements
- [ ] Ubuntu 20.04+ or Debian 10+ server
- [ ] Minimum 2GB RAM
- [ ] 20GB+ disk space
- [ ] Root or sudo access
- [ ] Static IP address or domain name

### Software Installation
- [ ] Python 3.8+ installed
- [ ] PostgreSQL or MySQL installed
- [ ] Nginx installed
- [ ] Git installed (optional)

### Files Prepared
- [ ] Project files uploaded to `/var/www/asset_tracker`
- [ ] `.env` file created with correct values
- [ ] Database credentials ready
- [ ] Email SMTP credentials ready (if using email features)

## Deployment Steps

### Database Setup
- [ ] Database created
- [ ] Database user created
- [ ] Permissions granted to user
- [ ] Connection tested from server

### Application Configuration
- [ ] `.env` file configured with:
  - [ ] SECRET_KEY (new random key)
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS (domain/IP)
  - [ ] Database credentials
  - [ ] Email settings
- [ ] settings_production.py reviewed
- [ ] STATIC_ROOT path correct
- [ ] MEDIA_ROOT path correct

### Virtual Environment
- [ ] Virtual environment created at `/var/www/asset_tracker/venv`
- [ ] Dependencies installed from requirements_production.txt
- [ ] Gunicorn installed

### Django Setup
- [ ] Migrations run (`python manage.py migrate`)
- [ ] Superuser created (`python manage.py createsuperuser`)
- [ ] Static files collected (`python manage.py collectstatic`)

### Web Server Configuration
- [ ] Nginx configuration copied to `/etc/nginx/sites-available/`
- [ ] Symbolic link created in `/etc/nginx/sites-enabled/`
- [ ] server_name updated with actual domain/IP
- [ ] Nginx configuration tested (`sudo nginx -t`)
- [ ] Nginx restarted

### Gunicorn Service
- [ ] gunicorn.service copied to `/etc/systemd/system/`
- [ ] gunicorn.socket copied to `/etc/systemd/system/`
- [ ] Paths in service file correct
- [ ] Systemd daemon reloaded
- [ ] Service started and enabled
- [ ] Service status checked (running)

### File Permissions
- [ ] Project owned by www-data user
- [ ] Correct permissions set (755 for directories, 644 for files)
- [ ] Log directories created with correct permissions
- [ ] Media upload directory writable

### Security
- [ ] DEBUG = False in production
- [ ] Strong SECRET_KEY generated
- [ ] Database using strong password
- [ ] Firewall configured (UFW)
- [ ] Only necessary ports open (80, 443, 22)
- [ ] SSH key authentication configured
- [ ] Root login disabled via SSH

## Post-Deployment

### Testing
- [ ] Application accessible via HTTP
- [ ] Admin panel accessible
- [ ] Static files loading correctly
- [ ] Media files uploading correctly
- [ ] Database operations working
- [ ] Email sending working (if configured)
- [ ] All main features tested:
  - [ ] Asset creation
  - [ ] Asset editing
  - [ ] Asset listing with filters
  - [ ] Excel export
  - [ ] User authentication
  - [ ] History tracking

### SSL Configuration (Highly Recommended)
- [ ] Certbot installed
- [ ] SSL certificate obtained
- [ ] HTTPS working
- [ ] HTTP to HTTPS redirect working
- [ ] Auto-renewal configured

### Monitoring & Maintenance
- [ ] Log files accessible
- [ ] Log rotation configured
- [ ] Backup script tested
- [ ] Automatic backups scheduled (cron)
- [ ] Update script tested
- [ ] Monitoring tools configured (optional)

### Documentation
- [ ] Server credentials documented
- [ ] Database credentials documented
- [ ] Admin user credentials documented
- [ ] Deployment notes documented
- [ ] Team members have access to documentation

## Verification Commands

Run these commands to verify deployment:

```bash
# Check services
sudo systemctl status asset_tracker
sudo systemctl status nginx
sudo systemctl status postgresql

# Check application
curl http://localhost
curl http://your_domain.com

# Check logs
sudo journalctl -u asset_tracker -n 50
sudo tail -20 /var/log/nginx/asset_tracker_access.log

# Check file permissions
ls -la /var/www/asset_tracker
ls -la /var/www/asset_tracker/staticfiles

# Check disk space
df -h

# Check memory usage
free -h

# Check active connections
netstat -tuln | grep :8000
netstat -tuln | grep :80
```

## Go-Live Checklist

### Final Pre-Launch
- [ ] All features tested on production server
- [ ] Performance tested with expected load
- [ ] Backup system tested and working
- [ ] Rollback plan prepared
- [ ] Team briefed on deployment
- [ ] Maintenance window communicated (if needed)

### Launch
- [ ] DNS updated (if using new domain)
- [ ] Old system gracefully shutdown (if applicable)
- [ ] Users notified of new system
- [ ] Login credentials distributed
- [ ] Support team ready

### Post-Launch Monitoring
- [ ] Application monitored for first 24 hours
- [ ] Error logs checked regularly
- [ ] Performance metrics reviewed
- [ ] User feedback collected
- [ ] Issues documented and addressed

## Troubleshooting Quick Reference

| Issue | Check | Fix |
|-------|-------|-----|
| 502 Bad Gateway | Gunicorn status | `sudo systemctl restart asset_tracker` |
| Static files not loading | collectstatic run | `python manage.py collectstatic` |
| Database connection error | PostgreSQL running | `sudo systemctl start postgresql` |
| Permission denied | File ownership | `sudo chown -R www-data:www-data /var/www/asset_tracker` |
| Application not accessible | Firewall rules | `sudo ufw allow 'Nginx Full'` |

## Maintenance Schedule

### Daily
- [ ] Check application logs for errors
- [ ] Monitor disk space

### Weekly
- [ ] Review access logs
- [ ] Check backup success
- [ ] Review system resources (CPU, RAM)

### Monthly
- [ ] Update system packages
- [ ] Review security logs
- [ ] Test backup restoration
- [ ] Review and rotate logs

### Quarterly
- [ ] Update Python dependencies
- [ ] Review and update security configurations
- [ ] Performance optimization review
- [ ] Disaster recovery test

---

## Sign-Off

**Deployment Date:** _______________

**Deployed By:** _______________

**Verified By:** _______________

**Production URL:** _______________

**Admin URL:** _______________

**Notes:**
_______________________________________________________
_______________________________________________________
_______________________________________________________

---

**Status:** 
- [ ] Deployment Complete
- [ ] All Tests Passed
- [ ] Production Ready
- [ ] Team Notified
- [ ] Documentation Updated

