-- ============================================================================
-- BULK FIX: Corrupted IPs in 192.168.70.x and 192.168.11.x Ranges
-- ============================================================================
-- Issue: Most laptops (70.x) and 11.x assets freeze when editing
-- Cause: IPs marked as free (is_assigned=0) but still linked to assets
-- Solution: Fix ALL corrupted IPs in these ranges at once
-- ============================================================================

-- STEP 1: Find ALL corrupted IPs in 70.x and 11.x ranges
-- ============================================================================

SELECT 
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.asset_id,
    a.asset_tag,
    a.assigned_to,
    a.system_type
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.serial_number = aip.asset_id
WHERE ip.is_assigned = 0 
  AND aip.asset_id IS NOT NULL
  AND (ip.address LIKE '192.168.70.%' OR ip.address LIKE '192.168.11.%')
ORDER BY ip.address;

-- IMPORTANT: Copy the results above before proceeding!
-- Count how many rows are returned - this is how many IPs need fixing

-- ============================================================================
-- STEP 2: Fix ALL corrupted IPs in BULK
-- ============================================================================

-- This single query fixes ALL corrupted IPs in 70.x and 11.x ranges at once!

UPDATE assets_ipaddress ip
JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
SET ip.is_assigned = 1,
    ip.assigned_to_asset_id = aip.asset_id
WHERE ip.is_assigned = 0
  AND aip.asset_id IS NOT NULL
  AND (ip.address LIKE '192.168.70.%' OR ip.address LIKE '192.168.11.%');

-- This will update ALL corrupted IPs in one go!

-- ============================================================================
-- STEP 3: Verify the fix
-- ============================================================================

-- Check if any corruption remains in 70.x and 11.x ranges
SELECT COUNT(*) as remaining_corruption
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 
  AND aip.asset_id IS NOT NULL
  AND (ip.address LIKE '192.168.70.%' OR ip.address LIKE '192.168.11.%');

-- Should return: 0

-- ============================================================================
-- STEP 4: Check ALL ranges for any remaining corruption
-- ============================================================================

SELECT 
    SUBSTRING_INDEX(ip.address, '.', 3) as ip_range,
    COUNT(*) as corrupted_count
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL
GROUP BY SUBSTRING_INDEX(ip.address, '.', 3)
ORDER BY corrupted_count DESC;

-- This shows if any other IP ranges also have corruption

-- ============================================================================
-- STEP 5: Find ALL assets that were affected (for testing)
-- ============================================================================

SELECT DISTINCT
    a.asset_tag,
    a.assigned_to,
    a.system_type,
    GROUP_CONCAT(ip.address) as ip_addresses
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.serial_number
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE (ip.address LIKE '192.168.70.%' OR ip.address LIKE '192.168.11.%')
GROUP BY a.asset_tag, a.assigned_to, a.system_type
ORDER BY a.asset_tag;

-- Test editing a few of these assets after the fix to verify they work

-- ============================================================================
-- SUMMARY OF COMMANDS
-- ============================================================================

-- Quick execution steps:

-- 1. Run STEP 1 query (see how many corrupted)
-- 2. Run STEP 2 UPDATE query (fix all at once)
-- 3. Run STEP 3 query (verify fixed - should be 0)
-- 4. Restart Django: sudo systemctl restart asset_tracker
-- 5. Test editing some laptop assets (70.x IPs)
-- 6. Test editing some 11.x assets
-- 7. Should all work now!

-- ============================================================================
-- EXPECTED RESULTS
-- ============================================================================

-- STEP 1: Probably 50-200+ corrupted IPs (many laptops!)
-- STEP 2: "Query OK, XXX rows affected" (matches Step 1 count)
-- STEP 3: 0 (no corruption remaining)
-- After restart: All laptop assets can be edited without freezing

-- ============================================================================
