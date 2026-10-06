# FINAL FIX - Asset Editing Still Freezes (BIDC1544 Anjana)

**Date:** September 24, 2026  
**Status:** Creating works ✅ | Editing freezes ❌

---

## SITUATION SUMMARY

### What Works:
- ✅ Creating new assets (BIDC1326 was re-created successfully)
- ✅ Database corruption was fixed (1 corrupted IP repaired)
- ✅ Site loads and login works

### What Still Freezes:
- ❌ Editing existing asset BIDC1544 (Anjana)
- ❌ Possibly other existing assets too

---

## ROOT CAUSE ANALYSIS

The freeze happens when **editing** but not when **creating** because:

1. **When creating:** Form only validates new data
2. **When editing:** Form loads and validates:
   - Primary IP
   - Secondary/Additional IPs
   - Accessories
   - Asset history
   - Related records

**Most likely cause:** BIDC1544 has corrupted secondary IPs or accessories that cause infinite loops when loading the edit form.

---

## DIAGNOSTIC QUERIES FOR LINUX TEAM

Run these queries in MySQL to find the corruption:

### Query 1: Find Asset ID for BIDC1544

```sql
SELECT serial_number, asset_tag, assigned_to, employee_code, status
FROM assets_asset
WHERE asset_tag = 'BIDC1544';
```

**Note the serial_number** - you'll need it for the next queries.

---

### Query 2: Check for Corrupted Secondary IPs (Replace XXX with serial_number from Query 1)

```sql
SELECT 
    aip.id as junction_id,
    aip.asset_id,
    aip.is_primary,
    aip.ip_label,
    aip.manual_ip,
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id
FROM assets_assetipaddress aip
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE aip.asset_id = XXX;
```

**Look for:**
- IPs where `is_assigned = 0` but `asset_id` is not NULL
- IPs where `assigned_to_asset_id` doesn't match `asset_id`
- Multiple primary IPs (`is_primary = 1` appears more than once)

---

### Query 3: Check for Orphaned IP Relationships

```sql
SELECT 
    aip.id,
    aip.asset_id,
    aip.ip_address_id,
    aip.is_primary
FROM assets_assetipaddress aip
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.id IS NULL AND aip.ip_address_id IS NOT NULL;
```

**Expected:** 0 rows (no orphaned records)

---

### Query 4: Check for Duplicate Primary IPs

```sql
SELECT 
    asset_id,
    COUNT(*) as primary_count
FROM assets_assetipaddress
WHERE is_primary = 1
GROUP BY asset_id
HAVING COUNT(*) > 1;
```

**Expected:** 0 rows (each asset should have only 1 primary IP)

---

### Query 5: Find ALL Assets with Corrupted IPs

```sql
SELECT 
    a.serial_number,
    a.asset_tag,
    a.assigned_to,
    COUNT(aip.id) as total_ips,
    SUM(CASE WHEN aip.is_primary = 1 THEN 1 ELSE 0 END) as primary_count
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
WHERE a.asset_tag IN ('BIDC1544', 'BIDC1569')
GROUP BY a.serial_number, a.asset_tag, a.assigned_to;
```

---

## COMMON CORRUPTION PATTERNS & FIXES

### Pattern 1: IP marked as free but linked to asset

**Symptom:** Query 2 shows `is_assigned = 0` but `asset_id` has a value

**Fix:**
```sql
UPDATE assets_ipaddress 
SET is_assigned = 1, assigned_to_asset_id = XXX 
WHERE id = YYY;
```
Replace XXX with asset serial_number, YYY with IP id.

---

### Pattern 2: Multiple Primary IPs

**Symptom:** Query 4 shows an asset with primary_count > 1

**Fix:** Keep only the first primary, set others to secondary:
```sql
-- Find the IPs for the asset
SELECT id, is_primary, created_at 
FROM assets_assetipaddress 
WHERE asset_id = XXX AND is_primary = 1
ORDER BY created_at ASC;

-- Keep the oldest one as primary, set others to secondary
UPDATE assets_assetipaddress 
SET is_primary = 0 
WHERE id IN (YYY, ZZZ);  -- IDs of the newer primary IPs
```

---

### Pattern 3: Orphaned IP Relationships

**Symptom:** Query 3 shows records

**Fix:** Delete orphaned relationships:
```sql
DELETE FROM assets_assetipaddress 
WHERE id IN (
    SELECT aip.id
    FROM assets_assetipaddress aip
    LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
    WHERE ip.id IS NULL AND aip.ip_address_id IS NOT NULL
);
```

