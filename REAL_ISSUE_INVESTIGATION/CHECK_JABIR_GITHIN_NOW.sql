-- ============================================================
-- IMMEDIATE DIAGNOSTIC - Check Jabir and Githin Right Now
-- Run these queries to see EXACTLY why their updates are failing
-- ============================================================

-- Query 1: Show ALL IP records for Jabir (BIDC1419)
SELECT 
    'JABIR (BIDC1419) - ALL IPs' as asset,
    aip.id as record_id,
    aip.is_primary,
    aip.ip_label as label,
    COALESCE(ip.address, aip.manual_ip, '(NONE)') as ip_value,
    ip.id as managed_ip_id,
    ip.is_assigned as managed_ip_assigned,
    aip.manual_ip as manual_ip_text
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1419'
ORDER BY aip.is_primary DESC, aip.id;

-- Query 2: Show ALL IP records for Githin (BIDC1420)
SELECT 
    'GITHIN (BIDC1420) - ALL IPs' as asset,
    aip.id as record_id,
    aip.is_primary,
    aip.ip_label as label,
    COALESCE(ip.address, aip.manual_ip, '(NONE)') as ip_value,
    ip.id as managed_ip_id,
    ip.is_assigned as managed_ip_assigned,
    aip.manual_ip as manual_ip_text
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1420'
ORDER BY aip.is_primary DESC, aip.id;

-- Query 3: Check for duplicate IPs on Jabir's asset
SELECT 
    'JABIR DUPLICATE CHECK' as test,
    COALESCE(ip.address, aip.manual_ip) as ip_value,
    COUNT(*) as count,
    GROUP_CONCAT(CONCAT('RecordID:', aip.id, ',Primary:', aip.is_primary, ',Label:', COALESCE(aip.ip_label, 'none'))) as all_records
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1419'
GROUP BY COALESCE(ip.address, aip.manual_ip)
HAVING COUNT(*) > 1;

-- Query 4: Check for duplicate IPs on Githin's asset
SELECT 
    'GITHIN DUPLICATE CHECK' as test,
    COALESCE(ip.address, aip.manual_ip) as ip_value,
    COUNT(*) as count,
    GROUP_CONCAT(CONCAT('RecordID:', aip.id, ',Primary:', aip.is_primary, ',Label:', COALESCE(aip.ip_label, 'none'))) as all_records
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1420'
GROUP BY COALESCE(ip.address, aip.manual_ip)
HAVING COUNT(*) > 1;

-- Query 5: Check for NULL/empty IPs on Jabir's asset
SELECT 
    'JABIR NULL IP CHECK' as test,
    aip.id as record_id,
    aip.is_primary,
    aip.ip_label,
    aip.ip_address_id,
    aip.manual_ip,
    CASE 
        WHEN aip.ip_address_id IS NULL AND (aip.manual_ip IS NULL OR aip.manual_ip = '') THEN '❌ NULL IP FOUND!'
        ELSE '✅ Has IP'
    END as status
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
WHERE a.asset_tag = 'BIDC1419';

-- Query 6: Check for NULL/empty IPs on Githin's asset
SELECT 
    'GITHIN NULL IP CHECK' as test,
    aip.id as record_id,
    aip.is_primary,
    aip.ip_label,
    aip.ip_address_id,
    aip.manual_ip,
    CASE 
        WHEN aip.ip_address_id IS NULL AND (aip.manual_ip IS NULL OR aip.manual_ip = '') THEN '❌ NULL IP FOUND!'
        ELSE '✅ Has IP'
    END as status
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
WHERE a.asset_tag = 'BIDC1420';

-- ============================================================
-- INTERPRETATION GUIDE
-- ============================================================
--
-- QUERY 1 & 2 (All IPs):
-- Expected: 1 row with is_primary=1, possibly more with is_primary=0
-- Problem: If you see multiple rows with SAME ip_value
--
-- QUERY 3 & 4 (Duplicate check):
-- Expected: Empty result (no duplicates)
-- Problem: If returns rows, those IPs are duplicated
--          → This is WHY the form won't submit!
--
-- QUERY 5 & 6 (NULL check):
-- Expected: All rows show "✅ Has IP"
-- Problem: If any show "❌ NULL IP FOUND!"
--          → This also blocks form submission!
--
-- ============================================================
-- WHAT TO DO NEXT
-- ============================================================
--
-- If Query 3 or 4 shows duplicates:
--   1. Note the record IDs
--   2. Delete the duplicate records (keep primary, delete extras)
--   3. Try updating the asset again
--
-- If Query 5 or 6 shows NULL IPs:
--   1. Note the record IDs
--   2. Either add an IP to that record, or delete it
--   3. Try updating the asset again
--
-- Example fix for duplicate:
--   DELETE FROM assets_assetipaddress WHERE id = XXX;
--   (Replace XXX with the duplicate record ID to remove)
--
-- Example fix for NULL IP:
--   DELETE FROM assets_assetipaddress WHERE id = XXX;
--   (Replace XXX with the NULL record ID to remove)
--
-- ============================================================

-- Query 7: Show what the formset validation is checking
-- This simulates the validation that's failing
SELECT 
    'VALIDATION SIMULATION' as test,
    a.asset_tag,
    'Primary IP:' as ip_type,
    COALESCE(primary_ip.address, primary_aip.manual_ip) as primary_ip_value,
    GROUP_CONCAT(
        DISTINCT COALESCE(additional_ip.address, additional_aip.manual_ip)
        ORDER BY additional_aip.id
    ) as additional_ips,
    CASE 
        WHEN COALESCE(primary_ip.address, primary_aip.manual_ip) IN (
            SELECT COALESCE(ip.address, aip.manual_ip)
            FROM assets_assetipaddress aip
            LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
            WHERE aip.asset_id = a.id AND aip.is_primary = 0
        ) THEN '❌ FAIL: Primary IP duplicated in additional IPs'
        ELSE '✅ PASS: No duplicate'
    END as validation_result
FROM assets_asset a
LEFT JOIN assets_assetipaddress primary_aip ON primary_aip.asset_id = a.id AND primary_aip.is_primary = 1
LEFT JOIN assets_ipaddress primary_ip ON primary_ip.id = primary_aip.ip_address_id
LEFT JOIN assets_assetipaddress additional_aip ON additional_aip.asset_id = a.id AND additional_aip.is_primary = 0
LEFT JOIN assets_ipaddress additional_ip ON additional_ip.id = additional_aip.ip_address_id
WHERE a.asset_tag IN ('BIDC1419', 'BIDC1420')
GROUP BY a.id, a.asset_tag, primary_ip.address, primary_aip.manual_ip;
