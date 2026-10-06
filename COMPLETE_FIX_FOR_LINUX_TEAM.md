# COMPLETE FIX FOR PRODUCTION LINUX SERVER

**Issue:** Assets BIDC1326 (Sankar), BIDC1544 (Anjana), BIDC1569, and Kharunnisa's assets freeze when updating

**Root Cause:** Database corruption - IP addresses marked as free (`is_assigned=0`) but actually assigned to assets

---

## STEP 1: Upload the Fixed Code File

**File to upload:**
```
Source (Windows): d:\Asset tracker\WORKING_FIX_NO_LIMITS\asset_forms.py
Destination (Linux): /var/www/asset_tracker/assets/forms/asset_forms.py
```

**How to upload:**
- Use WinSCP, FileZilla, or scp command
- Make sure to backup the old file first:
  ```bash
  sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py /var/www/asset_tracker/assets/forms/asset_forms.py.backup_$(date +%Y%m%d)
  ```

---

## STEP 2: Fix Database Corruption

### 2A. First, check how many corrupted IPs exist:

```sql
SELECT COUNT(*) as total_corrupted
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**If the result is 0:** Skip to STEP 3  
**If the result is > 0:** Continue with 2B

### 2B. Find ALL corrupted IP records:

```sql
SELECT 
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    aip.asset_id,
    a.asset_tag
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.id = aip.asset_id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Copy the results and send them to the developer.**

### 2C. Fix the 14 known corrupted IPs:

Run these 14 UPDATE commands one by one:

```sql
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1084;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1141;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1028;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1678;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1486;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1587;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1437;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1656;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1167;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1714;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1414;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1768;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1417;
UPDATE assets_ipaddress SET is_assigned = 1 WHERE id = 1106;
```

### 2D. Fix the assigned_to_asset_id field:

```sql
UPDATE assets_ipaddress SET assigned_to_asset_id = 106 WHERE id = 1084;
UPDATE assets_ipaddress SET assigned_to_asset_id = 147 WHERE id = 1141;
UPDATE assets_ipaddress SET assigned_to_asset_id = 61 WHERE id = 1028;
UPDATE assets_ipaddress SET assigned_to_asset_id = 193 WHERE id = 1678;
UPDATE assets_ipaddress SET assigned_to_asset_id = 142 WHERE id = 1486;
UPDATE assets_ipaddress SET assigned_to_asset_id = 164 WHERE id = 1587;
UPDATE assets_ipaddress SET assigned_to_asset_id = 128 WHERE id = 1437;
UPDATE assets_ipaddress SET assigned_to_asset_id = 181 WHERE id = 1656;
UPDATE assets_ipaddress SET assigned_to_asset_id = 116 WHERE id = 1167;
UPDATE assets_ipaddress SET assigned_to_asset_id = 203 WHERE id = 1714;
UPDATE assets_ipaddress SET assigned_to_asset_id = 126 WHERE id = 1414;
UPDATE assets_ipaddress SET assigned_to_asset_id = 210 WHERE id = 1768;
UPDATE assets_ipaddress SET assigned_to_asset_id = 126 WHERE id = 1417;
UPDATE assets_ipaddress SET assigned_to_asset_id = 109 WHERE id = 1106;
```

### 2E. Verify the fix:

```sql
SELECT COUNT(*) as remaining_corrupted
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Should return 0 (zero)**

---

## STEP 3: Restart Django

```bash
sudo systemctl restart asset_tracker
```

Wait 10 seconds, then check status:

```bash
sudo systemctl status asset_tracker
```

**Should show:** `Active: active (running)` in GREEN

---

## STEP 4: Test the Fix

1. **Open the asset tracker website in browser**
2. **Try to edit asset BIDC1326 (Sankar)**
   - Click Edit
   - Change something (e.g., add a note in Particulars)
   - Click Update
   - **Expected:** Page saves immediately without freezing

3. **Try to edit asset BIDC1544 (Anjana)**
   - Same test as above

4. **Try to edit asset BIDC1569**
   - Same test as above

5. **Try to edit Kharunnisa's asset**
   - Same test as above

---

## STEP 5: If Still Freezing

If the issue persists after all steps above:

### 5A. Check for MORE corrupted IPs:

```sql
SELECT 
    ip.id,
    ip.address,
    ip.is_assigned,
    aip.asset_id,
    a.asset_tag
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id  
LEFT JOIN assets_asset a ON a.id = aip.asset_id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Send the results to the developer.**

### 5B. Check Django logs for errors:

```bash
sudo journalctl -u asset_tracker -n 100 --no-pager
```

**Send the last 100 lines to the developer.**

### 5C. Check MySQL slow query log:

```bash
sudo tail -100 /var/log/mysql/mysql-slow.log
```

**Send the results to the developer.**

---

## Troubleshooting

### If Django won't start after file upload:

```bash
# Check for Python syntax errors
cd /var/www/asset_tracker
python manage.py check

# If there's a syntax error, restore backup:
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py.backup_* /var/www/asset_tracker/assets/forms/asset_forms.py
sudo systemctl restart asset_tracker
```

### If site loads but freeze issue persists:

The database corruption is more extensive than the 14 IPs we identified. Run Step 5A and send results.

---

## Summary Checklist

- [ ] File uploaded: asset_forms.py
- [ ] SQL corruption fix: 14 UPDATE commands executed
- [ ] Verification query shows 0 corrupted IPs
- [ ] Django restarted successfully
- [ ] BIDC1326 can be edited without freezing
- [ ] BIDC1544 can be edited without freezing
- [ ] BIDC1569 can be edited without freezing
- [ ] Kharunnisa's assets can be edited without freezing

---

**After completing all steps, report back with:**
1. ✅ or ❌ for each checklist item
2. Any error messages encountered
3. Results of the verification queries
