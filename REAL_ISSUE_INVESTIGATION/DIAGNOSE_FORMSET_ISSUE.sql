-- ============================================================
-- DIAGNOSE THE REAL ISSUE - Additional IP Formset Validation
-- The problem is NOT the IP dropdown - it's formset validation failing silently
-- ============================================================

-- Query 1: Check if Jabir has duplicate IPs
-- Primary IP vs Additional IPs
SELECT 
    'JABIR DUPLICATE CHECK' as test_name,
    a.asset_tag,
    aip.id as record_id,
    aip.is_primary,
    COALESCE(ip.address, aip.manual_ip) as ip_value,
    COUNT(*) OVER (PARTITION BY COALESCE(ip.address, aip.manual_ip)) as duplicate_count
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1419'
ORDER BY aip.is_primary DESC, ip_value;

-- Query 2: Check if Githin has duplicate IPs
SELECT 
    'GITHIN DUPLICATE CHECK' as test_name,
    a.asset_tag,
    aip.id as record_id,
    aip.is_primary,
    COALESCE(ip.address, aip.manual_ip) as ip_value,
    COUNT(*) OVER (PARTITION BY COALESCE(ip.address, aip.manual_ip)) as duplicate_count
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1420'
ORDER BY aip.is_primary DESC, ip_value;

-- Query 3: Find ALL assets with duplicate IP assignments
-- This is the REAL problem causing form validation to fail
SELECT 
    a.asset_tag,
    a.assigned_to,
    COALESCE(ip.address, aip.manual_ip) as ip_value,
    COUNT(*) as count,
    GROUP_CONCAT(CONCAT(aip.id, ':', aip.is_primary)) as record_details
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
GROUP BY a.id, a.asset_tag, a.assigned_to, ip_value
HAVING COUNT(*) > 1
ORDER BY a.asset_tag;

-- Query 4: Find assets with BOTH primary=1 and additional with same IP
-- This causes "This IP is already assigned to this asset" error
SELECT 
    'DUPLICATE PRIMARY VS ADDITIONAL' as issue_type,
    a.asset_tag,
    a.assigned_to,
    primary_ip.ip_value as primary_ip,
    additional_ip.ip_value as additional_ip,
    'SAME IP IN PRIMARY AND ADDITIONAL!' as problem
FROM assets_asset a
CROSS JOIN LATERAL (
    SELECT COALESCE(ip.address, aip.manual_ip) as ip_value
    FROM assets_assetipaddress aip
    LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
    WHERE aip.asset_id = a.id AND aip.is_primary = 1
    LIMIT 1
) primary_ip
CROSS JOIN LATERAL (
    SELECT COALESCE(ip.address, aip.manual_ip) as ip_value
    FROM assets_assetipaddress aip
    LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
    WHERE aip.asset_id = a.id AND aip.is_primary = 0
) additional_ip
WHERE primary_ip.ip_value = additional_ip.ip_value;

-- Query 5: Check for NULL or empty IP values in additional IPs
-- These might cause validation issues
SELECT 
    'NULL/EMPTY IP CHECK' as issue_type,
    a.asset_tag,
    aip.id,
    aip.is_primary,
    aip.ip_address_id,
    aip.manual_ip,
    ip.address as managed_ip_address
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE aip.ip_address_id IS NULL AND (aip.manual_ip IS NULL OR aip.manual_ip = '')
ORDER BY a.asset_tag;

-- Query 6: List ALL additional IPs for affected users
-- Shows complete picture of what's in the database
SELECT 
    a.asset_tag,
    a.assigned_to,
    aip.id as record_id,
    aip.is_primary,
    aip.ip_label,
    COALESCE(ip.address, aip.manual_ip, '(NONE)') as ip_value,
    aip.ip_address_id as managed_ip_id,
    aip.manual_ip as manual_ip_text
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag IN ('BIDC1419', 'BIDC1420')
ORDER BY a.asset_tag, aip.is_primary DESC, aip.id;

-- Query 7: Find users with additional IP formset issues
-- Assets that have additional IPs (any asset with >1 IP record)
SELECT 
    a.asset_tag,
    a.assigned_to,
    a.system_type,
    COUNT(aip.id) as total_ips,
    SUM(CASE WHEN aip.is_primary = 1 THEN 1 ELSE 0 END) as primary_count,
    SUM(CASE WHEN aip.is_primary = 0 THEN 1 ELSE 0 END) as additional_count
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.id
GROUP BY a.id, a.asset_tag, a.assigned_to, a.system_type
HAVING COUNT(aip.id) > 1
ORDER BY total_ips DESC, a.asset_tag;

-- ============================================================
-- INTERPRETATION
-- ============================================================
--
-- If Query 3 shows results:
--   → These assets have duplicate IPs
--   → Formset validation WILL FAIL
--   → User cannot update these assets
--
-- If Query 4 shows results:
--   → Primary IP same as an additional IP
--   → This triggers "already assigned" validation error
--   → User sees nothing, just "no response" when clicking Update
--
-- If Query 5 shows results:
--   → Additional IP records with no IP value
--   → These cause formset validation to fail
--
-- If Query 6 shows multiple records for Jabir/Githin:
--   → They have additional IPs configured
--   → Check if any are duplicates or null
--
-- If Query 7 shows many results:
--   → Many users affected (not just Jabir/Githin)
--   → ALL these users cannot update their assets
--
-- ============================================================
