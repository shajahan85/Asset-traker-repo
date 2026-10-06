# STEP BY STEP FIX - Run One Query at a Time

**Issue:** Assets BIDC1326, BIDC1544, BIDC1569 still freeze after initial SQL fix  
**Approach:** Run one query, send result, get fix, repeat

---

## STEP 1: Check if there are more corrupted IPs

**Linux team: Please run this ONE query in MySQL:**

```sql
SELECT COUNT(*) as total_corrupted
FROM assets_ipaddress ip
LEFT JOIN assets_assetipaddress aip ON aip.ip_address_id = ip.id
WHERE ip.is_assigned = 0 AND aip.asset_id IS NOT NULL;
```

**What to send back:** Just copy-paste the number you see.

**Expected result:**
- If you see `0` → Good! Move to STEP 2
- If you see a number > 0 → Send us the number and we'll give you the fix commands

---

## How to run the query:

```bash
# Connect to MySQL
mysql -u your_username -p your_database_name

# Then paste the query above
```

---

**After you send the result, we'll tell you what to do next.**

**Stop here and wait for instructions before running STEP 2.**
