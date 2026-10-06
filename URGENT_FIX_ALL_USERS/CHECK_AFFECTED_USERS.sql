-- ============================================================
-- SQL QUERIES TO IDENTIFY HOW MANY USERS ARE AFFECTED
-- Run these BEFORE deploying to understand the scope
-- ============================================================

-- Query 1: Count free IPs by range
-- This shows how many free IPs exist in each range
SELECT 
    CASE 
        WHEN address LIKE '10.%' THEN '10.x range'
        WHEN address LIKE '192.168.11.%' THEN '192.168.11.x range'
        WHEN address LIKE '192.168.50.%' THEN '192.168.50.x range'
        WHEN address LIKE '192.168.60.%' THEN '192.168.60.x range'
        WHEN address LIKE '192.168.70.%' THEN '192.168.70.x range'
        WHEN address LIKE '192.168.99.%' THEN '192.168.99.x range'
        ELSE 'Other ranges'
    END as ip_range,
    COUNT(*) as free_ip_count
FROM assets_ipaddress
WHERE is_assigned = 0
GROUP BY ip_range
ORDER BY ip_range;

-- Query 2: Total free IPs
-- If this is > 200, the bug is definitely affecting some users
SELECT COUNT(*) as total_free_ips
FROM assets_ipaddress
WHERE is_assigned = 0;

-- Query 3: Count how many free IPs sort BEFORE 70.x range
-- If this is > 200, then ALL 70.x users are affected
SELECT COUNT(*) as free_ips_before_70x
FROM assets_ipaddress
WHERE is_assigned = 0 
AND address < '192.168.70.0';

-- Query 4: List ALL assets with IPs in 70.x range
-- These are the users currently affected by the bug
SELECT 
    a.id,
    a.asset_tag,
    a.assigned_to,
    a.system_type,
    ip.address,
    ip.is_assigned
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.address LIKE '192.168.70.%'
ORDER BY ip.address;

-- Query 5: Count assets by IP range
-- Shows distribution of users across ranges
SELECT 
    CASE 
        WHEN ip.address LIKE '10.%' THEN '10.x range'
        WHEN ip.address LIKE '192.168.11.%' THEN '192.168.11.x range'
        WHEN ip.address LIKE '192.168.50.%' THEN '192.168.50.x range'
        WHEN ip.address LIKE '192.168.60.%' THEN '192.168.60.x range'
        WHEN ip.address LIKE '192.168.70.%' THEN '192.168.70.x range'
        WHEN ip.address LIKE '192.168.99.%' THEN '192.168.99.x range'
        ELSE 'Other ranges'
    END as ip_range,
    COUNT(*) as asset_count
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
GROUP BY ip_range
ORDER BY ip_range;

-- Query 6: List ALL assets with IPs in 11.x range
-- These users are also likely affected
SELECT 
    a.id,
    a.asset_tag,
    a.assigned_to,
    a.system_type,
    ip.address,
    ip.is_assigned
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE ip.address LIKE '192.168.11.%'
ORDER BY ip.address;

-- Query 7: Find position of first 70.x IP in sorted free IP list
-- If this number > 200, then 70.x IPs are being excluded
SELECT 
    @rownum := @rownum + 1 AS position,
    address
FROM 
    assets_ipaddress,
    (SELECT @rownum := 0) r
WHERE 
    is_assigned = 0
ORDER BY 
    address
LIMIT 250;
-- Look for where 192.168.70.x first appears in this list

-- Query 8: Calculate exact position of Jabir's IP if it were free
-- Shows where 192.168.70.34 would rank
SELECT COUNT(*) + 1 as position_if_free
FROM assets_ipaddress
WHERE is_assigned = 0 
AND address < '192.168.70.34';

-- Query 9: Calculate exact position of Githin's IP if it were free
-- Shows where 192.168.70.85 would rank
SELECT COUNT(*) + 1 as position_if_free
FROM assets_ipaddress
WHERE is_assigned = 0 
AND address < '192.168.70.85';

-- Query 10: Summary report
-- Quick overview of the problem scope
SELECT 
    (SELECT COUNT(*) FROM assets_ipaddress WHERE is_assigned = 0) as total_free_ips,
    (SELECT COUNT(*) FROM assets_ipaddress WHERE is_assigned = 0 AND address < '192.168.70.0') as free_before_70x,
    (SELECT COUNT(*) FROM assets_asset a 
     JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
     JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
     WHERE ip.address LIKE '192.168.70.%') as total_70x_users,
    (SELECT COUNT(*) FROM assets_asset a 
     JOIN assets_assetipaddress aip ON aip.asset_id = a.id AND aip.is_primary = 1
     JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
     WHERE ip.address LIKE '192.168.11.%') as total_11x_users;

-- ============================================================
-- INTERPRETATION GUIDE
-- ============================================================
-- 
-- If Query 2 (total_free_ips) > 200:
--   → The 200 limit is cutting off some IPs
--
-- If Query 3 (free_before_70x) > 200:
--   → ALL 70.x users are affected
--   → Count from Query 4 = number of affected users
--
-- If Query 3 (free_before_70x) > 200 AND Query 4 shows many users:
--   → URGENT: Many users cannot edit their assets
--
-- Query 10 gives you the summary:
--   - If free_before_70x > 200 AND total_70x_users > 0
--     → Deploy immediately! Multiple users affected
--
-- ============================================================
