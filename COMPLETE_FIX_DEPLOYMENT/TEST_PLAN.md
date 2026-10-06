# Asset Edit Page - Complete Fix Test Plan

## Issues Fixed

### 1. IP Dropdown Bug (Primary IP)
**Problem:** Current IP excluded from dropdown if it sorts after 200th free IP
**Fix:** Always include current IP at top of dropdown, regardless of position
**Files:** `assets/forms/asset_forms.py` lines 266-278

### 2. IP Dropdown Bug (Additional IPs)
**Problem:** Same issue for additional IPs (WiFi, Mobile, VPN)
**Fix:** Same solution applied to AdditionalIPForm
**Files:** `assets/forms/asset_forms.py` lines 721-738

### 3. Silent Validation Failures
**Problem:** Validation errors not visible to users (missing CSS, alert() popups)
**Fix:** Added inline error display with styling, red borders, auto-scroll
**Files:** `assets/templates/assets/asset_form.html` lines 7-23, 1095-1144

---

## Test Scenarios

### Scenario A: Edit Asset with 70.x IP (Jabir - BIDC1419)

**Steps:**
1. Navigate to Asset List
2. Click Edit on BIDC1419 (Jabir)
3. **Verify:** IP dropdown shows `192.168.70.34` at or near top
4. **Verify:** All other fields populated correctly
5. Click Update WITHOUT making any changes
6. **Expected:** Success message "Asset BIDC1419 updated successfully"
7. **Expected:** Returns to previous page (not main page if using back button fix)

**Pass Criteria:**
- ✅ IP dropdown contains current IP
- ✅ Update succeeds without changes
- ✅ No validation errors
- ✅ No page freeze

---

### Scenario B: Edit Asset with 70.x IP (Githin - BIDC1420)

**Steps:**
1. Navigate to Asset List
2. Click Edit on BIDC1420 (Githin)
3. **Verify:** IP dropdown shows `192.168.70.85` at or near top
4. **Verify:** All other fields populated correctly
5. Click Update WITHOUT making any changes
6. **Expected:** Success message "Asset BIDC1420 updated successfully"

**Pass Criteria:**
- ✅ IP dropdown contains current IP
- ✅ Update succeeds without changes
- ✅ No validation errors
- ✅ No page freeze

---

### Scenario C: Edit Asset with 11.x IP

**Steps:**
1. Find an asset with 192.168.11.x IP
2. Click Edit
3. **Verify:** IP dropdown shows current 11.x IP at top
4. Click Update WITHOUT making any changes
5. **Expected:** Success message

**Pass Criteria:**
- ✅ IP dropdown contains current IP
- ✅ Update succeeds

---

### Scenario D: Edit Asset with Additional IPs in 70.x Range

**Steps:**
1. Find an asset that has additional IPs in 70.x range
2. Click Edit
3. Scroll to "Additional IP Addresses" section
4. **Verify:** Each additional IP dropdown shows its current IP
5. Click Update WITHOUT making changes
6. **Expected:** Success message

**Pass Criteria:**
- ✅ All additional IP dropdowns contain their current IPs
- ✅ Update succeeds
- ✅ Additional IPs unchanged

---

### Scenario E: Change Primary IP to Different Range

**Steps:**
1. Edit Jabir's asset (BIDC1419, currently 192.168.70.34)
2. Change IP to one from 10.x or 50.x range
3. Click Update
4. **Expected:** Success message
5. Go back to edit page
6. **Verify:** New IP is shown in dropdown and selected

**Pass Criteria:**
- ✅ IP change succeeds
- ✅ Old IP freed (is_assigned=0)
- ✅ New IP assigned (is_assigned=1)
- ✅ Next edit shows new IP in dropdown

---

### Scenario F: Validation Error Display

**Steps:**
1. Create or Edit a Laptop asset
2. Clear the Hardware Serial Number field (required for laptops)
3. Click Update
4. **Verify:** Red error message appears below Hardware Serial Number field
5. **Verify:** Field has red border
6. **Verify:** Page scrolls to the error field
7. **Verify:** Console shows validation error (F12 → Console)
8. Fill in the serial number
9. Click Update
10. **Expected:** Success message

**Pass Criteria:**
- ✅ Error message visible in red text
- ✅ Invalid field highlighted with red border
- ✅ Page auto-scrolls to error
- ✅ Error clears when field is fixed
- ✅ Form submits successfully after correction

---

### Scenario G: Asset Tag Change Requires Password

**Steps:**
1. Edit any asset
2. Change the Asset Tag field
3. **Verify:** Password field appears with warning
4. Click Update WITHOUT entering password
5. **Expected:** Alert "Please enter your admin password to change the asset tag."
6. Enter admin password
7. Click Update
8. **Expected:** Success message with tag change confirmation

