# Troubleshooting - Why Changes Are Not Visible

**Issue:** Deployed files but changes not appearing  
**Date:** September 16, 2026

---

## 🔍 Step-by-Step Diagnosis

Run these commands on the Linux server to find the problem:

---

### Step 1: Check if Files Were Deployed

```bash
# Check if bug fix is deployed
grep -n "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py

# Expected output:
# 10:def get_filtered_free_ips(include_current_ip_id=None, limit=30):

# If NOT found → Files NOT deployed or wrong path
```

**If files not found:**
```bash
# Find correct path
find /var -name "asset_tracker" -type d 2>/dev/null

# Or check where Django is running from
ps aux | grep manage.py
```

---

### Step 2: Check if CSS Files Were Deployed

```bash
# Check if CSS file exists
ls -la /var/www/asset_tracker/assets/static/assets/css/styles.css

# Check if it has the fix
grep "max-height.*70vh" /var/www/asset_tracker/assets/static/assets/css/styles.css

# Expected: Should find "max-height: 70vh"
```

**If CSS not found:**
```bash
# CSS might be in different location
find /var/www/asset_tracker -name "styles.css" -type f
```

---

### Step 3: Check if Static Files Were Collected

```bash
# Check staticfiles directory
ls -la /var/www/asset_tracker/staticfiles/assets/css/

# Should show:
# styles.css (with recent date/time)
# mobile.css (with recent date/time)

# Check if CSS has the fix
grep "max-height.*70vh" /var/www/asset_tracker/staticfiles/assets/css/styles.css
```

**If staticfiles empty or old:**
```bash
# Recollect static files
cd /var/www/asset_tracker
source venv/bin/activate
python manage.py collectstatic --clear --noinput
```

---

### Step 4: Check if Service Was Restarted

```bash
# Check when service was last restarted
sudo systemctl status asset_tracker | grep "Active:"

# If restart was more than 1 hour ago, files might be deployed but service not restarted
```

**Restart service:**
```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

---

### Step 5: Check if Nginx Was Restarted

```bash
# Check nginx status
sudo systemctl status nginx | grep "Active:"

# Restart nginx
sudo systemctl restart nginx
sudo systemctl status nginx
```

---

### Step 6: Check Permissions

```bash
# Check file ownership
ls -la /var/www/asset_tracker/assets/forms/asset_forms.py

# Should show: www-data www-data

# If wrong ownership:
sudo chown -R www-data:www-data /var/www/asset_tracker/assets
sudo chmod -R 755 /var/www/asset_tracker/assets
```

---

### Step 7: Check for Errors in Logs

```bash
# Check Django logs
sudo journalctl -u asset_tracker -n 100 | grep -i error

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Django application logs (if configured)
sudo tail -f /var/www/asset_tracker/logs/django.log 2>/dev/null
```

---

## 🎯 Common Problems & Solutions

### Problem 1: Files Deployed But Changes Not Visible

**Cause:** Browser cache or static files not collected

**Solution:**
```bash
# On server
python manage.py collectstatic --clear --noinput
sudo systemctl restart nginx

# On browser
# Press Ctrl + Shift + Delete (clear all cache)
# Or Ctrl + F5 (hard refresh)
# Or try incognito/private window
```

---

### Problem 2: Horizontal Scroll Still at Bottom

**Cause:** CSS not loaded or browser cache

**Solution:**
```bash
# 1. Verify CSS collected
ls -la /var/www/asset_tracker/staticfiles/assets/css/styles.css

# 2. Check CSS content
grep "max-height.*70vh" /var/www/asset_tracker/staticfiles/assets/css/styles.css

# 3. If missing, recollect
python manage.py collectstatic --clear --noinput

# 4. Restart nginx
sudo systemctl restart nginx

# 5. Clear browser cache completely
```

---

### Problem 3: Page Still Freezes

**Cause:** Bug fix not deployed or Python code not reloaded

**Solution:**
```bash
# 1. Check if fix is in source code
grep "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py

