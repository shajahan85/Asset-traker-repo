# Asset Tracker - Linux Deployment Guide

## ✅ Why Linux is Better for Django

- **Easier setup** - No FastCGI complexity
- **Better performance** - Nginx + Gunicorn is faster
- **Standard approach** - Industry best practice
- **More documentation** - Huge community support
- **Simpler debugging** - Better error messages

---

## 📋 Requirements

### Server Specifications

**Minimum:**
- CPU: 2 cores
- RAM: 2 GB
- Disk: 10 GB
- OS: Ubuntu 20.04/22.04 LTS or CentOS 7/8

**Recommended:**
- CPU: 4 cores
- RAM: 4 GB
- Disk: 20 GB SSD
- OS: Ubuntu 22.04 LTS

### Software Requirements

- Ubuntu 20.04/22.04 LTS (recommended)
- Python 3.9+
- PostgreSQL 12+ (or SQLite for testing)
- Nginx
- Redis (for Celery background tasks)
- Git (optional, for updates)

---

## 🚀 Complete Step-by-Step Deployment

### Phase 1: Initial Server Setup (15 minutes)

```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y nginx
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y redis-server
sudo apt install -y git curl

# Verify installations
python3 --version  # Should be 3.9 or higher
nginx -v
psql --version
redis-cli --version
```

---

### Phase 2: Setup PostgreSQL Database (10 minutes)

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL shell, run:
CREATE DATABASE asset_tracker;
CREATE USER asset_tracker_user WITH PASSWORD 'YourSecurePassword123!';
ALTER ROLE asset_tracker_user SET client_encoding TO 'utf8';
ALTER ROLE asset_tracker_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE asset_tracker_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE asset_tracker TO asset_tracker_user;
\q

# Test connection
psql -U asset_tracker_user -d asset_tracker -h localhost -W
# Enter password when prompted, then \q to exit
```

---

### Phase 3: Create Application User (5 minutes)

```bash
# Create dedicated user for the application
sudo adduser --system --group --home /opt/assettracker assettracker

# Create necessary directories
sudo mkdir -p /opt/assettracker
sudo chown -R assettracker:assettracker /opt/assettracker
```

---

### Phase 4: Upload Application Files (10 minutes)

**Option A: Using SCP (from your Windows machine)**

```powershell
# From your development machine (Windows)
# Replace YOUR_SERVER_IP with actual server IP

scp -r "D:\Asset tracker\*" root@YOUR_SERVER_IP:/tmp/assettracker

