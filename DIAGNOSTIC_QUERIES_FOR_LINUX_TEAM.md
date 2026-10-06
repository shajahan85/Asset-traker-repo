# DIAGNOSTIC QUERIES FOR FREEZE BUG - RUN ON LINUX SERVER

**Date:** February 4, 2026  
**Issue:** Assets BIDC1326, BIDC1544, BIDC1569 still freeze after SQL fix  
**Status:** Need to run these queries to find the root cause

---

## INSTRUCTIONS FOR LINUX TEAM

Please run these SQL queries in MySQL and send back the results.

### How to run these queries:

```bash
# Connect to MySQL
mysql -u your_username -p your_database_name

# Or if you have a specific config:
mysql -u root -p asset_tracker
```

Then copy-paste each query below and send us the output.

---

## QUERY 1: Check if there are MORE corrupted IPs

This checks if there are additional IP addresses with the same corruption pattern we fixed before.

```sql
SELECT COUNT(*) as total_corrupted
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**Expected:** Should be 0 (zero). If it's > 0, we have more corrupted data.

---

## QUERY 2: Check the problem assets in detail

This shows the IP addresses assigned to the three problem assets.

```sql
SELECT 
    a.id, 
    a.asset_tag, 
    a.asset_name, 
    COUNT(aip.id) as ip_count,
    GROUP_CONCAT(ip.id) as ip_ids,
    GROUP_CONCAT(ip.address) as ip_addresses,
    GROUP_CONCAT(ip.is_assigned) as ip_assigned_flags
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_ipaddress ip ON ip.id = aip.ip_address_id
WHERE a.asset_tag IN ('BIDC1326', 'BIDC1544', 'BIDC1569')
GROUP BY a.id, a.asset_tag, a.asset_name;
```

**Expected:** Should show the IPs for each asset with is_assigned = 1 for all.

---

## QUERY 3: Check for duplicate asset tags

```sql
SELECT asset_tag, COUNT(*) as count 
FROM assets_asset 
WHERE asset_tag IN ('BIDC1326', 'BIDC1544', 'BIDC1569')
GROUP BY asset_tag 
HAVING count > 1;
```

**Expected:** Should return no rows (no duplicates).

---

## QUERY 4: Check for orphaned IP relationships

```sql
SELECT COUNT(*) as orphaned_count
FROM assets_assetipaddress aip
LEFT JOIN assets_asset a ON a.id = aip.asset_id
WHERE a.id IS NULL;
```

**Expected:** Should be 0 (zero).

---

## QUERY 5: Verify the 14 IPs we fixed earlier

```sql
SELECT 
    ip.id, 
    ip.address, 
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.asset_id,
    a.asset_tag
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.id = aip.asset_id
WHERE ip.id IN (1084, 1141, 1028, 1678, 1486, 1587, 1437, 1656, 1167, 1714, 1414, 1768, 1417, 1106)
ORDER BY ip.id;
```

**Expected:** All should have `is_assigned = 1`.

---

## QUERY 6: Check for ALL corrupted IPs (full scan)

This is a more comprehensive check to find ANY IP with corruption.

```sql
SELECT 
    ip.id,
    ip.address,
    ip.is_assigned,
    ip.assigned_to_asset_id,
    aip.asset_id as relationship_asset_id,
    a.asset_tag
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
LEFT JOIN assets_asset a ON a.id = aip.asset_id
WHERE (ip.is_assigned = 0 AND aip.asset_id IS NOT NULL)
   OR (ip.is_assigned = 1 AND aip.asset_id IS NULL)
   OR (ip.assigned_to_asset_id IS NOT NULL AND ip.assigned_to_asset_id != aip.asset_id);
```

**Expected:** Should return 0 rows (no corruption).

---

## QUERY 7: Check the specific problem assets for any anomalies

```sql
SELECT 
    a.id,
    a.asset_tag,
    a.asset_name,
    a.status,
    a.employee_code,
    a.is_freed,
    COUNT(DISTINCT aip.id) as ip_relationship_count,
    COUNT(DISTINCT si.id) as secondary_ip_count
FROM assets_asset a
LEFT JOIN assets_assetipaddress aip ON aip.asset_id = a.id
LEFT JOIN assets_secondaryipaddress si ON si.asset_id = a.id
WHERE a.asset_tag IN ('BIDC1326', 'BIDC1544', 'BIDC1569')
GROUP BY a.id, a.asset_tag, a.asset_name, a.status, a.employee_code, a.is_freed;
```

---

## QUERY 8: Enable slow query logging (to catch what's freezing)

**IMPORTANT:** Run these commands, then try to update BIDC1326 in the browser.

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 2;
SET GLOBAL log_queries_not_using_indexes = 'ON';
SHOW VARIABLES LIKE 'slow_query_log%';
```

After running these, try to update asset BIDC1326 in the browser (let it freeze for 30 seconds), then run:

```bash
sudo tail -100 /var/log/mysql/mysql-slow.log
```

Or if the log file is in a different location:

```bash
sudo tail -100 /var/lib/mysql/$(hostname)-slow.log
```

Send us the last 100 lines from the slow query log.

---

## ADDITIONAL CHECK: Django Application Log

While the page is freezing, check the Django application log for any errors:

```bash
sudo tail -f /var/log/asset_tracker/error.log
```

Or wherever your Django logs are located. Look for:
- Database timeout errors
- Lock wait timeout errors
- Any ERROR or WARNING messages

---

## SUMMARY OF WHAT TO SEND BACK

Please send us:

1. ✅ Results of Query 1 (corrupted IP count)
2. ✅ Results of Query 2 (problem assets details)
3. ✅ Results of Query 3 (duplicate check)
4. ✅ Results of Query 4 (orphaned IPs)
5. ✅ Results of Query 5 (verify our 14 fixed IPs)
6. ✅ Results of Query 6 (full corruption scan)
7. ✅ Results of Query 7 (asset anomalies)
8. ✅ The slow query log output after trying to update BIDC1326
9. ✅ Any Django error log messages during the freeze

---

## ALTERNATIVE: If you can't access slow query log

If you cannot enable slow query logging, try this instead:

**While the page is freezing, run this in MySQL:**

```sql
SHOW FULL PROCESSLIST;
```

This will show what queries are currently running. Send us the output, especially any queries that are in "Locked" or "Waiting" state.

---

**Once we have these results, we can identify the exact cause of the freeze and fix it.**
