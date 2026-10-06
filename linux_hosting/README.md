# Asset Tracker - Linux Hosting Files

This directory contains all the necessary configuration files and scripts for deploying the Asset Tracker Django application on a Linux server.

## 📁 Files Overview

### Configuration Files

1. **gunicorn_config.py** - Gunicorn WSGI server configuration
2. **nginx.conf** - Nginx web server configuration
3. **gunicorn.service** - Systemd service file for Gunicorn
4. **gunicorn.socket** - Systemd socket file for Gunicorn
5. **settings_production.py** - Django production settings
6. **.env.example** - Environment variables template

### Scripts

1. **deploy.sh** - Automated deployment script
2. **update.sh** - Application update script
3. **backup.sh** - Database and media files backup script

### Documentation

1. **DEPLOYMENT_GUIDE.md** - Comprehensive deployment guide
2. **requirements_production.txt** - Python dependencies for production

## 🚀 Quick Start

### Prerequisites
- Ubuntu 20.04+ or Debian 10+ server
- Root or sudo access
- Domain name (optional but recommended)

### Step-by-Step Deployment

1. **Prepare Server**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv nginx postgresql git
   ```

2. **Upload Project Files**
   ```bash
   # Upload your project to /var/www/asset_tracker
   scp -r "D:\Asset tracker" user@server:/tmp/
   sudo mv /tmp/asset_tracker /var/www/
   ```

3. **Set Up Database**
   ```bash
   sudo -u postgres createdb asset_tracker_db
   sudo -u postgres createuser asset_tracker_user
   sudo -u postgres psql -c "ALTER USER asset_tracker_user WITH PASSWORD 'your_password';"
   ```

4. **Configure Environment**
   ```bash
   cd /var/www/asset_tracker
   cp linux_hosting/.env.example .env
   sudo nano .env  # Edit with your values
   ```

5. **Run Deployment Script**
   ```bash
   cd /var/www/asset_tracker
   sudo bash linux_hosting/deploy.sh
   ```

6. **Configure Domain (Optional)**
   ```bash
   sudo nano /etc/nginx/sites-available/asset_tracker
   # Update server_name with your domain
   sudo systemctl reload nginx
   ```

7. **Set Up SSL (Recommended)**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

## 📋 Management Commands

### Service Management
```bash
# Start services
sudo systemctl start asset_tracker
sudo systemctl start nginx

# Stop services
sudo systemctl stop asset_tracker
sudo systemctl stop nginx

# Restart services
sudo systemctl restart asset_tracker
sudo systemctl restart nginx

# Check status
sudo systemctl status asset_tracker
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u asset_tracker -f

# Nginx logs
sudo tail -f /var/log/nginx/asset_tracker_access.log
sudo tail -f /var/log/nginx/asset_tracker_error.log

# Gunicorn logs
sudo tail -f /var/log/asset_tracker/gunicorn_error.log
```

### Backup & Update
```bash
# Create backup
sudo bash /var/www/asset_tracker/linux_hosting/backup.sh

# Update application
sudo bash /var/www/asset_tracker/linux_hosting/update.sh
```

## 🔧 Troubleshooting

### Issue: 502 Bad Gateway
```bash
# Check if Gunicorn is running
sudo systemctl status asset_tracker
sudo systemctl restart asset_tracker
```

### Issue: Static Files Not Loading
```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Database Connection Error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify .env file has correct credentials
cat /var/www/asset_tracker/.env

# Test database connection
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py dbshell
```

### Issue: Permission Denied
```bash
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

## 🔐 Security Recommendations

1. **Change Default Passwords**
   - Database password
   - Django SECRET_KEY
   - Admin account password

2. **Enable Firewall**
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw allow OpenSSH
   sudo ufw enable
   ```

3. **Install SSL Certificate**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

4. **Regular Updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

5. **Enable Automatic Backups**
   ```bash
   # Add to crontab
   sudo crontab -e
   # Add line: 0 2 * * * /var/www/asset_tracker/linux_hosting/backup.sh
   ```

## 📊 Monitoring

### Check Application Health
```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Check active connections
netstat -tuln | grep :8000
netstat -tuln | grep :80
```

### Performance Monitoring
```bash
# Gunicorn workers
ps aux | grep gunicorn

# Nginx status
curl http://localhost/nginx_status  # if configured
```

## 📞 Support

For detailed instructions, see **DEPLOYMENT_GUIDE.md**

For issues:
1. Check logs first
2. Verify all services are running
3. Check file permissions
4. Review configuration files

## 🔄 Update History

- **v1.0** - Initial deployment configuration
- Supports: Ubuntu 20.04+, PostgreSQL/MySQL, Nginx, Gunicorn
- Python 3.8+, Django 4.2.30

---

**Note:** Always test deployment on a staging server before production!
