# Server Update - Files to Upload

Complete list of files that need to be uploaded to your Linux server.

---

## 📋 Files to Upload (7 Files Total)

### 1. **Forms** (1 file)
```
Windows Location:
d:\Asset tracker\assets\forms\asset_forms.py

Linux Server Location:
/var/www/asset_tracker/assets/forms/asset_forms.py

Changes: Added send_notification checkbox field
```

### 2. **Services** (2 files)
```
Windows Location:
d:\Asset tracker\assets\services\notification_service.py

Linux Server Location:
/var/www/asset_tracker/assets/services/notification_service.py

Changes: Added skip_notification parameter to all notification methods
```

```
Windows Location:
d:\Asset tracker\assets\services\asset_service.py

Linux Server Location:
/var/www/asset_tracker/assets/services/asset_service.py

Changes: Added skip_notification parameter to create_asset and update_asset methods
```

### 3. **Views** (1 file)
```
Windows Location:
d:\Asset tracker\assets\views.py

Linux Server Location:
/var/www/asset_tracker/assets/views.py

Changes: Read checkbox value and pass to service in create/update views
```

### 4. **Templates** (3 files)
```
Windows Location:
d:\Asset tracker\assets\templates\assets\asset_form.html

Linux Server Location:
/var/www/asset_tracker/assets/templates/assets/asset_form.html

Changes: Added email notification checkbox before submit button
```

```
Windows Location:
d:\Asset tracker\assets\templates\assets\free_ips.html

Linux Server Location:
/var/www/asset_tracker/assets/templates/assets/free_ips.html

Changes: Added IP series quick filter buttons
```

```
Windows Location:
d:\Asset tracker\assets\templates\assets\freed_systems.html

Linux Server Location:
/var/www/asset_tracker/assets/templates/assets/freed_systems.html

Changes: Removed Issues column, fixed Actions column visibility
```

---

## 📦 Quick Copy Commands (Windows)

Copy these files to a single folder for easy upload:

```powershell
# Create upload folder
New-Item -ItemType Directory -Path "d:\Asset tracker\server_update" -Force

# Copy all files maintaining structure
$files = @(
    "assets\forms\asset_forms.py",
    "assets\services\notification_service.py",
    "assets\services\asset_service.py",
    "assets\views.py",
    "assets\templates\assets\asset_form.html",
    "assets\templates\assets\free_ips.html",
    "assets\templates\assets\freed_systems.html"
)

foreach ($file in $files) {
    $source = "d:\Asset tracker\$file"
    $dest = "d:\Asset tracker\server_update\$file"
    $destDir = Split-Path $dest -Parent
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    Copy-Item $source $dest -Force
}

Write-Output "Files copied to: d:\Asset tracker\server_update\"
```

---

## 🚀 Deployment Methods

### Method 1: Using Deployment Package (Easiest)

The `deployment_package` folder already has ALL these files ready!

```powershell
# Upload entire deployment_package folder
scp -r "d:\Asset tracker\deployment_package" username@server:/tmp/

# Then on Linux server:
cd /tmp/deployment_package
bash DEPLOY.sh
```

### Method 2: Manual File Upload

**Using SCP:**
```powershell
# Upload files one by one
scp "d:\Asset tracker\assets\forms\asset_forms.py" username@server:/tmp/
scp "d:\Asset tracker\assets\services\notification_service.py" username@server:/tmp/
scp "d:\Asset tracker\assets\services\asset_service.py" username@server:/tmp/
scp "d:\Asset tracker\assets\views.py" username@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\asset_form.html" username@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\free_ips.html" username@server:/tmp/
scp "d:\Asset tracker\assets\templates\assets\freed_systems.html" username@server:/tmp/
```

**Using FileZilla/WinSCP:**
- Upload these 7 files to `/tmp/` on your server

---

## 🔧 Installation on Linux Server

### Step 1: Backup Current Files

```bash
# Create backup directory
sudo mkdir -p /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)

# Backup files
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/services/notification_service.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/services/asset_service.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/views.py /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
sudo cp /var/www/asset_tracker/assets/templates/assets/*.html /var/www/asset_tracker/backups/$(date +%Y%m%d_%H%M%S)/
```

### Step 2: Copy New Files

