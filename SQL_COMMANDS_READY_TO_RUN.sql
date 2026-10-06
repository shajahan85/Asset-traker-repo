-- ============================================================================
-- SQL COMMANDS FOR ASSET TRACKER FIX
-- Date: September 24, 2026
-- Database: assets_db
-- ============================================================================

-- Connect to database first:
-- mysql -u your_username -p assets_db

-- ============================================================================
-- STEP 1: VERIFY DATABASE CORRUPTION IS FIXED
-- ============================================================================

-- This should return 0 (zero)
SELECT COUNT(*) as total_corrupted
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;

-- Expected: total_corrupted = 0

-- ============================================================================
-- STEP 2: FIND BIDC1544 ASSET ID
-- ============================================================================

SELECT serial_number, asset_tag, assigned_to, employee_code, status
FROM assets_asset
WHERE asset_tag = 'BIDC1544';

-- Note the serial_number - you'll use it in the next queries

-- ============================================================================
-- STEP 3: CHECK BIDC1544 FOR CORRUPTION
-- ============================================================================

-- Replace XXX with the serial_number from Step 2
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
WHERE aip.asset_id = XXX;  -- Replace XXX with actual serial_number

-- Look for:
-- - ip.is_assigned = 0 (should be 1)
-- - ip.assigned_to_asset_id NULL or doesn't match asset_id

-- ============================================================================
-- STEP 4: FIX CORRUPTED IPS FOR BIDC1544 (IF FOUND)
-- ============================================================================

-- If Step 3 found corrupted IPs, run this for each corrupted IP:
-- Replace XXX with asset serial_number, YYY with ip.id

UPDATE assets_ipaddress 
SET is_assigned = 1, assigned_to_asset_id = XXX 
WHERE id = YYY;

-- Run the UPDATE command for each corrupted IP found in Step 3

-- ============================================================================
-- STEP 5: CHECK FOR DUPLICATE PRIMARY IPS
-- ============================================================================

-- This should return no rows (each asset should have only 1 primary IP)
SELECT 
    asset_id,
    COUNT(*) as primary_count
FROM assets_assetipaddress
WHERE is_primary = 1
GROUP BY asset_id
HAVING COUNT(*) > 1;

-- If any rows are returned, that asset has multiple primary IPs (corruption)

-- ============================================================================
-- STEP 6: FIX DUPLICATE PRIMARY IPS (IF FOUND)
-- ============================================================================

-- For each asset with duplicate primary IPs from Step 5:

-- First, see which IPs are marked as primary:
SELECT id, asset_id, is_primary, created_at, ip_address_id, manual_ip
FROM assets_assetipaddress 
WHERE asset_id = XXX AND is_primary = 1  -- Replace XXX
ORDER BY created_at ASC;

-- Keep the OLDEST one as primary, set the rest to secondary:
UPDATE assets_assetipaddress 
SET is_primary = 0 
WHERE id IN (YYY, ZZZ);  -- Replace with IDs of the NEWER primary IPs

-- ============================================================================
-- STEP 7: FIND ALL OTHER PROBLEMATIC ASSETS
-- ============================================================================

-- This finds all assets that might freeze when editing
SELECT 
    a.serial_number,
    a.asset_tag,
    a.assigned_to,
    a.employee_code,
    COUNT(DISTINCT aip.id) as ip_count,
    SUM(CASE WHEN ip.is_assigned = 0 THEN 1 ELSE 0 END) as free_ips_count
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
GROUP BY a.serial_number, a.asset_tag, a.assigned_to, a.employee_code
HAVING SUM(CASE WHEN ip.is_assigned = 0 THEN 1 ELSE 0 END) > 0;

-- Any assets listed here have corrupted IPs and will freeze when editing

-- ============================================================================
-- STEP 8: COMPREHENSIVE CORRUPTION CHECK
-- ============================================================================

-- Find ALL types of IP corruption in the database
SELECT 
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.id as junction_id,
    aip.asset_id,
    a.asset_tag,
    a.assigned_to,
    CASE 
        WHEN ip.is_assigned = 0 AND aip.asset_id IS NOT NULL THEN 'Marked free but assigned'
        WHEN ip.is_assigned = 1 AND aip.asset_id IS NULL AND ip.assigned_to_asset_id IS NOT NULL THEN 'Marked assigned but no junction'
        WHEN ip.assigned_to_asset_id IS NOT NULL AND ip.assigned_to_asset_id != aip.asset_id THEN 'Mismatched asset IDs'
        ELSE 'Unknown'
    END as corruption_type
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.serial_number = aip.asset_id
WHERE (ip.is_assigned = 0 AND aip.asset_id IS NOT NULL)
   OR (ip.is_assigned = 1 AND aip.asset_id IS NULL AND ip.assigned_to_asset_id IS NOT NULL)
   OR (ip.assigned_to_asset_id IS NOT NULL AND ip.assigned_to_asset_id != aip.asset_id);

-- For each row returned, fix with:
UPDATE assets_ipaddress 
SET is_assigned = 1, assigned_to_asset_id = [asset_id from result] 
WHERE id = [ip_id from result];

-- ============================================================================
-- STEP 9: SAVE BIDC1544 DATA BEFORE DELETING (OPTIONAL)
-- ============================================================================

-- If you plan to delete and re-create BIDC1544, save this data first:
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
    GROUP_CONCAT(ip.address) as all_ips
FROM assets_asset a
LEFT JOIN assets_operatingsystem os ON os.id = a.operating_system_id
LEFT JOIN assets_team t ON t.id = a.team_id
LEFT JOIN assets_branch b ON b.id = a.branch_id
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1544'
GROUP BY a.asset_tag, a.system_type, a.manufacturer, a.hardware_serial_number, 
         os.name, a.assigned_to, a.employee_code, a.particulars, 
         t.name, b.name, a.warranty_expiration;

-- Copy the results - you'll need them to re-create the asset

-- ============================================================================
-- STEP 10: DELETE BIDC1544 (OPTIONAL - USE ONLY IF RE-CREATING)
-- ============================================================================

-- Get serial number first
SELECT serial_number FROM assets_asset WHERE asset_tag = 'BIDC1544';
-- Note the serial_number (let's call it XXX)

-- Delete IP relationships
DELETE FROM assets_assetipaddress WHERE asset_id = XXX;

-- Delete the asset
DELETE FROM assets_asset WHERE asset_tag = 'BIDC1544';

-- After this, re-create BIDC1544 using the web interface

-- ============================================================================
-- STEP 11: FINAL VERIFICATION
-- ============================================================================

-- After all fixes, verify there are NO corrupted IPs left:
SELECT COUNT(*) as remaining_corruption
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;

-- Expected: remaining_corruption = 0

-- Verify no duplicate primary IPs:
SELECT COUNT(*) as duplicate_primaries
FROM (
    SELECT asset_id, COUNT(*) as cnt
    FROM assets_assetipaddress
    WHERE is_primary = 1
    GROUP BY asset_id
    HAVING COUNT(*) > 1
) sub;

-- Expected: duplicate_primaries = 0

-- ============================================================================
-- DONE!
-- ============================================================================

-- After running these queries and fixing any issues found:
-- 1. Restart Django: sudo systemctl restart asset_tracker
-- 2. Test editing BIDC1544
-- 3. Test editing other previously problematic assets

-- ============================================================================