**Pass Criteria:**
- ✅ Password field appears when tag changes
- ✅ Alert shown if password missing
- ✅ Update succeeds with valid admin password
- ✅ Change logged in asset history

---

### Scenario H: Multiple Users Editing Simultaneously

**Steps:**
1. User A: Opens edit page for Asset X
2. User B: Opens edit page for same Asset X
3. User A: Makes changes and clicks Update
4. **Expected:** User A's changes saved successfully
5. User B: Makes changes and clicks Update
6. **Expected:** User B's changes saved successfully
7. **Verify:** No IP corruption in database

**Pass Criteria:**
- ✅ Both updates succeed
- ✅ No race condition corruption
- ✅ IP assignment states remain consistent

---

### Scenario I: Manual IP Entry for Assets Without Managed IP

**Steps:**
1. Edit any asset
2. Click "Manual Entry" button next to IP Address field
3. Enter a custom IP: `172.16.10.50`
4. Click Update
5. **Expected:** Success message
6. Go back to edit page
7. **Verify:** Manual IP shown (not in dropdown)

**Pass Criteria:**
- ✅ Manual IP saves correctly
- ✅ Dropdown not used
- ✅ Manual IP persists

---

### Scenario J: Browser Console Verification

**During ANY edit operation:**

1. Open browser console (F12 → Console)
2. Click Update
3. **Verify NO errors shown:**
   - ❌ "Validation failed" (unless intentional test)
   - ❌ JavaScript errors (red text)
   - ❌ "All required attributes removed"
4. **Expected messages:**
   - ✅ "Form is submitting..."
   - ✅ Form data logged
   - ✅ "Toggling visibility for type: managed" (if using IP dropdown)

**Pass Criteria:**
- ✅ No JavaScript errors
- ✅ Form submission logged
- ✅ No "required attributes removed" message

---

## Database Integrity Checks

After ALL tests complete, run these SQL queries:

### Check 1: No Orphaned IPs
```sql
-- Should return 0 rows
SELECT ip.id, ip.address, ip.is_assigned, aip.asset_id
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Expected:** Empty set (0 rows)

### Check 2: All Assigned IPs Have Assets
```sql
-- Should return 0 rows
SELECT ip.id, ip.address, ip.is_assigned, ip.assigned_to_asset_id
FROM assets_ipaddress ip
WHERE ip.is_assigned = 1 AND ip.assigned_to_asset_id IS NULL;
```

**Expected:** Empty set (0 rows)

### Check 3: Asset IP Counts Match
```sql
-- Check for assets with multiple primary IPs (should be 0)
SELECT asset_id, COUNT(*) as primary_count
FROM assets_assetipaddress
WHERE is_primary = 1
GROUP BY asset_id
HAVING COUNT(*) > 1;
```

**Expected:** Empty set (0 rows)

### Check 4: Jabir and Githin Status
```sql
-- Verify their IPs are correctly assigned
SELECT 
    a.asset_tag,
    a.assigned_to,
    ip.address,
    ip.is_assigned,
    aip.is_primary
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag IN ('BIDC1419', 'BIDC1420')
ORDER BY a.asset_tag;
```

**Expected:**
```
BIDC1419 | Jabir  | 192.168.70.34 | 1 | 1
BIDC1420 | Githin | 192.168.70.85 | 1 | 1
```

---

## Performance Test

**Goal:** Ensure the form loads quickly even with the fixes

**Steps:**
1. Open edit page for ANY asset
2. Measure page load time
3. **Expected:** < 2 seconds

**Pass Criteria:**
- ✅ Page loads in under 2 seconds
- ✅ IP dropdown populates within 1 second
- ✅ No browser lag

---

## Rollback Plan (If Tests Fail)

If ANY test fails:

### 1. Restore Previous Files
```bash
sudo cp /var/www/asset_tracker/assets/forms/asset_forms.py.backup_YYYYMMDD_HHMMSS /var/www/asset_tracker/assets/forms/asset_forms.py
sudo cp /var/www/asset_tracker/assets/templates/assets/asset_form.html.backup_YYYYMMDD_HHMMSS /var/www/asset_tracker/assets/templates/assets/asset_form.html
sudo systemctl restart asset_tracker
```

### 2. Report the Issue
- Which test scenario failed?
- What was the error message?
- What did the console show?
- Screenshot of the problem

---

## Success Criteria Summary

✅ All 10 test scenarios pass
✅ All 4 database integrity checks pass
✅ Performance test passes
✅ No JavaScript errors in console
✅ No regression (existing functionality still works)

**Once all tests pass, the fix is production-ready!**
