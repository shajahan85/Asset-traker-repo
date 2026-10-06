# Deployment Update Guide - Linux Server

Guide for deploying recent changes to your Linux production server.

---

## 📋 Recent Changes to Deploy

1. **Email Notification Toggle** - Checkbox to control email sending
2. **IP Series Quick Filter** - Quick filter buttons on Free IP page
3. **Freed Systems Table Fix** - Removed Issues column, fixed Actions visibility
4. **Employee Code in Emails** - Added to all email notifications
5. **Database Migration Tools** - Export/import scripts (if needed)

---

## 🚀 Quick Deployment (Using Git)

### Step 1: Commit Your Changes on Windows

```powershell
cd "d:\Asset tracker"

# Check what changed
git status

# Add all changes
git add .

# Commit with message
git commit -m "Add email notification toggle, IP filter, freed systems fix, employee code in emails"

# Push to repository
git push origin main
```

### Step 2: Update Linux Server

SSH into your Linux server and run:

```bash
# Navigate to application directory
cd /var/www/asset_tracker

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# No new migrations needed (only code changes)

# Collect static files (for template/CSS changes)
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart asset_tracker

# Verify it's running
sudo systemctl status asset_tracker
```

**Done!** ✅ Changes are live.

---

## 📦 Manual Deployment (Without Git)

If you're not using Git, follow these steps:

### Step 1: Create Archive on Windows

```powershell
cd "d:\Asset tracker"

# Create a zip of changed files
# Option A: Compress entire project
Compress-Archive -Path "d:\Asset tracker\*" -DestinationPath "d:\asset_tracker_update.zip" -Force

# Option B: Just the changed files (recommended)
# See list below for specific files
```

### Changed Files to Upload:

```
📁 assets/
  ├── forms/asset_forms.py                          ← Email toggle field
  ├── services/notification_service.py              ← Skip notification logic
  ├── templates/assets/
  │   ├── asset_form.html                          ← Checkbox in form
  │   ├── free_ips.html                            ← IP series filter
  │   └── freed_systems.html                       ← Removed Issues column
  
📁 linux_hosting/
  ├── export_database.py                           ← Database export script
  ├── test_migration.py                            ← Migration testing
  ├── DATABASE_MIGRATION.md                        ← Migration guide
  ├── MIGRATION_QUICK_REFERENCE.md                 ← Quick commands
  └── README_MIGRATION.md                          ← Migration overview

📄 EMAIL_NOTIFICATION_TOGGLE_INSTRUCTIONS.md        ← Developer guide
📄 DEPLOYMENT_UPDATE_GUIDE.md                       ← This file
```

### Step 2: Upload to Linux Server

**Using SCP (from Windows):**
```powershell
# Upload specific files
scp "d:\Asset tracker\assets\forms\asset_forms.py" user@server:/tmp/
scp "d:\Asset tracker\assets\services\notification_service.py" user@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\asset_form.html" user@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\free_ips.html" user@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\freed_systems.html" user@server:/tmp/

# Or upload entire zip
scp "d:\asset_tracker_update.zip" user@server:/tmp/
```

**Using FTP/SFTP:**
- Use FileZilla or WinSCP
- Upload files to `/tmp/` directory on server

### Step 3: Apply Changes on Linux Server

SSH into your server:

```bash
# Navigate to temp directory
cd /tmp

# If using zip
unzip asset_tracker_update.zip

# Backup current files (important!)
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py /var/www/asset_tracker/assets/forms/asset_forms.py.bak
sudo cp /var/www/asset_tracker/assets/services/notification_service.py /var/www/asset_tracker/assets/services/notification_service.py.bak

# Copy files to application directory
sudo cp -r assets/* /var/www/asset_tracker/assets/
sudo cp -r linux_hosting/* /var/www/asset_tracker/linux_hosting/

# Set permissions
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker

# Activate virtual environment
cd /var/www/asset_tracker
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput

# Restart application
sudo systemctl restart asset_tracker

# Check status
sudo systemctl status asset_tracker
```

---

## 🔍 Verification Steps

### 1. Check Application is Running

```bash
sudo systemctl status asset_tracker
# Should show: active (running)
```

### 2. Check Logs

```bash
# Application logs
sudo journalctl -u asset_tracker -n 50

# Nginx logs
sudo tail -f /var/log/nginx/asset_tracker_error.log
```

### 3. Test in Browser

