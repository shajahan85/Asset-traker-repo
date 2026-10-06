# Server Controller Team Filter Fix

**Issue:** Server control page team filter shows all teams including non-technical teams  
**Fix:** Exclude non-relevant teams from the filter dropdown

---

## TEAMS EXCLUDED FROM FILTER

The following teams will NOT appear in the server controller team filter:

1. Accounts team
2. iBOSS Support team
3. BA team
4. Hotel team
5. HR team
6. Marketing team
7. Developers
8. Test teams
9. Not Applicable
10. Server controllers

**Only technical/operational teams will be shown in the filter.**

---

## FILE TO UPLOAD

**File:** `views_server_controller.py`  
**Upload to:** `/var/www/asset_tracker/assets/views_server_controller.py`

---

## DEPLOYMENT STEPS

### 1. Backup Current File

```bash
cd /var/www/asset_tracker/assets/
sudo cp views_server_controller.py views_server_controller.py.backup_$(date +%Y%m%d_%H%M%S)
```

### 2. Upload New File

**Using WinSCP/FileZilla:**
- Upload `SERVER_CONTROLLER_TEAM_FILTER_FIX\views_server_controller.py`
- To: `/var/www/asset_tracker/assets/views_server_controller.py`
- Overwrite existing file

**Using scp:**
```powershell
scp "d:\Asset tracker\SERVER_CONTROLLER_TEAM_FILTER_FIX\views_server_controller.py" username@server:/tmp/
```

Then on server:
```bash
sudo mv /tmp/views_server_controller.py /var/www/asset_tracker/assets/views_server_controller.py
sudo chown www-data:www-data /var/www/asset_tracker/assets/views_server_controller.py
sudo chmod 644 /var/www/asset_tracker/assets/views_server_controller.py
```

### 3. Restart Django

```bash
sudo systemctl restart asset_tracker
sudo systemctl status asset_tracker
```

**Expected:** Green `Active: active (running)`

---

## TESTING

1. Go to Server Controllers page
2. Click on the "Team" filter dropdown
3. **Verify:** Should NOT see:
   - Accounts team
   - iBOSS Support team
   - BA team
   - Hotel team
   - HR team
   - Marketing team
   - Developers
   - Test teams
   - Not Applicable
   - Server controllers

4. **Should see:** Only technical/operational teams relevant to server management

---

## CODE CHANGE

**Location:** Line 112-115 in `views_server_controller.py`

**Before:**
```python
context['teams'] = Team.objects.all().order_by('name')
```

**After:**
```python
excluded_teams = [
    'Accounts team', 'iBOSS Support team', 'BA team', 'Hotel team',
    'HR team', 'Marketing team', 'Developers', 'Test teams',
    'Not Applicable', 'Server controllers'
]
context['teams'] = Team.objects.exclude(name__in=excluded_teams).order_by('name')
```

---

## NOTES

- This only affects the team filter dropdown on the Server Controllers page
- The excluded teams are **case-sensitive** - must match exactly as in database
- If team names in your database are slightly different (e.g., "Accounts Team" vs "Accounts team"), the exclusion won't work
- To verify team names in database, run:

```sql
SELECT name FROM assets_team ORDER BY name;
```

---

## ROLLBACK

If needed, restore the backup:

```bash
cd /var/www/asset_tracker/assets/
sudo cp views_server_controller.py.backup_* views_server_controller.py
sudo systemctl restart asset_tracker
```

---

## TIME REQUIRED

- Upload: 2 minutes
- Restart: 1 minute
- Testing: 1 minute

**Total: ~4 minutes**

---

**Simple fix, immediate improvement!** 👍
