-- ============================================================
-- VERIFICATION QUERIES - RUN AFTER DEPLOYING THE FIX
-- These confirm that the fix is working correctly
-- ============================================================

-- Verification 1: Check Jabir's asset (BIDC1419)
-- Should show IP 192.168.70.34 with is_assigned=1
SELECT 
    'JABIR CHECK' as test_name,
    a.asset_tag,
    a.assigned_to,
    ip.address,
    ip.is_assigned,
    aip.is_primary,
    CASE 
        WHEN ip.is_assigned = 1 AND aip.is_primary = 1 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1419';

-- Verification 2: Check Githin's asset (BIDC1420)
-- Should show IP 192.168.70.85 with is_assigned=1
SELECT 
    'GITHIN CHECK' as test_name,
    a.asset_tag,
    a.assigned_to,
    ip.address,
    ip.is_assigned,
    aip.is_primary,
    CASE 
        WHEN ip.is_assigned = 1 AND aip.is_primary = 1 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1420';

-- Verification 3: Check for orphaned IPs (database corruption)
-- Should return 0 rows
SELECT 
    'ORPHANED IP CHECK' as test_name,
    ip.id,
    ip.address,
    ip.is_assigned,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL
GROUP BY ip.id, ip.address, ip.is_assigned;

-- Verification 4: Check for IPs marked as assigned but not linked to assets
-- Should return 0 rows
SELECT 
    'UNLINKED ASSIGNED IP CHECK' as test_name,
    ip.id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    CASE 
        WHEN COUNT(*) = 0 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_ipaddress ip
WHERE ip.is_assigned = 1 AND ip.assigned_to_asset_id IS NULL
GROUP BY ip.id, ip.address, ip.is_assigned, ip.assigned_to_asset_id;

-- Verification 5: Check for assets with multiple primary IPs
-- Should return 0 rows
SELECT 
    'MULTIPLE PRIMARY IP CHECK' as test_name,
    asset_id,
    COUNT(*) as primary_count,
    CASE 
        WHEN COUNT(*) = 1 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_assetipaddress
WHERE is_primary = 1
GROUP BY asset_id
HAVING COUNT(*) > 1;

-- Verification 6: Sample of 70.x range assets
-- All should show is_assigned=1 and is_primary=1
SELECT 
    '70.x RANGE CHECK' as test_name,
    a.asset_tag,
    a.assigned_to,
    ip.address,
    ip.is_assigned,
    aip.is_primary,
    CASE 
        WHEN ip.is_assigned = 1 AND aip.is_primary = 1 THEN '✅ PASS'
        ELSE '❌ FAIL'
    END as status
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.address LIKE '192.168.70.%'
LIMIT 10;

-- Verification 7: Overall system health summary
SELECT 
    'SYSTEM HEALTH SUMMARY' as check_type,
    (SELECT COUNT(*) FROM assets_asset) as total_assets,
    (SELECT COUNT(*) FROM assets_ipaddress WHERE is_assigned = 1) as assigned_ips,
    (SELECT COUNT(*) FROM assets_ipaddress WHERE is_assigned = 0) as free_ips,
    (SELECT COUNT(*) FROM assets_assetipaddress WHERE is_primary = 1) as assets_with_primary_ip,
    CASE 
        WHEN (SELECT COUNT(*) FROM assets_asset) = (SELECT COUNT(*) FROM assets_assetipaddress WHERE is_primary = 1)
        THEN '✅ All assets have primary IPs'
        ELSE '⚠️ Some assets missing primary IPs'
    END as status;

-- ============================================================
-- MANUAL TEST CHECKLIST (Do these in browser)
-- ============================================================
--
-- ✅ 1. Edit BIDC1419 (Jabir)
--    - IP dropdown shows 192.168.70.34
--    - Click Update without changes
--    - Success message appears
--
-- ✅ 2. Edit BIDC1420 (Githin)
--    - IP dropdown shows 192.168.70.85
--    - Click Update without changes
--    - Success message appears
--
-- ✅ 3. Edit any laptop asset (70.x IP)
--    - IP dropdown shows current IP
--    - Update works
--
-- ✅ 4. Edit any 11.x IP asset
--    - IP dropdown shows current IP
--    - Update works
--
-- ✅ 5. Try to submit with missing required field (e.g., clear Asset Tag)
--    - Red error message appears below field
--    - Field has red border
--    - Page scrolls to error
--
-- ✅ 6. Check browser console (F12)
--    - No JavaScript errors (red text)
--    - Should see "Form is submitting..." when clicking Update
--    - Should NOT see "All required attributes removed"
--
-- ============================================================
-- EXPECTED RESULTS
-- ============================================================
--
-- All SQL queries should show ✅ PASS
-- All manual tests should work
-- If everything passes → FIX IS WORKING! 🎉
--
-- ============================================================