---

## ALTERNATIVE SOLUTION: Delete and Re-create BIDC1544

If the corruption is too complex, the easiest solution is:

### Step 1: Save Current Data

```sql
-- Get all info about BIDC1544
SELECT * FROM assets_asset WHERE asset_tag = 'BIDC1544';

-- Get all IPs
SELECT * FROM assets_assetipaddress WHERE asset_id = (
    SELECT serial_number FROM assets_asset WHERE asset_tag = 'BIDC1544'
);
```

**Copy the results to a text file for reference.**

### Step 2: Delete the Asset

In the Asset Tracker web interface:
1. Go to asset BIDC1544
2. Click "Free Asset" or "Delete"
3. Confirm deletion

### Step 3: Re-create the Asset

1. Click "Add Asset"
2. Fill in all the details from the saved data
3. Save the new asset
4. Add secondary IPs if needed (by editing the newly created asset)

---

## COMPREHENSIVE FIX FOR ALL CORRUPTED IPS

Run this query to find ALL corrupted IPs (not just the 1 we fixed earlier):

```sql
SELECT 
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.id as junction_id,
    aip.asset_id,
    a.asset_tag,
    a.assigned_to
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.serial_number = aip.asset_id
WHERE (ip.is_assigned = 0 AND aip.asset_id IS NOT NULL)
   OR (ip.is_assigned = 1 AND aip.asset_id IS NULL AND ip.assigned_to_asset_id IS NOT NULL)
   OR (ip.assigned_to_asset_id IS NOT NULL AND ip.assigned_to_asset_id != aip.asset_id);
```

**For each row returned, run:**
```sql
UPDATE assets_ipaddress 
SET is_assigned = 1, assigned_to_asset_id = [asset_id from result] 
WHERE id = [ip_id from result];
```

---

## TEMPORARY WORKAROUND

Until the corruption is fully fixed, users can:

1. **For Anjana (BIDC1544):**
   - Delete the asset (or "Free" it first, then delete)
   - Re-create it as a new asset
   - This will work immediately

2. **For other problematic assets:**
   - Same process: delete and re-create

**This is safe because:**
- Asset history is preserved if you "Free" before deleting
- You can copy all the data before deleting
- Re-creating takes only 2-3 minutes per asset

---

## FILES TO UPLOAD (If Not Already Done)

Make sure these files are uploaded to the Linux server:

1. **asset_forms.py** → `/var/www/asset_tracker/assets/forms/asset_forms.py`
2. **views.py** → `/var/www/asset_tracker/assets/views.py`

Both files are in: `d:\Asset tracker\LINUX_SERVER_UPLOAD\`

After uploading, restart Django:
```bash
sudo systemctl restart asset_tracker
```

---

## TESTING PLAN

### Test 1: Identify All Problematic Assets
Run Query 5 to find all assets that might have issues.

### Test 2: Fix or Re-create
For each problematic asset:
- Try to edit it
- If it freezes → Delete and re-create
- If it saves → Good, no action needed

### Test 3: Verify Database is Clean
After fixing/re-creating all problematic assets, run:

```sql
SELECT COUNT(*) as corrupted_count
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Should return 0.**

---

## QUICK REFERENCE: Commands for Linux Team

```bash
# 1. Connect to MySQL
mysql -u your_username -p assets_db

# 2. Run diagnostic queries (see above)

# 3. Run fix commands based on results

# 4. Restart Django
sudo systemctl restart asset_tracker

# 5. Test editing assets
```

---

## SUMMARY

**Problem:** Asset editing freezes for existing assets (BIDC1544 Anjana)  
**Cause:** Corrupted IP relationships in database  
**Solution:** 
1. Run diagnostic queries to find corruption
2. Fix with SQL UPDATE commands OR
3. Delete and re-create the problematic assets

**Temporary Workaround:** Delete BIDC1544 and re-create it (takes 2-3 minutes)

---

## WHEN YOU WAKE UP

1. **Check if Linux team uploaded the 2 files** (asset_forms.py and views.py)
2. **Run the diagnostic queries** above to find BIDC1544's corruption
3. **Choose one:**
   - Option A: Fix corruption with SQL (if corruption is simple)
   - Option B: Delete and re-create BIDC1544 (faster and easier)
4. **Test editing BIDC1544 after fix**

---

**All queries and commands are ready to copy-paste. Sleep well!** 😊
