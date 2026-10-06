-- =====================================================
-- DIAGNOSTIC QUERIES FOR IP DROPDOWN BUG
-- Run these to confirm the bug and verify the fix
-- =====================================================

-- Query 1: Count total free IPs in the system
-- If this is > 200, the limit could be causing issues
SELECT COUNT(*) as total_free_ips 
FROM assets_ipaddress 
WHERE is_assigned=0;

-- Query 2: Count free IPs that sort BEFORE 70.x range
-- If this is > 200, then 70.x IPs are being cut off by the limit
SELECT COUNT(*) as free_ips_before_70_range
FROM assets_ipaddress 
WHERE is_assigned=0 AND address < '192.168.70.0';

-- Query 3: Show Jabir's current IP assignment
-- Should show IP 192.168.70.34 with is_assigned=1
SELECT 
    a.asset_tag,
    a.assigned_to,
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    aip.is_primary
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1419';

-- Query 4: Show Githin's current IP assignment
-- Should show IP 192.168.70.85 with is_assigned=1
SELECT 
    a.asset_tag,
    a.assigned_to,
    ip.id as ip_id,
    ip.address,
    ip.is_assigned,
    aip.is_primary
FROM assets_asset a
JOIN assets_assetipaddress aip ON aip.asset_id = a.id
JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag = 'BIDC1420';

-- Query 5: Show first 200 free IPs ordered by address
-- This simulates what the OLD code was doing
-- Check if 70.x IPs appear in this list
SELECT id, address, is_assigned
FROM assets_ipaddress
WHERE is_assigned=0
ORDER BY address
LIMIT 200;

-- Query 6: Show last 5 IPs from the first 200 free IPs
-- This shows where the cutoff happens
SELECT id, address, is_assigned
FROM assets_ipaddress
WHERE is_assigned=0
ORDER BY address
LIMIT 5 OFFSET 195;

-- Query 7: Count free IPs in each major range
-- Shows distribution of free IPs across ranges
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
    COUNT(*) as free_count
FROM assets_ipaddress
WHERE is_assigned=0
GROUP BY ip_range
ORDER BY ip_range;

-- Query 8: Show what position Jabir's IP would be in if it were free
-- This calculates where 192.168.70.34 would rank if sorted with free IPs
SELECT COUNT(*) + 1 as position_in_sorted_list
FROM assets_ipaddress
WHERE is_assigned=0 AND address < '192.168.70.34';

-- Query 9: Show what position Githin's IP would be in if it were free
-- This calculates where 192.168.70.85 would rank if sorted with free IPs
SELECT COUNT(*) + 1 as position_in_sorted_list
FROM assets_ipaddress
WHERE is_assigned=0 AND address < '192.168.70.85';

-- =====================================================
-- INTERPRETATION OF RESULTS
-- =====================================================
-- 
-- If Query 1 (total_free_ips) > 200:
--   → The 200 limit is definitely cutting off some IPs
--
-- If Query 2 (free_ips_before_70_range) > 200:
--   → The 70.x range IPs are AFTER the cutoff
--   → This confirms the bug affecting Jabir/Githin
--
-- If Query 8 or Query 9 returns value > 200:
--   → That IP would be at position > 200 if sorted with free IPs
--   → The OLD code would exclude it from the dropdown
--   → This confirms the bug for that specific asset
--
-- If Query 3 and Query 4 show is_assigned=1:
--   → IPs are correctly assigned (no corruption)
--   → The issue is purely the dropdown limit bug
--
-- If Query 7 shows large counts for 10.x, 50.x, 60.x ranges:
--   → Those ranges fill up the first 200 slots
--   → Higher ranges (70.x, 11.x) get excluded
-- =====================================================
