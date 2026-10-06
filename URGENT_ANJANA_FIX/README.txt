========================================
URGENT FIX: Fields Disappearing When Editing
========================================
Date: 2026-09-22
Issue: When editing assets (e.g., Anjana's assets), fields disappear and show errors

PROBLEM IDENTIFIED:
-------------------
The recent performance optimization (limiting queries to 50 records) caused
a critical bug: If an asset's current branch/team/OS was NOT in the first 50
records alphabetically, it would NOT appear in the dropdown when editing.

This caused:
- Fields to appear empty when editing
- Validation errors when trying to save
- Data loss risk

AFFECTED ASSETS:
----------------
ANY asset where the current values are beyond the first 50 alphabetically:
- Branch not in top 50
- Operating System not in top 50  
- Team not in top 50

Example: Anjana's assets (BIDC1022, BIDC1443, BIDC1544, BIDC1204)

SOLUTION APPLIED:
-----------------
Modified asset_forms.py to ALWAYS include current values in querysets,
even if they're beyond the 50-record limit:

1. Branch dropdown: Includes current branch + top 49 others
2. Operating System dropdown: Includes current OS + top 49 others  
3. Team dropdowns: Includes current team + top 49 others

This ensures:
✓ Performance optimization remains (still limited to ~50 records)
✓ Current values ALWAYS appear in dropdowns
✓ No data loss when editing
✓ No validation errors

TESTING PERFORMED:
------------------
Tested all 4 of Anjana's assets:
- BIDC1022: ✓ PASS
- BIDC1443: ✓ PASS
- BIDC1544: ✓ PASS
- BIDC1204: ✓ PASS

All current values (branch, OS, teams) are included in querysets.

DEPLOYMENT:
-----------
1. Copy asset_forms.py to: /var/www/asset_tracker/assets/forms/
2. Run: sudo systemctl restart asset_tracker
3. Test editing any asset
4. Fields should now show current values and save properly

VERIFICATION:
-------------
After deployment:
1. Login to asset tracker
2. Edit any of Anjana's assets
3. All fields should show current values
4. Change any field (e.g., employee code)
5. Click Save
6. Should save successfully without errors
7. Values should NOT disappear

If issues persist, check browser console (F12) for JavaScript errors.

========================================
