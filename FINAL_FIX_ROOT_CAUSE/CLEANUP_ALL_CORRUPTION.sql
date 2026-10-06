-- ============================================================================
-- CLEAN UP ALL CORRUPTED IPS - RUN AFTER UPLOADING NEW views.py
-- ============================================================================

-- This script finds and fixes ALL corrupted IPs in one go
-- Run this AFTER uploading the fixed views.py file

-- ============================================================================
-- STEP 1: Find all corrupted IPs
-- ============================================================================

SELECT 
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.asset_id,
    a.asset_tag,
    a.assigned_to
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.serial_number = aip.asset_id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;

-- Copy the results - you'll need the ip_id and asset_id for each row

-- ============================================================================
-- STEP 2: Fix each corrupted IP
-- ============================================================================

-- For each row from Step 1, run this command:
-- UPDATE assets_ipaddress 
-- SET is_assigned = 1, assigned_to_asset_id = [asset_id] 
-- WHERE id = [ip_id];

-- Example:
-- UPDATE assets_ipaddress SET is_assigned = 1, assigned_to_asset_id = 100 WHERE id = 1450;

-- ============================================================================
-- STEP 3: Verify all corruption is fixed
-- ============================================================================

SELECT COUNT(*) as remaining_corruption
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;

-- Should return: 0

-- ============================================================================
-- ALTERNATIVE: Find which assets need to be deleted and re-created
-- ============================================================================

-- This finds assets that have corrupted IPs
-- Instead of fixing the corruption, you can delete and re-create these assets

SELECT DISTINCT
    a.serial_number,
    a.asset_tag,
    a.assigned_to,
    a.employee_code
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.is_assigned = 0;

-- Delete and re-create each asset listed above

-- ============================================================================
-- RECOMMENDED APPROACH
-- ============================================================================

-- OPTION A: Fix corruption with SQL (faster if many assets)
--   1. Run Step 1 to find corrupted IPs
--   2. Run UPDATE commands for each IP
--   3. Run Step 3 to verify
--   4. Restart Django
--   5. Test editing assets

-- OPTION B: Delete and re-create (cleaner, guaranteed to work)
--   1. Run ALTERNATIVE query above
--   2. For each asset listed, delete and re-create via web interface
--   3. Takes 2-3 min per asset
--   4. Guaranteed clean data

-- ============================================================================
