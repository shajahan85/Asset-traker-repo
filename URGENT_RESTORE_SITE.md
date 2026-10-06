# URGENT - RESTORE SITE NOW

**Error:** "This site can't be reached"  
**Meaning:** Django has crashed or stopped running

---

## LINUX TEAM - RUN THESE COMMANDS IMMEDIATELY:

### Command 1: Check if Django is running

```bash
sudo systemctl status asset_tracker
```

**You will see one of these:**

- `Active: active (running)` → Django is running but there's a network issue
- `Active: inactive (dead)` → Django is stopped, need to start it
- `Active: failed` → Django crashed, need to fix and restart

---

### Command 2: Restart Django NOW

```bash
sudo systemctl restart asset_tracker
```

Wait 5 seconds, then run:

```bash
sudo systemctl status asset_tracker
```

**What you should see:**
- Green text saying `Active: active (running)` → GOOD, site should work now
- Red text saying `failed` → Django is crashing, move to Command 3

---

### Command 3: If Django is failing to start, check the error log

```bash
sudo journalctl -u asset_tracker -n 100 --no-pager
```

**Send us the last 50 lines** - we'll see exactly why Django is crashing.

---

## MOST LIKELY CAUSE:

**The asset_forms.py file we uploaded has a syntax error.**

### Quick Fix - Restore the backup file:

```bash
# Go to the forms directory
cd /var/www/asset_tracker/assets/forms/

# Backup the broken file
sudo cp asset_forms.py asset_forms.py.broken_$(date +%Y%m%d_%H%M%S)

# Find and restore the previous working version
sudo ls -lt asset_forms.py* | head -10

# Look for a file like "asset_forms.py.backup" or "asset_forms.py.20260203"
# Then copy it back:
sudo cp asset_forms.py.backup asset_forms.py

# Or if no backup exists, restore from the original code folder
sudo cp /var/www/asset_tracker_original_backup/assets/forms/asset_forms.py asset_forms.py

# Restart Django
sudo systemctl restart asset_tracker

# Check status
sudo systemctl status asset_tracker
```

---

## ALTERNATIVE: If you can't find a backup

**Restore from your Windows development folder:**

1. In your Windows system, go to: `d:\Asset tracker\ORIGINAL_WORKING_FILE\`
2. Copy the `asset_forms.py` file from there
3. Upload it to the server at: `/var/www/asset_tracker/assets/forms/asset_forms.py`
4. Restart Django:

```bash
sudo systemctl restart asset_tracker
```

---

## AFTER RESTORING:

1. **Test if site loads** - try to open the homepage
2. **Don't try to edit BIDC1326 yet** - that will still freeze
3. **The site should at least load** - we'll fix the freeze issue separately

---

## WHAT TO SEND US:

Please run these commands and send us the output:

```bash
# Command 1
sudo systemctl status asset_tracker

# Command 2
sudo journalctl -u asset_tracker -n 50 --no-pager | tail -30

# Command 3
cd /var/www/asset_tracker/assets/forms/
ls -lh asset_forms.py*
```

---

## SUMMARY OF WHAT TO DO RIGHT NOW:

1. ✅ Run `sudo systemctl restart asset_tracker`
2. ✅ Check if site loads now
3. ✅ If site still doesn't load, send us the output of `sudo journalctl -u asset_tracker -n 50`
4. ✅ If Django won't start, restore the backup asset_forms.py file

---

**TIME IS CRITICAL - GET THE SITE BACK UP FIRST, THEN WE'LL FIX THE FREEZE ISSUE!**
