# Asset Tracker - Linux Deployment Quick Start

## 🎯 Prerequisites Checklist

- [ ] Ubuntu/Debian Linux server (20.04+ or Debian 10+)
- [ ] Root or sudo access
- [ ] Server IP address or domain name
- [ ] SSH access to server

## 🚀 5-Minute Deployment

### 1. Prepare Server (Run on Linux server)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv python3-dev \
    postgresql postgresql-contrib libpq-dev \
    nginx git build-essential
```

### 2. Setup Database

```bash
# Create PostgreSQL database and user
sudo -u postgres psql << EOF
CREATE DATABASE asset_tracker_db;
CREATE USER asset_tracker_user WITH PASSWORD 'ChangeThisPassword123!';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker_db TO asset_tracker_user;
\q
EOF
```

### 3. Upload Project Files

**From Windows machine:**
```powershell
# Compress project (exclude venv, __pycache__, .git)
Compress-Archive -Path "D:\Asset tracker\*" -DestinationPath "D:\asset_tracker.zip"

# Upload to server using WinSCP, FileZilla, or SCP
# Example with SCP:
scp "D:\asset_tracker.zip" user@your_server_ip:/tmp/
```

**On Linux server:**
```bash
# Extract files
cd /tmp
unzip asset_tracker.zip -d /tmp/asset_tracker
sudo mkdir -p /var/www/asset_tracker
sudo mv /tmp/asset_tracker/* /var/www/asset_tracker/
```

### 4. Configure Environment

```bash
cd /var/www/asset_tracker

# Create .env file
sudo cp linux_hosting/.env.example .env

# Edit .env with your values
sudo nano .env
```

**Required changes in .env:**
- `SECRET_KEY` - Generate new: `python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`
- `DB_PASSWORD` - Your database password (ChangeThisPassword123!)
- `ALLOWED_HOSTS` - Your domain or IP (e.g., 192.168.1.100,yourdomain.com)
- `EMAIL_*` - Your email settings

### 5. Run Automated Deployment

```bash
cd /var/www/asset_tracker
sudo chmod +x linux_hosting/*.sh
sudo bash linux_hosting/deploy.sh
```

This script will:
- Create virtual environment
- Install Python dependencies
- Run database migrations
- Collect static files
- Configure Nginx
- Set up Gunicorn service
- Start all services

### 6. Create Admin User

```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py createsuperuser
```

### 7. Access Your Application

Open browser and go to:
- `http://your_server_ip/` or
- `http://yourdomain.com/`

Admin panel:
- `http://your_server_ip/admin/`

## 🔐 Optional: Setup SSL Certificate (Free)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
```

## ✅ Verify Deployment

```bash
# Check services are running
sudo systemctl status asset_tracker
sudo systemctl status nginx

# Check if application is responding
curl http://localhost

# View logs
sudo journalctl -u asset_tracker -n 50
```

## 🔧 Common Post-Deployment Tasks

### Update Nginx Configuration with Your Domain

```bash
sudo nano /etc/nginx/sites-available/asset_tracker

# Change this line:
# server_name your_domain.com www.your_domain.com;
# To your actual domain or IP

# Reload Nginx
sudo systemctl reload nginx
```

### Setup Automatic Backups

```bash
# Make backup script executable
sudo chmod +x /var/www/asset_tracker/linux_hosting/backup.sh

# Test backup
sudo bash /var/www/asset_tracker/linux_hosting/backup.sh

# Add to crontab for daily backups at 2 AM
sudo crontab -e
# Add this line:
0 2 * * * /var/www/asset_tracker/linux_hosting/backup.sh
```

### Configure Firewall

```bash
# Allow HTTP, HTTPS, and SSH
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status
```

## 📝 Useful Commands

```bash
# Restart application
sudo systemctl restart asset_tracker

# View real-time logs
sudo journalctl -u asset_tracker -f

# Update application
cd /var/www/asset_tracker
sudo bash linux_hosting/update.sh

# Backup database
sudo bash linux_hosting/backup.sh
```

## ❓ Troubleshooting

### Application not accessible
```bash
# Check services
sudo systemctl status asset_tracker nginx

# Check logs
sudo journalctl -u asset_tracker -n 100
sudo tail -f /var/log/nginx/asset_tracker_error.log
```

### 502 Bad Gateway Error
```bash
# Restart Gunicorn
sudo systemctl restart asset_tracker

# Check if socket file exists
ls -l /run/asset_tracker.sock
```

### Static files not loading
```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify .env database settings
cat /var/www/asset_tracker/.env | grep DB_
```

### Permission issues
```bash
# Fix permissions
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

## 📚 Next Steps

1. **Configure Email Settings** - Update SMTP settings in `.env` for notifications
2. **Setup SSL Certificate** - Follow SSL setup guide above
3. **Configure Backups** - Set up automatic daily backups
4. **Monitor Application** - Set up monitoring tools (optional)
5. **Security Hardening** - Follow security checklist in DEPLOYMENT_GUIDE.md

## 📞 Need Help?

See **DEPLOYMENT_GUIDE.md** for detailed documentation.

Check logs first:
```bash
sudo journalctl -u asset_tracker -f
sudo tail -f /var/log/nginx/asset_tracker_error.log
```

---

**Deployment Time:** ~15-20 minutes
**Difficulty:** Intermediate
**Support:** Check DEPLOYMENT_GUIDE.md for detailed help
