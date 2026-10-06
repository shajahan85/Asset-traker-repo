# Guest IP Assignment - Quick Testing Guide

## Quick Start

**Server:** http://localhost:8000  
**Page:** http://localhost:8000/assets/ips/free/  
**Server Status:** ✅ Running (check with `list_processes` command)

---

## 1-Minute Smoke Test

If you just want to verify the feature works, do these quick tests:

### ✅ Test 1: Assign a Guest IP (30 seconds)
1. Go to http://localhost:8000/assets/ips/free/
2. Find a green "Free" IP
3. Click "Assign to Guest" button
4. Enter "Test Guest" in the modal
5. Click "Assign"
6. ✅ **Expected:** IP turns yellow/amber, shows "👤 Guest: Test Guest"

### ✅ Test 2: Release the Guest IP (15 seconds)
1. Find the yellow IP you just assigned
2. Click "Release" button
3. Confirm in the dialog
4. ✅ **Expected:** IP turns green, shows "Free" again

### ✅ Test 3: Search (15 seconds)
1. Assign an IP to "John Doe"
2. Type "John" in the search box
3. ✅ **Expected:** Only IPs with "John" in guest name shown

---

## Access Information

### Admin User (Required)
You'll need admin credentials to test this feature. If you don't have them:
```bash
python manage.py createsuperuser
```

### Regular User (For Authorization Testing)
Create a regular user to test that they CANNOT use guest IP features.

---

## Visual Reference

### What to Look For

**Free IP (Green):**
```
┌─────────────────┐
│  192.168.1.100  │
│      Free       │
│ [Assign to Guest] │
└─────────────────┘
```

**Guest IP (Yellow/Amber):**
```
┌─────────────────────┐
│   192.168.1.100     │
│ 👤 Guest: John Doe  │
│     [Release]       │
└─────────────────────┘
```

**Occupied IP (Red/Gray):**
```
┌─────────────────────┐
│   192.168.1.100     │
│ 💻 Asset: LAP-001   │
│   (No guest button) │
└─────────────────────┘
```

---

## Testing Checklist (Essential Tests Only)

Essential tests that must pass:

- [  ] **T1:** Assign free IP to guest → IP shows as occupied (yellow)
- [  ] **T2:** Release guest IP → IP shows as free (green)
- [  ] **T3:** Search by guest name → Results filtered correctly
- [  ] **T4:** Cannot assign occupied IP → No button visible
- [  ] **T5:** Cannot release non-guest IP → No button visible
- [  ] **T6:** Refresh page → Guest assignment persists
- [  ] **T7:** No console errors → Open DevTools and check
- [  ] **T8:** Regular users cannot assign → No buttons for non-admins

---

## Common Issues and Solutions

### Issue: Buttons Not Appearing
**Solution:** Make sure you're logged in as an admin user

### Issue: "404 Not Found" Error
**Solution:** URLs should be `/assets/guest-ip/assign/` (not `/guest-ip/assign/`)

### Issue: Modal Not Opening
**Solution:** Check browser console for JavaScript errors. Make sure `guest_ip_assignment.js` is loaded.

### Issue: No Free IPs Available
**Solution:** Create more IP ranges or release existing assigned IPs

---

## Database Verification Commands

Check database state at any time:

```bash
# Count free IPs
python manage.py shell -c "from assets.models import IPAddress; print(f'Free IPs: {IPAddress.objects.filter(is_assigned=False).count()}')"

# Count guest IPs
python manage.py shell -c "from assets.models import IPAddress; print(f'Guest IPs: {IPAddress.objects.filter(guest_name__isnull=False).count()}')"

# List all guest assignments
python manage.py shell -c "from assets.models import IPAddress; for ip in IPAddress.objects.filter(guest_name__isnull=False): print(f'{ip.address} -> {ip.guest_name}')"
```

---

## Full Test Report

For comprehensive testing, use: **GUEST_IP_MANUAL_TEST_REPORT.md**

That document contains:
- 15 detailed test cases
- Browser compatibility checklist
- Performance testing guidelines
- Defect tracking template
- Sign-off section

---

## Developer Tools Tips

### Console (F12 → Console Tab)
Watch for:
- ❌ Red errors (critical issues)
- ⚠️ Yellow warnings (may indicate problems)
- ✅ No errors = good!

### Network (F12 → Network Tab)
Check these requests succeed:
- `POST /assets/guest-ip/assign/` → 200 OK
- `POST /assets/guest-ip/release/` → 200 OK

### Example of Good Response:
```json
{
  "success": true,
  "message": "IP 192.168.1.100 assigned to John Doe",
  "ip_address": "192.168.1.100",
  "guest_name": "John Doe"
}
```

---

## Test Data Suggestions

Use these guest names for testing:
- ✅ **Normal names:** "John Doe", "Jane Smith", "Bob Wilson"
- ✅ **International:** "José García", "王小明", "François Müller"
- ✅ **Special chars:** "O'Brien", "Mary-Jane", "Jean-Paul"
- ✅ **Long names:** "Christopher Alexander Montgomery-Wellington III"
- ✅ **Edge cases:** 150-character name (boundary test)

---

## Quick Troubleshooting

**Problem:** Feature not working at all  
**Check:**
1. Is server running? → `list_processes`
2. Are you logged in as admin?
3. Are there free IPs? → Check database
4. Any console errors? → Open DevTools

**Problem:** Tests failing  
**Check:**
1. Using correct URL prefix? → `/assets/guest-ip/...`
2. CSRF token present? → Check Network tab
3. Database migration applied? → Run `python manage.py migrate`

---

## Success Criteria Summary

The feature is **ready for production** when:

✅ All 8 essential tests pass  
✅ No JavaScript console errors  
✅ AJAX operations complete in <1 second  
✅ UI matches existing design patterns  
✅ No regressions in existing features  
✅ Works on Chrome, Firefox, and Edge  

---

## Next Steps After Testing

1. **If all tests pass:**
   - Complete the full test report
   - Sign off on GUEST_IP_MANUAL_TEST_REPORT.md
   - Mark Task 11 as complete
   - Feature is ready for production

2. **If tests fail:**
   - Document failures in test report
   - Create bug tickets for issues found
   - Notify development team
   - Retest after fixes

---

## Quick Commands Reference

```bash
# Start server (if not running)
python manage.py runserver 0.0.0.0:8000

# Check server processes
# Use: list_processes tool

# Create test admin user
python manage.py createsuperuser

# Access the feature
# Navigate to: http://localhost:8000/assets/ips/free/

# View server logs
# Use: get_process_output tool with terminalId=1
```

---

**Ready to test?** Go to: http://localhost:8000/assets/ips/free/

**Need help?** Check GUEST_IP_MANUAL_TEST_REPORT.md for detailed test cases