```bash
# Navigate to temp directory
cd /tmp

# Copy files to application directory
sudo cp asset_forms.py /var/www/asset_tracker/assets/forms/
sudo cp notification_service.py /var/www/asset_tracker/assets/services/
sudo cp asset_service.py /var/www/asset_tracker/assets/services/
sudo cp views.py /var/www/asset_tracker/assets/
sudo cp asset_form.html /var/www/asset_tracker/assets/templates/assets/
sudo cp free_ips.html /var/www/asset_tracker/assets/templates/assets/
sudo cp freed_systems.html /var/www/asset_tracker/assets/templates/assets/
```

### Step 3: Set Permissions

```bash
sudo chown -R www-data:www-data /var/www/asset_tracker/assets
sudo chmod -R 755 /var/www/asset_tracker/assets
```

### Step 4: Collect Static Files

```bash
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --noinput
```

### Step 5: Restart Services

```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

---

## ✅ Verification Checklist

After deployment, verify these features work:

### 1. Email Toggle Checkbox
- [ ] Go to any asset edit page
- [ ] See checkbox: "☑ Send Email Notification"
- [ ] Edit asset with checkbox CHECKED → Email sent
- [ ] Edit asset with checkbox UNCHECKED → No email sent

### 2. IP Series Filter
- [ ] Go to Free IP page
- [ ] See filter buttons at top: [192.168.10.x] [192.168.70.x] etc.
- [ ] Click a button → Shows only that series
- [ ] Click "Show All" → Shows all IPs

### 3. Freed Systems Page
- [ ] Go to Freed Systems page
- [ ] "Issues" column is NOT visible
- [ ] Action buttons ARE visible on the right
- [ ] Can click Edit, Reassign, Scrap, Delete buttons

### 4. Employee Code in Emails
- [ ] Create or update asset with checkbox CHECKED
- [ ] Check email received
- [ ] Verify "Employee Code: XXX" line is present

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

### Server Not Starting

```bash
# Check logs
sudo journalctl -u asset_tracker -n 50

# Check for syntax errors
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py check
```

---

## 📊 File Summary Table

| File | Size | Purpose |
|------|------|---------|
| asset_forms.py | ~40 KB | Email checkbox field |
| notification_service.py | ~8 KB | Skip notification logic |
| asset_service.py | ~30 KB | Pass skip parameter |
| views.py | ~90 KB | Read checkbox value |
| asset_form.html | ~48 KB | Display checkbox |
| free_ips.html | ~36 KB | IP series filter |
| freed_systems.html | ~7 KB | Fixed Actions column |
| **TOTAL** | **~259 KB** | **7 files** |

---

## 🔄 Rollback Procedure

If something goes wrong:

```bash
# Stop application
sudo systemctl stop asset_tracker

# Restore from backup (use actual timestamp from Step 1)
BACKUP_DIR="/var/www/asset_tracker/backups/YYYYMMDD_HHMMSS"
sudo cp $BACKUP_DIR/asset_forms.py /var/www/asset_tracker/assets/forms/
sudo cp $BACKUP_DIR/notification_service.py /var/www/asset_tracker/assets/services/
sudo cp $BACKUP_DIR/asset_service.py /var/www/asset_tracker/assets/services/
sudo cp $BACKUP_DIR/views.py /var/www/asset_tracker/assets/
sudo cp $BACKUP_DIR/*.html /var/www/asset_tracker/assets/templates/assets/

# Restart
sudo systemctl start asset_tracker
```

---

## 📞 Quick Reference

### Upload Command (All at once):
```powershell
scp -r "d:\Asset tracker\deployment_package" username@server:/tmp/
```

### Deploy Command (On server):
```bash
cd /tmp/deployment_package && bash DEPLOY.sh
```

### Restart Command:
```bash
sudo systemctl restart asset_tracker
```

### Check Status:
```bash
sudo systemctl status asset_tracker
```

---

## ⚠️ Important Notes

1. **No Database Migrations Needed** - These are code-only changes
2. **Backup First** - Always backup before deploying
3. **Test After Deployment** - Verify all 4 features work
4. **Deployment Package Ready** - `d:\Asset tracker\deployment_package\` has everything

---

**Ready to Deploy?** 
1. Use the `deployment_package` folder (easiest)
2. Or manually upload these 7 files
3. Follow the Linux commands above
4. Test all features

**Need Help?** Check `DEPLOYMENT_UPDATE_GUIDE.md` in the project folder.

