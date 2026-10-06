# LINUX SERVER - FILE DEPLOYMENT INSTRUCTIONS

**Date:** September 24, 2026  
**File to upload:** `asset_forms.py`  
**Issue:** Fixes page freeze for Sankar (BIDC1326), Anjana (BIDC1544), Kharunnisa, and BIDC1569

---

## FILE TO UPLOAD

**Source file (Windows):**
```
d:\Asset tracker\LINUX_SERVER_UPLOAD\asset_forms.py
```

**Destination (Linux Server):**
```
/var/www/asset_tracker/assets/forms/asset_forms.py
```

---

## STEP-BY-STEP DEPLOYMENT

### Step 1: Backup Current File

Before uploading, backup the current file on the server:

```bash
cd /var/www/asset_tracker/assets/forms/
sudo cp asset_forms.py asset_forms.py.backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Upload the New File

**Option A - Using WinSCP:**
1. Open WinSCP
2. Connect to your Linux server
3. Navigate to: `/var/www/asset_tracker/assets/forms/`
4. Upload `asset_forms.py` from `d:\Asset tracker\LINUX_SERVER_UPLOAD\`
5. Overwrite the existing file

**Option B - Using FileZilla:**
1. Open FileZilla
2. Connect to your Linux server
3. Navigate to: `/var/www/asset_tracker/assets/forms/`
4. Drag and drop `asset_forms.py` from Windows to Linux
5. Confirm overwrite

**Option C - Using scp command (from Windows PowerShell):**
```powershell
scp "d:\Asset tracker\LINUX_SERVER_UPLOAD\asset_forms.py" username@server_ip:/tmp/asset_forms.py
```

Then on Linux server:
```bash
sudo mv /tmp/asset_forms.py /var/www/asset_tracker/assets/forms/asset_forms.py
sudo chown www-data:www-data /var/www/asset_tracker/assets/forms/asset_forms.py
sudo chmod 644 /var/www/asset_tracker/assets/forms/asset_forms.py
```

### Step 3: Verify File Uploaded Successfully

On Linux server, check if the file has the correct function:

```bash
grep -n "def get_filtered_free_ips" /var/www/asset_tracker/assets/forms/asset_forms.py
```

**Expected output:** Should show a line number (e.g., `10:def get_filtered_free_ips(include_current_ip_id=None, limit=None):`)

**If no output:** The file upload failed or wrong file uploaded.

### Step 4: Restart Django

```bash
sudo systemctl restart asset_tracker
```

Wait 5 seconds, then check status:

```bash
sudo systemctl status asset_tracker
```

**Expected:** Green text showing `Active: active (running)`

**If failed (red text):**
```bash
# Check error logs
sudo journalctl -u asset_tracker -n 50

# Restore backup if needed
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py.backup_* /var/www/asset_tracker/assets/forms/asset_forms.py
sudo systemctl restart asset_tracker
```

---

## WHAT THIS FILE FIXES

This updated `asset_forms.py` contains:

1. ✅ `get_filtered_free_ips()` function - was missing, causing Django to crash
2. ✅ IP query limit of 200 - prevents loading all IPs at once
3. ✅ Proper IP filtering logic - handles both managed and manual IPs correctly

**What it does NOT fix:**
- ❌ Database corruption (14+ IPs marked as free but assigned to assets)
- This requires SQL commands - see `COMPLETE_FIX_FOR_LINUX_TEAM.md`

---

## AFTER DEPLOYMENT

### Test 1: Check if site loads
- Open the website
- Login page should appear
- You should be able to log in

### Test 2: Check if freeze is fixed
**Note:** The freeze will STILL OCCUR until you run the SQL fix commands!

The file upload only fixes the crash. The freeze requires database repair.

---

## NEXT STEP

After successfully uploading this file and restarting Django:

**Run the SQL commands** from `COMPLETE_FIX_FOR_LINUX_TEAM.md` to fix the database corruption.

Only then will the freeze issue be resolved.

---

## FILE VERIFICATION

To verify this is the correct file, check these details:

```bash
# File should be about 35-40 KB
ls -lh /var/www/asset_tracker/assets/forms/asset_forms.py

# Should contain get_filtered_free_ips function
grep "def get_filtered_free_ips" /var/www/asset_tracker/assets/forms/asset_forms.py

# Should contain limit parameter
grep "limit=None" /var/www/asset_tracker/assets/forms/asset_forms.py
```

---

## ROLLBACK (If Something Goes Wrong)

If the new file causes issues:

```bash
# Restore backup
cd /var/www/asset_tracker/assets/forms/
sudo cp asset_forms.py.backup_* asset_forms.py

# Restart Django
sudo systemctl restart asset_tracker

# Verify site is working
sudo systemctl status asset_tracker
```

---

## SUMMARY CHECKLIST

- [ ] Backup created
- [ ] File uploaded to correct location
- [ ] File ownership correct (www-data:www-data)
- [ ] File permissions correct (644)
- [ ] Django restarted successfully
- [ ] Site loads (login page appears)
- [ ] Ready to run SQL fix commands

---

**Questions? Issues? Send back:**
1. Output of `systemctl status asset_tracker`
2. Output of `grep "def get_filtered_free_ips" /var/www/asset_tracker/assets/forms/asset_forms.py`
3. Any error messages from logs
