# Files to Upload to Linux Server

**Last Updated:** September 9, 2026  
**Purpose:** Update production server with recent changes

---

## 📦 Complete File List for Linux Team

### Python Files (Backend)

```
1. assets/views.py
   Location: deployment_package/assets/views.py
   Purpose: Main views (email notifications with employee code)

2. assets/views_server_controller.py
   Location: deployment_package/assets/views_server_controller.py
   Purpose: Server Controller views with IP filter

3. assets/forms/asset_forms.py
   Location: deployment_package/assets/forms/asset_forms.py
   Purpose: Asset form with email notification checkbox

4. assets/services/asset_service.py
   Location: deployment_package/assets/services/asset_service.py
   Purpose: Asset service operations

5. assets/services/notification_service.py
   Location: deployment_package/assets/services/notification_service.py
   Purpose: Email notification service (skip logic)
```

---

### HTML Templates (Frontend)

```
6. assets/templates/assets/asset_form.html
   Location: deployment_package/assets/templates/assets/asset_form.html
   Purpose: Asset edit form with email checkbox

7. assets/templates/assets/freed_systems.html
   Location: deployment_package/assets/templates/assets/freed_systems.html
   Purpose: Freed systems page (SC badge, removed Issues column)

8. assets/templates/assets/free_ips.html
   Location: deployment_package/assets/templates/assets/free_ips.html
   Purpose: Free IPs page with IP series filters

9. assets/templates/assets/server_controller_list.html
   Location: deployment_package/assets/templates/assets/server_controller_list.html
   Purpose: Server Controllers main page with IP filter

10. assets/templates/assets/server_controller_form.html
    Location: deployment_package/assets/templates/assets/server_controller_form.html
    Purpose: Server Controller edit form

11. assets/templates/assets/server_controller_reassign.html
    Location: deployment_package/assets/templates/assets/server_controller_reassign.html
    Purpose: Server Controller reassign form
```

---

## 📂 Directory Structure on Server

The Linux team should place files maintaining this structure:

```
/var/www/asset_tracker/   (or your server path)
├── assets/
│   ├── views.py                               ← Replace
│   ├── views_server_controller.py             ← Replace
│   ├── forms/
│   │   └── asset_forms.py                     ← Replace
│   ├── services/
│   │   ├── asset_service.py                   ← Replace
│   │   └── notification_service.py            ← Replace
│   └── templates/
│       └── assets/
│           ├── asset_form.html                ← Replace
│           ├── freed_systems.html             ← Replace
│           ├── free_ips.html                  ← Replace
│           ├── server_controller_list.html    ← Replace
│           ├── server_controller_form.html    ← Replace
│           └── server_controller_reassign.html ← Replace
```

---

## 🚀 Quick Upload Command

Share this with your Linux team:

### Option 1: Upload entire deployment_package folder

```bash
# From Windows (PowerShell):
scp -r "d:\Asset tracker\deployment_package" username@server-ip:/tmp/

# Then on Linux server:
ssh username@server-ip
cd /tmp/deployment_package
sudo cp -r assets/* /var/www/asset_tracker/assets/
```

### Option 2: Upload specific files (if they prefer)

```bash
# From Windows (PowerShell):
cd "d:\Asset tracker\deployment_package"

# Upload Python files
scp assets/views.py username@server-ip:/tmp/
scp assets/views_server_controller.py username@server-ip:/tmp/
scp assets/forms/asset_forms.py username@server-ip:/tmp/
scp assets/services/asset_service.py username@server-ip:/tmp/
scp assets/services/notification_service.py username@server-ip:/tmp/

# Upload templates
scp assets/templates/assets/asset_form.html username@server-ip:/tmp/
scp assets/templates/assets/freed_systems.html username@server-ip:/tmp/
scp assets/templates/assets/free_ips.html username@server-ip:/tmp/
scp assets/templates/assets/server_controller_list.html username@server-ip:/tmp/
scp assets/templates/assets/server_controller_form.html username@server-ip:/tmp/
scp assets/templates/assets/server_controller_reassign.html username@server-ip:/tmp/
```

---

## ⚙️ Linux Team Steps (After Upload)

### 1. Backup Current Files

```bash
# Create backup directory
sudo mkdir -p /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)

# Backup files
sudo cp /var/www/asset_tracker/assets/views.py \
        /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/views_server_controller.py \
        /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true
# ... backup other files
```

### 2. Copy New Files

```bash
# Copy from /tmp to application directory
cd /tmp/deployment_package

sudo cp assets/views.py /var/www/asset_tracker/assets/
sudo cp assets/views_server_controller.py /var/www/asset_tracker/assets/
sudo cp assets/forms/asset_forms.py /var/www/asset_tracker/assets/forms/
sudo cp assets/services/asset_service.py /var/www/asset_tracker/assets/services/
sudo cp assets/services/notification_service.py /var/www/asset_tracker/assets/services/

sudo cp assets/templates/assets/asset_form.html /var/www/asset_tracker/assets/templates/assets/
sudo cp assets/templates/assets/freed_systems.html /var/www/asset_tracker/assets/templates/assets/
sudo cp assets/templates/assets/free_ips.html /var/www/asset_tracker/assets/templates/assets/
sudo cp assets/templates/assets/server_controller_list.html /var/www/asset_tracker/assets/templates/assets/
sudo cp assets/templates/assets/server_controller_form.html /var/www/asset_tracker/assets/templates/assets/
sudo cp assets/templates/assets/server_controller_reassign.html /var/www/asset_tracker/assets/templates/assets/
```