# Then on server:
sudo mv /tmp/assettracker/* /opt/assettracker/
sudo chown -R assettracker:assettracker /opt/assettracker
```

**Option B: Using Git**

```bash
# On server
cd /opt/assettracker
sudo -u assettracker git clone YOUR_GIT_REPO_URL .
```

**Option C: Manual Upload**
- Use WinSCP or FileZilla
- Upload to `/opt/assettracker/`
- Set owner: `sudo chown -R assettracker:assettracker /opt/assettracker`

---

### Phase 5: Setup Python Environment (10 minutes)

```bash
# Switch to application user
sudo su - assettracker
cd /opt/assettracker

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install Gunicorn (production WSGI server)
pip install gunicorn

# Exit assettracker user
exit
```

---

### Phase 6: Configure Environment (10 minutes)

```bash
# Create .env file
sudo nano /opt/assettracker/.env
```

**Add this content to .env:**

```ini
# Django Core
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production
ALLOWED_HOSTS=your-server-ip,yourdomain.com,localhost

# Database (PostgreSQL)
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=asset_tracker
DATABASE_USER=asset_tracker_user
DATABASE_PASSWORD=YourSecurePassword123!
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis (for Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=Asset Tracker <noreply@yourdomain.com>

# Security (enable after HTTPS setup)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

**Save and exit:** Ctrl+X, Y, Enter

```bash
# Set secure permissions
sudo chown assettracker:assettracker /opt/assettracker/.env
sudo chmod 600 /opt/assettracker/.env
```

---

### Phase 7: Run Django Setup (10 minutes)

```bash
# Switch to application user
sudo su - assettracker
cd /opt/assettracker
source venv/bin/activate

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser
# Follow prompts to create admin user

# Test that Django works
python manage.py check

# Exit
exit
```

---

### Phase 8: Configure Gunicorn (15 minutes)

```bash
# Create Gunicorn configuration file
sudo nano /opt/assettracker/gunicorn_config.py
```

**Add this content:**

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/opt/assettracker/logs/gunicorn_access.log"
errorlog = "/opt/assettracker/logs/gunicorn_error.log"
loglevel = "info"

# Process naming
proc_name = "assettracker"

# Server mechanics
daemon = False
pidfile = "/opt/assettracker/gunicorn.pid"
user = "assettracker"
group = "assettracker"
```

**Save and create logs directory:**

```bash
sudo mkdir -p /opt/assettracker/logs
sudo chown -R assettracker:assettracker /opt/assettracker/logs
```

---

### Phase 9: Create Systemd Service (10 minutes)

```bash
# Create Gunicorn service file
sudo nano /etc/systemd/system/assettracker.service
```

**Add this content:**

```ini
[Unit]
Description=Asset Tracker Gunicorn Server
After=network.target

[Service]
Type=notify
User=assettracker
Group=assettracker
WorkingDirectory=/opt/assettracker
Environment="PATH=/opt/assettracker/venv/bin"
ExecStart=/opt/assettracker/venv/bin/gunicorn asset_tracker.wsgi:application -c /opt/assettracker/gunicorn_config.py
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Save and enable service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable assettracker

# Start service
sudo systemctl start assettracker

# Check status
sudo systemctl status assettracker

# View logs if needed
sudo journalctl -u assettracker -f
```

---

### Phase 10: Configure Nginx (15 minutes)

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/assettracker
```

**Add this content:**

```nginx
upstream assettracker_server {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-server-ip yourdomain.com;

    client_max_body_size 100M;

    access_log /var/log/nginx/assettracker_access.log;
    error_log /var/log/nginx/assettracker_error.log;

    # Static files
    location /static/ {
        alias /opt/assettracker/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /opt/assettracker/media/;
        expires 7d;
    }

    # Main application
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://assettracker_server;
    }
}
```

**Enable site and restart Nginx:**

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/assettracker /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Enable Nginx on boot
sudo systemctl enable nginx
```

---

### Phase 11: Configure Celery Services (15 minutes)

**Create Celery Worker Service:**

```bash
sudo nano /etc/systemd/system/assettracker-celery.service
```

```ini
[Unit]
Description=Asset Tracker Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=assettracker
Group=assettracker
WorkingDirectory=/opt/assettracker
Environment="PATH=/opt/assettracker/venv/bin"
ExecStart=/opt/assettracker/venv/bin/celery -A asset_tracker worker --loglevel=info --pidfile=/opt/assettracker/celery_worker.pid
ExecStop=/bin/kill -s TERM $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Create Celery Beat Service:**

```bash
sudo nano /etc/systemd/system/assettracker-celerybeat.service
```

```ini
[Unit]
Description=Asset Tracker Celery Beat
After=network.target redis.service

[Service]
Type=simple
User=assettracker
Group=assettracker
WorkingDirectory=/opt/assettracker
Environment="PATH=/opt/assettracker/venv/bin"
ExecStart=/opt/assettracker/venv/bin/celery -A asset_tracker beat --loglevel=info --pidfile=/opt/assettracker/celery_beat.pid
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable assettracker-celery
sudo systemctl enable assettracker-celerybeat

# Start services
sudo systemctl start assettracker-celery
sudo systemctl start assettracker-celerybeat

# Check status
sudo systemctl status assettracker-celery
sudo systemctl status assettracker-celerybeat
```

---

### Phase 12: Configure Firewall (5 minutes)

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (important!)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

---

### Phase 13: Test Deployment ✅

```bash
# Test from server
curl http://localhost

# Test from your machine
# Open browser: http://YOUR_SERVER_IP/
```

**You should see your Asset Tracker application!**

---

## 🔒 Phase 14: Setup SSL/HTTPS (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Update .env for HTTPS
sudo nano /opt/assettracker/.env
# Set these to True:
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True

# Restart application
sudo systemctl restart assettracker
```

---

## 📊 Useful Commands

### Application Management

```bash
# Restart application
sudo systemctl restart assettracker

# View application logs
sudo journalctl -u assettracker -f

# View Gunicorn logs
sudo tail -f /opt/assettracker/logs/gunicorn_error.log

# Restart Nginx
sudo systemctl restart nginx

# Restart Celery
sudo systemctl restart assettracker-celery
sudo systemctl restart assettracker-celerybeat
```

### Django Management

```bash
# Run management commands
sudo su - assettracker
cd /opt/assettracker
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Django shell
python manage.py shell

exit
```

### Database Backup

```bash
# Backup PostgreSQL database
sudo -u postgres pg_dump asset_tracker > backup_$(date +%Y%m%d).sql

# Restore from backup
sudo -u postgres psql asset_tracker < backup_20260821.sql
```

---

## 🔧 Troubleshooting

### Application Won't Start

```bash
# Check service status
sudo systemctl status assettracker

# View detailed logs
sudo journalctl -u assettracker -n 100

# Test Gunicorn manually
sudo su - assettracker
cd /opt/assettracker
source venv/bin/activate
gunicorn asset_tracker.wsgi:application --bind 127.0.0.1:8000
```

### Static Files Not Loading

```bash
# Re-collect static files
sudo su - assettracker
cd /opt/assettracker
source venv/bin/activate
python manage.py collectstatic --noinput
exit

# Check permissions
ls -la /opt/assettracker/staticfiles/

# Restart Nginx
sudo systemctl restart nginx
```

### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U asset_tracker_user -d asset_tracker -h localhost -W

# Check .env file
sudo cat /opt/assettracker/.env | grep DATABASE
```

---

## 🎯 Quick Comparison: IIS vs Linux

| Feature | Windows IIS | Linux Nginx + Gunicorn |
|---------|------------|------------------------|
| Setup Time | 2-4 hours | 1-2 hours |
| Complexity | High | Medium |
| Performance | Good | Excellent |
| Documentation | Limited | Extensive |
| Debugging | Difficult | Easy |
| Cost | Windows license | Free |
| Community Support | Low | High |
| **Recommended** | ❌ No | ✅ **YES!** |

---

## 📋 Deployment Checklist

- [ ] Server with Ubuntu 20.04/22.04 LTS
- [ ] Python 3.9+ installed
- [ ] PostgreSQL database created
- [ ] Redis installed and running
- [ ] Application files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed (requirements.txt)
- [ ] .env file configured
- [ ] Migrations run
- [ ] Static files collected
- [ ] Superuser created
- [ ] Gunicorn configured and running
- [ ] Nginx configured and running
- [ ] Celery services running
- [ ] Firewall configured
- [ ] SSL certificate installed (optional)
- [ ] Application tested and working

---

## 🆘 Need Help?

**Total deployment time: 2-3 hours for first time**

The Linux deployment is straightforward and well-documented. If you encounter any issues, the error messages are clear and easy to debug.

**Much better than IIS! 🎉**
