# Deployment Package - Asset Tracker Updates

This folder contains all files that need to be uploaded to your Linux server.

---

## 📦 Package Contents

### Changed Application Files:

```
deployment_package/
├── assets/
│   ├── forms/
│   │   └── asset_forms.py                    ← Email toggle checkbox
│   ├── services/
│   │   └── notification_service.py           ← Skip notification logic
│   ├── templates/
│   │   └── assets/
│   │       ├── asset_form.html              ← Checkbox in form
│   │       ├── free_ips.html                ← IP series filter
│   │       ├── freed_systems.html           ← Removed Issues column
│   │       ├── server_controller_list.html  ← SC main page (FIXED)
│   │       ├── server_controller_form.html  ← SC edit form (FIXED)
│   │       └── server_controller_reassign.html ← SC reassign form
│   ├── views.py                             ← Main views file
│   └── views_server_controller.py           ← SC views (FIXED)
│
├── DEPLOYMENT_UPDATE_GUIDE.md               ← Full deployment guide
├── EMAIL_NOTIFICATION_TOGGLE_INSTRUCTIONS.md ← Developer reference
├── SERVER_CONTROLLER_FIX.md                 ← HyperV VM bug fix
├── SERVER_CONTROLLER_IP_FILTER.md           ← IP filter feature (NEW)
└── README.md                                ← This file
```

---

## 🚨 IMPORTANT - Bug Fix Applied

**Issue Fixed:** Server Controllers page was showing AttributeError due to incorrect HyperV VM relationship name.

See **SERVER_CONTROLLER_FIX.md** for technical details.

**Status:** ✅ Fixed and tested - all files updated in this package

---

## 🚀 Quick Deployment Steps

### Step 1: Upload to Linux Server

**Using SCP (from Windows PowerShell):**
```powershell
# Upload entire folder
scp -r "d:\Asset tracker\deployment_package" username@your-server-ip:/tmp/
```

**Or using FileZilla/WinSCP:**
- Connect to your server
- Upload the entire `deployment_package` folder to `/tmp/`

---

### Step 2: Apply Changes on Linux Server

SSH into your server and run:

```bash
# Navigate to temp directory
cd /tmp/deployment_package

# Backup current files (IMPORTANT!)
sudo mkdir -p /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/services/notification_service.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/

# Copy new files to application
sudo cp -r assets/* /var/www/asset_tracker/assets/

# Set correct permissions
sudo chown -R www-data:www-data /var/www/asset_tracker/assets
sudo chmod -R 755 /var/www/asset_tracker/assets

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

## ✅ Verify Deployment

### 1. Check Application Status
```bash
sudo systemctl status asset_tracker
# Should show: active (running)
```

### 2. Check Logs for Errors
```bash
sudo journalctl -u asset_tracker -n 50
```

### 3. Test in Browser

Visit your server and test:

1. **Email Toggle:**
   - Edit any asset
   - Scroll to bottom
   - See: ☑ Send Email Notification

2. **IP Series Filter:**
   - Go to Free IP page
   - See filter buttons at top
   - Click to test filtering

3. **Freed Systems:**
   - Go to Freed Systems page
   - Issues column should be gone
   - Action buttons should be visible

---

## 📋 What's Updated

### Core Features:
1. ✅ **Email Notification Toggle** - Checkbox to control email sending per-save
2. ✅ **IP Series Quick Filter** - Quick filter buttons on Free IP page (192.168.10.x, 70.x, 11.x, 50.x)
3. ✅ **Freed Systems Table Fix** - Removed Issues column, fixed Actions visibility
4. ✅ **Employee Code in Emails** - Added to all email notifications

### Server Controller Feature (NEW):
5. ✅ **Server Controllers Page** - Manage 192.168.50.x range systems
6. ✅ **IP Filter with VM Detection** - Smart filtering: Enter VM IP → shows host + all VMs
7. ✅ **Enhanced VM Display** - Shows all VMs with IPs, highlights filtered VM
8. ✅ **SC Badge Display** - Yellow circle badge in Freed Systems
9. ✅ **Free/Reassign/Scrap** - Full workflow for server controllers
10. ✅ **HyperV VM Integration** - Display VMs hosted on each server controller

### Bug Fixes:
11. ✅ **HyperV VM Relationship Fix** - Corrected `hyperv_vms` → `hosted_vms` (see SERVER_CONTROLLER_FIX.md)

---

## 🔄 Rollback (If Needed)

If something goes wrong:

```bash
# Stop application
sudo systemctl stop asset_tracker

# Restore from backup (use actual timestamp)
sudo cp /var/www/asset_tracker/backups/YYYYMMDD_HHMMSS/* /var/www/asset_tracker/assets/forms/
sudo cp /var/www/asset_tracker/backups/YYYYMMDD_HHMMSS/* /var/www/asset_tracker/assets/services/

# Restart
sudo systemctl start asset_tracker
```

---

## 🐛 Troubleshooting

### Changes Not Visible
```bash
# Clear cache and restart
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --clear --noinput
sudo systemctl restart asset_tracker
sudo systemctl restart nginx
```

### Permission Errors
```bash
sudo chown -R www-data:www-data /var/www/asset_tracker
sudo chmod -R 755 /var/www/asset_tracker
```

### 502 Bad Gateway
```bash
# Check and restart services
sudo systemctl status asset_tracker
sudo systemctl restart asset_tracker
sudo systemctl restart nginx
```

---

## 📞 Support

For detailed instructions, see:
- **DEPLOYMENT_UPDATE_GUIDE.md** - Complete deployment guide
- **EMAIL_NOTIFICATION_TOGGLE_INSTRUCTIONS.md** - Developer reference

---

## ⚠️ Important Notes

1. **No Database Migrations Needed** - These are code-only changes
2. **Backup First** - Always backup before deploying
3. **Test After Deployment** - Verify all features work
4. **Email Currently Disabled** - Re-enable if needed after testing

---

**Package Created:** December 2024  
**For:** Asset Tracker Django Application  
**Version:** Recent Updates Package