# 2. If not found, files not deployed correctly
# Deploy again:
cd /tmp/COMPLETE_DEPLOYMENT
sudo cp assets/forms/asset_forms.py /var/www/asset_tracker/assets/forms/
sudo chown www-data:www-data /var/www/asset_tracker/assets/forms/asset_forms.py

# 3. Restart Django
sudo systemctl restart asset_tracker

# 4. Check logs for errors
sudo journalctl -u asset_tracker -n 50
```

---

### Problem 4: Server Controllers Not Showing

**Cause:** Views or URLs not deployed

**Solution:**
```bash
# Check if views file exists
ls -la /var/www/asset_tracker/assets/views_server_controller.py

# Check if URLs are configured
grep "server-controllers" /var/www/asset_tracker/assets/urls.py

# If missing, deploy:
sudo cp assets/views_server_controller.py /var/www/asset_tracker/assets/
sudo systemctl restart asset_tracker
```

---

## 🔧 Nuclear Option: Complete Redeployment

If nothing else works, do a complete redeployment:

```bash
# 1. Stop services
sudo systemctl stop asset_tracker
sudo systemctl stop nginx

# 2. Backup everything
sudo cp -r /var/www/asset_tracker/assets /var/www/asset_tracker/assets.backup.$(date +%Y%m%d_%H%M%S)

# 3. Deploy all files fresh
cd /tmp/COMPLETE_DEPLOYMENT
sudo cp -r assets/* /var/www/asset_tracker/assets/

# 4. Fix permissions
sudo chown -R www-data:www-data /var/www/asset_tracker/assets
sudo chmod -R 755 /var/www/asset_tracker/assets

# 5. Clear and recollect static files
cd /var/www/asset_tracker
source venv/bin/activate
rm -rf staticfiles/assets/
python manage.py collectstatic --clear --noinput

# 6. Restart services
sudo systemctl start asset_tracker
sudo systemctl start nginx

# 7. Check status
sudo systemctl status asset_tracker
sudo systemctl status nginx

# 8. Check logs
sudo journalctl -u asset_tracker -n 50
```

---

## ✅ Final Verification Commands

After deployment, run these to verify everything:

```bash
# 1. Check bug fix deployed
grep "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py && echo "✅ Bug fix found" || echo "❌ Bug fix NOT found"

# 2. Check CSS deployed
grep "max-height.*70vh" /var/www/asset_tracker/assets/static/assets/css/styles.css && echo "✅ CSS source found" || echo "❌ CSS NOT found"

# 3. Check CSS collected
grep "max-height.*70vh" /var/www/asset_tracker/staticfiles/assets/css/styles.css && echo "✅ CSS collected" || echo "❌ CSS NOT collected"

# 4. Check service running
systemctl is-active asset_tracker && echo "✅ Django running" || echo "❌ Django NOT running"

# 5. Check nginx running
systemctl is-active nginx && echo "✅ Nginx running" || echo "❌ Nginx NOT running"

# 6. Check for errors
sudo journalctl -u asset_tracker -n 20 --no-pager | grep -i error && echo "⚠️ Errors found" || echo "✅ No errors"
```

---

## 📞 Contact Developer

If issues persist after following all steps above, provide this information:

```bash
# Run this and send output:
echo "=== System Info ===" && \
echo "Django Path: $(which python)" && \
echo "Active: $(systemctl is-active asset_tracker)" && \
echo "" && \
echo "=== Bug Fix Check ===" && \
grep -n "limit=30" /var/www/asset_tracker/assets/forms/asset_forms.py && \
echo "" && \
echo "=== CSS Check ===" && \
ls -la /var/www/asset_tracker/staticfiles/assets/css/ && \
echo "" && \
echo "=== Recent Logs ===" && \
sudo journalctl -u asset_tracker -n 10 --no-pager
```

---

**Created:** September 16, 2026  
**For:** Linux Deployment Team  
**Issue:** Changes not appearing after deployment