### 3. Set Permissions

```bash
# Set correct ownership
sudo chown -R www-data:www-data /var/www/asset_tracker/assets

# Set correct permissions
sudo chmod -R 755 /var/www/asset_tracker/assets
```

### 4. Collect Static Files

```bash
# Activate virtual environment
cd /var/www/asset_tracker
source venv/bin/activate

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Restart Application

```bash
# Restart Django application
sudo systemctl restart asset_tracker

# Check status
sudo systemctl status asset_tracker

# Check logs
sudo journalctl -u asset_tracker -n 50
```

---

## ✅ Verification Steps

After deployment, verify:

```bash
# 1. Check service is running
sudo systemctl status asset_tracker

# 2. Check for errors in logs
sudo journalctl -u asset_tracker -n 100 | grep -i error

# 3. Test in browser
curl http://your-server/assets/

# 4. Check Server Controllers page
curl http://your-server/assets/server-controllers/
```

---

## 🎯 What Changed - Summary for Linux Team

### New Features:
1. ✅ **Server Controllers Page** - New page at /assets/server-controllers/
2. ✅ **IP Filter with VM Detection** - Smart filtering on SC page
3. ✅ **Email Notification Toggle** - Checkbox to control emails
4. ✅ **IP Series Filters** - Quick filters on Free IP page
5. ✅ **SC Badge** - Yellow badge on freed systems
6. ✅ **Table Improvements** - Fixed freed systems layout

### Technical:
- **No database migrations needed** (code-only changes)
- **No new dependencies** (uses existing packages)
- **Backward compatible** (won't break existing functionality)
- **No configuration changes** (settings.py unchanged)

---

## 🚨 Important Notes for Linux Team

### ⚠️ MUST DO:
1. ✅ **Backup files before replacing**
2. ✅ **Set correct permissions after copying**
3. ✅ **Run collectstatic command**
4. ✅ **Restart the application service**
5. ✅ **Check logs for errors**

### ❌ DO NOT:
- ❌ Run migrations (not needed)
- ❌ Modify settings.py
- ❌ Change database
- ❌ Skip backup step

### 💡 OPTIONAL:
- Clear Nginx cache if using reverse proxy
- Restart Nginx if static files not loading

---

## 📞 Troubleshooting

### If service won't start:
```bash
# Check for Python syntax errors
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py check

# Check detailed error
sudo journalctl -u asset_tracker -n 200
```

### If pages show 404:
```bash
# Verify files exist
ls -la /var/www/asset_tracker/assets/views_server_controller.py
ls -la /var/www/asset_tracker/assets/templates/assets/server_controller_list.html

# Check URLs configured
grep -r "server-controllers" /var/www/asset_tracker/assets/urls.py
```

### If templates not found:
```bash
# Verify template paths
ls -la /var/www/asset_tracker/assets/templates/assets/

# Check permissions
ls -la /var/www/asset_tracker/assets/templates/
```

### If static files not loading:
```bash
# Recollect static files
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --clear --noinput

# Restart Nginx
sudo systemctl restart nginx
```

---

## 📋 Rollback Procedure (If Needed)

If something goes wrong:

```bash
# Stop application
sudo systemctl stop asset_tracker

# Restore from backup (use actual timestamp)
BACKUP_DIR="/var/www/asset_tracker/backups/YYYYMMDD_HHMMSS"
sudo cp $BACKUP_DIR/* /var/www/asset_tracker/assets/

# Restart
sudo systemctl start asset_tracker
sudo systemctl status asset_tracker
```

---

## 📊 Expected Results After Deployment

### New URLs Available:
- `/assets/server-controllers/` - Main SC page
- `/assets/server-controllers/<id>/edit/` - Edit SC
- `/assets/server-controllers/<id>/free/` - Free SC
- `/assets/server-controllers/<id>/reassign/` - Reassign SC
- `/assets/server-controllers/export/` - Export SC to Excel

### New Features Visible:
- Server Controllers menu item (staff only)
- IP filter on SC page with VM detection
- Email checkbox on asset forms
- IP series buttons on Free IP page
- SC badge on freed systems
- Updated freed systems table

---

## 📞 Contact

If Linux team has questions:
- Check documentation in deployment_package/
- Review TODAYS_CHANGES.md for detailed changes
- See DEPLOYMENT_UPDATE_GUIDE.md for full instructions

---

**Prepared by:** Asset Tracker Development Team  
**Date:** September 9, 2026  
**Package Version:** 2.1  
**Status:** ✅ Ready for Production Deployment
