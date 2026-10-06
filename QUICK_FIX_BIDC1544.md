# QUICK FIX - BIDC1544 (Anjana) Editing Freeze

**Fastest solution: Delete and re-create the asset** (2-3 minutes)

---

## OPTION 1: Quick Fix (Recommended - 2 minutes)

### Step 1: Save Current Info (Run in MySQL)

```sql
SELECT 
    a.asset_tag,
    a.system_type,
    a.manufacturer,
    a.hardware_serial_number,
    os.name as operating_system,
    a.assigned_to,
    a.employee_code,
    a.particulars,
    t.name as team,
    b.name as branch,
    a.warranty_expiration,
    ip.address as primary_ip
FROM assets_asset a
LEFT JOIN assets_operatingsystem os ON os.id = a.operating_system_id
LEFT JOIN assets_team t ON t.id = a.team_id
LEFT JOIN assets_branch b ON b.id = a.branch_id
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number AND aip.is_primary = 1
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1544';
```

**Copy the results - you'll need them to re-create the asset.**

---

### Step 2: Delete the Asset

**In the web interface:**
1. Go to Assets page
2. Find BIDC1544
3. Click on it to view details
4. Click "Free Asset" button (if available) → Enter admin password
5. Then click "Delete" or "Scrap" button

**Or run SQL:**
```sql
-- Get the serial number first
SELECT serial_number FROM assets_asset WHERE asset_tag = 'BIDC1544';

-- Delete IP relationships (replace XXX with serial_number)
DELETE FROM assets_assetipaddress WHERE asset_id = XXX;

-- Delete the asset
DELETE FROM assets_asset WHERE asset_tag = 'BIDC1544';
```

---

### Step 3: Re-create the Asset

**In the web interface:**
1. Go to "Add Asset"
2. Fill in the form with the data from Step 1:
   - Asset Tag: BIDC1544
   - System Type: [from saved data]
   - Operating System: [from saved data]
   - IP Address: [from saved data]
   - Assigned To: Anjana (or whatever was saved)
   - Employee Code: [from saved data]
   - Team: [from saved data]
   - Branch: [from saved data]
   - Warranty: [from saved data]
3. Click "Save" or "Create"

**Done!** The asset should work now without freezing.

---

## OPTION 2: Fix Database Corruption (Longer - 10 minutes)

### Step 1: Find Corruption for BIDC1544

```sql
-- Get asset ID
SELECT serial_number FROM assets_asset WHERE asset_tag = 'BIDC1544';
-- Note the number (let's call it XXX)

-- Check for corrupted IPs
SELECT 
    aip.id as junction_id,
    aip.asset_id,
    aip.is_primary,
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id
FROM assets_assetipaddress aip
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE aip.asset_id = XXX;
```

**Look for rows where:**
- `is_assigned = 0` but `asset_id` has a value → Fix with UPDATE
- `assigned_to_asset_id` is NULL or doesn't match XXX → Fix with UPDATE

---

### Step 2: Fix Each Corrupted IP

For each row from Step 1 that looks wrong:

```sql
UPDATE assets_ipaddress 
SET is_assigned = 1, assigned_to_asset_id = XXX 
WHERE id = YYY;
```

Replace:
- XXX = asset serial_number from Step 1
- YYY = ip_id from the corrupted row

---

### Step 3: Restart Django

```bash
sudo systemctl restart asset_tracker
```

---

### Step 4: Test

Try to edit BIDC1544 - should work now!

---

## RECOMMENDATION

**Use Option 1** (delete and re-create) because:
- ✅ Faster (2 minutes vs 10 minutes)
- ✅ Cleaner (no lingering corruption)
- ✅ Easier (no complex SQL queries)
- ✅ Guaranteed to work

**Use Option 2** only if:
- Asset has lots of history you want to preserve
- Asset has many accessories attached
- Asset has complex configuration

---

## FOR LINUX TEAM

**After fixing BIDC1544, check other assets too:**

```sql
-- Find all assets that might have similar issues
SELECT 
    a.asset_tag,
    a.assigned_to,
    COUNT(aip.id) as ip_count
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL
GROUP BY a.asset_tag, a.assigned_to;
```

Any assets listed here will have the same freeze problem when editing.

---

**Sleep well! This will be fixed when you wake up.** 😊
