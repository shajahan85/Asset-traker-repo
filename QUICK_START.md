# Asset Tracker - Quick Start Guide

## 🚀 First Time Setup (On Test Server)

### Option 1: Automated Setup (Recommended)

1. **Copy project to server**
   ```
   Copy entire folder to: C:\inetpub\wwwroot\asset-tracker
   (or any location you prefer)
   ```

2. **Run deployment script** (as Administrator)
   ```powershell
   cd C:\inetpub\wwwroot\asset-tracker
   .\deploy_test_server.ps1
   ```

3. **Follow prompts to create admin user**

4. **Server will start automatically!**

### Option 2: Manual Setup

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate it
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py migrate

# 5. Create admin user
python manage.py createsuperuser

# 6. Collect static files
python manage.py collectstatic

# 7. Start server
python manage.py runserver 0.0.0.0:8000
```

---

## 🔄 Daily Use

### Start the Server

```powershell
cd C:\inetpub\wwwroot\asset-tracker
.\start_server.ps1
```

**OR manually:**

```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver 0.0.0.0:8000
```

### Stop the Server

Press `Ctrl + C` in the terminal

---

## 🌐 Access the Application

- **From server:** `http://localhost:8000`
- **From network:** `http://your-server-ip:8000`
- **Admin panel:** `http://your-server-ip:8000/admin/`

---

## 📝 Common Commands

### Database Operations

```powershell
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database (WARNING: Deletes all data!)
Remove-Item db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### User Management

```powershell
# Create superuser
python manage.py createsuperuser

# Change user password
python manage.py changepassword username

# Create staff user programmatically
python manage.py shell
```

Then in Python shell:
```python
from django.contrib.auth.models import User
user = User.objects.create_user('username', 'email@example.com', 'password')
user.is_staff = True
user.save()
```

### Static Files

```powershell
# Collect static files
python manage.py collectstatic --noinput

# Clear and re-collect
python manage.py collectstatic --noinput --clear
```

### Backup & Restore

**Backup:**
```powershell
# Database
Copy-Item db.sqlite3 "db.sqlite3.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Media files
Compress-Archive -Path media -DestinationPath "media_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
```

**Restore:**
```powershell
# Database
Copy-Item db.sqlite3.backup.20240101_120000 db.sqlite3

# Media files
Expand-Archive -Path media_backup_20240101_120000.zip -DestinationPath media -Force
```

---

## 🔧 Troubleshooting

### Can't access from other computers

```powershell
# Add firewall rule
New-NetFirewallRule -DisplayName "Django Test Server" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow

# Check ALLOWED_HOSTS in .env file
# Should include: localhost,127.0.0.1,your-server-ip
```

### "Module not found" errors

```powershell
# Reinstall dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt --upgrade
```

### Database errors

```powershell
# Check if migrations are applied
python manage.py showmigrations

# Apply pending migrations
python manage.py migrate
```

### Static files not loading

```powershell
# Re-collect static files
python manage.py collectstatic --noinput --clear

# Check settings
python manage.py diffsettings | Select-String "STATIC"
```

### Permission errors

```powershell
# Give permissions to media folder
icacls "media" /grant "Users:(OI)(CI)F" /T
```

---

## 📦 Update Application

```powershell
# 1. Stop server (Ctrl+C)

# 2. Backup database
Copy-Item db.sqlite3 "db.sqlite3.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 3. Pull latest changes (if using Git)
git pull

# 4. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 5. Update dependencies
pip install -r requirements.txt --upgrade

# 6. Apply new migrations
python manage.py migrate

# 7. Collect static files
python manage.py collectstatic --noinput

# 8. Restart server
.\start_server.ps1
```

---

## 🔐 Security Notes for Test Server

- ✅ Change default SECRET_KEY in .env
- ✅ Use strong admin passwords
- ✅ Keep DEBUG=True only for test servers
- ✅ Set DEBUG=False for production
- ✅ Regularly backup database
- ✅ Update ALLOWED_HOSTS in .env

---

## 📞 Getting Help

Check the logs:
```powershell
# Django logs
Get-Content authentication.log -Tail 50

# Windows Event Viewer
eventvwr.msc
```

Common log locations:
- Django logs: `authentication.log`
- IIS logs: `C:\inetpub\logs\LogFiles\`
- Application logs: `logs\stdout.log`

---

## 🎯 Quick Feature Test

After deployment, test these features:

1. ✅ Login to admin panel
2. ✅ Create a new asset
3. ✅ Upload an attachment
4. ✅ Export assets to Excel
5. ✅ Import assets from Excel
6. ✅ View freed systems
7. ✅ Access warranty tracking
8. ✅ Manage IP addresses

---

## 🚦 Server Status Check

```powershell
# Check if server is running
Test-NetConnection -ComputerName localhost -Port 8000

# Check Python process
Get-Process python

# View active connections
netstat -an | Select-String "8000"
```

---

**For detailed deployment instructions, see DEPLOYMENT.md**