1. **Visit your domain** (e.g., https://yourserver.com)
2. **Login** with admin credentials
3. **Test Email Toggle:**
   - Go to any asset edit page
   - Scroll to bottom
   - Verify checkbox is visible: "☑ Send Email Notification"
4. **Test IP Series Filter:**
   - Go to Free IP page
   - Verify filter buttons at top: [192.168.10.x] [192.168.70.x] etc.
   - Click a button, verify filtering works
5. **Test Freed Systems:**
   - Go to Freed Systems page
   - Verify "Issues" column is removed
   - Verify Action buttons are visible

---

## 🐛 Troubleshooting

### Issue: Changes Not Visible

**Solution 1: Clear Django Cache**
```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --clear --noinput
sudo systemctl restart asset_tracker
```

**Solution 2: Hard Reload Browser**
- Press `Ctrl + Shift + R` (Chrome/Firefox)
- Or clear browser cache

### Issue: 502 Bad Gateway

**Check Gunicorn:**
```bash
sudo systemctl status asset_tracker
sudo journalctl -u asset_tracker -n 100
```

**Restart Services:**
```bash
sudo systemctl restart asset_tracker
sudo systemctl restart nginx
```

### Issue: Static Files Not Loading

```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --noinput
sudo chown -R www-data:www-data /var/www/asset_tracker/staticfiles
sudo systemctl restart nginx
```

### Issue: Permission Denied

```bash
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

---

## 📝 Rollback Procedure

If something goes wrong:

```bash
# Stop application
sudo systemctl stop asset_tracker

# Restore backup files
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py.bak /var/www/asset_tracker/assets/forms/asset_forms.py
sudo cp /var/www/asset_tracker/assets/services/notification_service.py.bak /var/www/asset_tracker/assets/services/notification_service.py

# Restart
sudo systemctl start asset_tracker
```

---

## 📊 Deployment Checklist

### Pre-Deployment:
- [ ] Backup current files on server
- [ ] Commit changes to Git (if using)
- [ ] Test changes on Windows development server
- [ ] Note down current working state

### Deployment:
- [ ] Upload/pull changes to server
- [ ] Set correct permissions
- [ ] Collect static files
- [ ] Restart application services

### Post-Deployment:
- [ ] Check application status
- [ ] Review logs for errors
- [ ] Test email toggle checkbox
- [ ] Test IP series filter
- [ ] Test freed systems page
- [ ] Verify all features work

### If Issues:
- [ ] Check error logs
- [ ] Verify file permissions
- [ ] Restart services
- [ ] Rollback if necessary

---

## 🎯 Summary Commands (Git Method)

### On Windows:
```powershell
cd "d:\Asset tracker"
git add .
git commit -m "Recent updates"
git push origin main
```

### On Linux Server:
```bash
cd /var/www/asset_tracker
git pull origin main
source venv/bin/activate
python manage.py collectstatic --noinput
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

---

## 📞 Quick Reference

### Files Changed:
- `assets/forms/asset_forms.py` - Added send_notification field
- `assets/services/notification_service.py` - Added skip_notification parameter
- `assets/templates/assets/asset_form.html` - Added checkbox
- `assets/templates/assets/free_ips.html` - Added IP series filter
- `assets/templates/assets/freed_systems.html` - Removed Issues column

### Services to Restart:
- `sudo systemctl restart asset_tracker` (Gunicorn)
- `sudo systemctl restart nginx` (if needed)

### Logs to Check:
- `sudo journalctl -u asset_tracker -n 50`
- `sudo tail -f /var/log/nginx/asset_tracker_error.log`

---

## ⚠️ Important Notes

1. **Email Notifications:** Currently disabled in code (return statement). You'll need to enable them after deployment if needed.

2. **No Database Changes:** These updates don't require migrations, just code deployment.

3. **Static Files:** Run `collectstatic` to ensure CSS/JS changes are applied.

4. **Testing:** Test all features after deployment before enabling email notifications.

5. **Backup:** Always backup before deploying to production.

---

## 🎉 Success Indicators

After deployment, you should see:
- ✅ Email toggle checkbox in asset forms
- ✅ IP series filter buttons on Free IP page
- ✅ Freed Systems page without Issues column
- ✅ Action buttons visible in Freed Systems
- ✅ No errors in application logs

---

**Need help?** Check the troubleshooting section or review the logs.

**Last Updated:** December 2024  
**For:** Asset Tracker Django Application

