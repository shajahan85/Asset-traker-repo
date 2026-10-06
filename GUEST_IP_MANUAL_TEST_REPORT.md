# Guest IP Assignment Feature - Manual Testing Report

**Feature:** Guest IP Assignment for Asset Tracker  
**Test Date:** {{ TO BE COMPLETED }}  
**Tester:** {{ TO BE COMPLETED }}  
**Django Server:** http://localhost:8000  
**Status:** Ready for Testing

---

## Pre-Testing Verification

### ✅ Implementation Checklist
- [x] Model changes applied (IPAddress with guest fields)
- [x] Database migration completed (0018_add_guest_ip_fields)
- [x] Service methods implemented (assign_ip_to_guest, release_guest_ip)
- [x] Views created (GuestIPAssignView, GuestIPReleaseView)
- [x] URL routes configured (/assets/guest-ip/assign/, /assets/guest-ip/release/)
- [x] Template updated with guest UI elements
- [x] CSS styling added for guest IPs
- [x] JavaScript module created (guest_ip_assignment.js)
- [x] Search functionality updated to include guest names
- [x] Django server running successfully

### Database Status
- **Total IPs:** 1015
- **Free IPs:** 674 (available for guest assignment)
- **Guest IPs:** 0 (none assigned yet)

---

## Test Environment

**Access Requirements:**
- Admin user credentials required
- Regular users should NOT have access to guest IP features
- Navigate to: http://localhost:8000/assets/ips/free/

---

## Manual Test Cases

### Test Case 1: Assign Free IP to Guest "John Doe"

**Objective:** Verify that a free IP can be assigned to a guest and shows as occupied

**Pre-conditions:**
- Logged in as admin user
- At least one free IP available

**Steps:**
1. Navigate to Free IPs page (http://localhost:8000/assets/ips/free/)
2. Locate a free IP address (green background, shows "Free" status)
3. Click the "Assign to Guest" button on a free IP
4. Verify modal opens with title "Assign IP to Guest"
5. Verify the selected IP address is displayed in the modal
6. Enter "John Doe" in the Guest Name field
7. Click "Assign" button
8. Wait for the page to reload

**Expected Results:**
- [  ] Modal opens successfully
- [  ] IP address is correctly displayed in modal
- [  ] Guest name input field is functional
- [  ] After assignment, IP shows with yellow/amber background
- [  ] IP displays guest indicator: 👤 Guest: John Doe
- [  ] IP now shows "Release" button instead of "Assign to Guest"
- [  ] IP no longer appears in the "Free" section
- [  ] Success message appears briefly
- [  ] No JavaScript console errors

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 2: Release Guest IP

**Objective:** Verify that a guest-assigned IP can be released and returns to free status

**Pre-conditions:**
- At least one IP assigned to a guest (from Test Case 1)

**Steps:**
1. Locate the guest-assigned IP (John Doe from Test Case 1)
2. Click the "Release" button
3. Verify browser confirmation dialog appears
4. Confirm that the dialog shows: "Release IP [IP_ADDRESS] from guest John Doe?"
5. Click "OK" in the confirmation dialog
6. Wait for the page to reload

**Expected Results:**
- [  ] Release button is visible on guest-assigned IP
- [  ] Confirmation dialog appears with correct IP and guest name
- [  ] After release, IP shows with green background
- [  ] IP displays "Free" status
- [  ] "Assign to Guest" button appears again
- [  ] Guest name no longer displayed
- [  ] Success message appears briefly
- [  ] No JavaScript console errors

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 3: Search for Guest by Name

**Objective:** Verify search functionality includes guest names

**Pre-conditions:**
- At least one IP assigned to a guest named "John"

**Steps:**
1. Assign an IP to guest "John Smith" (if not already done)
2. Locate the search box at the top of the page
3. Type "John" in the search box
4. Observe the filtered results

**Expected Results:**
- [  ] Search box filters IPs in real-time
- [  ] Guest-assigned IPs with "John" in the name appear in results
- [  ] Guest indicator (👤) is visible in search results
- [  ] Other IPs are hidden from view
- [  ] Clearing search shows all IPs again

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 4: Try to Assign Already-Assigned IP

**Objective:** Verify error handling for assigning an already-assigned IP

**Pre-conditions:**
- At least one IP already assigned (to asset, VM, network device, or guest)

**Steps:**
1. Locate an IP that is already assigned (not free)
2. Verify that "Assign to Guest" button is NOT visible on assigned IPs
3. Attempt to directly POST to /assets/guest-ip/assign/ with an assigned IP's ID (using browser dev tools or curl)

**Expected Results:**
- [  ] "Assign to Guest" button only appears on free IPs
- [  ] Occupied IPs (red background) do not show the assign button
- [  ] If directly POSTing, receive error message: "This IP address is already assigned"
- [  ] HTTP 400 error code returned
- [  ] IP remains in its current assigned state

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 5: Try to Release Non-Guest IP

**Objective:** Verify that only guest-assigned IPs can be released via guest release workflow

**Pre-conditions:**
- At least one IP assigned to an asset, VM, or network device (not guest)

**Steps:**
1. Locate an IP assigned to an asset/VM/network device
2. Verify that "Release" button is NOT visible on these IPs
3. Attempt to directly POST to /assets/guest-ip/release/ with a non-guest IP's ID

**Expected Results:**
- [  ] "Release" button only appears on guest-assigned IPs
- [  ] Asset/VM/Network Device IPs do not show the release button
- [  ] If directly POSTing, receive error message: "This IP is not assigned to a guest"
- [  ] HTTP 400 error code returned
- [  ] IP remains in its current assigned state

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 6: Persistence Test

**Objective:** Verify that guest assignments persist across page refreshes

**Pre-conditions:**
- At least one IP assigned to a guest

**Steps:**
1. Assign an IP to guest "Test Persistence"
2. Note the IP address assigned
3. Wait for success message and page reload
4. Click browser refresh button (F5) or navigate away and back
5. Locate the same IP address

**Expected Results:**
- [  ] Guest assignment persists after page reload
- [  ] IP still shows guest indicator and name
- [  ] IP still has yellow/amber background
- [  ] "Release" button still visible
- [  ] No data loss occurred

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 7: Concurrent Access Simulation

**Objective:** Verify that the system handles race conditions safely

**Pre-conditions:**
- Two browser sessions/tabs open as admin
- At least one free IP available

**Steps:**
1. Open the Free IPs page in two different browser tabs
2. In Tab 1: Click "Assign to Guest" for IP address X.X.X.X
3. In Tab 2: Simultaneously (before Tab 1 completes), click "Assign to Guest" for the SAME IP address X.X.X.X
4. In Tab 1: Enter "Guest A" and click Assign
5. In Tab 2: Enter "Guest B" and click Assign
6. Observe the results in both tabs

**Expected Results:**
- [  ] Only ONE guest assignment succeeds
- [  ] The second attempt receives an error message
- [  ] Error message indicates IP is already assigned
- [  ] No data corruption occurs
- [  ] Database maintains data integrity
- [  ] Both tabs can refresh to see the correct state

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 8: Empty/Invalid Guest Name

**Objective:** Verify validation of guest name input

**Pre-conditions:**
- At least one free IP available

**Steps:**
1. Click "Assign to Guest" on a free IP
2. Leave the guest name field empty
3. Click "Assign" button
4. Observe validation error
5. Enter only spaces "    " in guest name field
6. Click "Assign" button
7. Observe validation error

**Expected Results:**
- [  ] Empty field shows error: "Guest name is required"
- [  ] Spaces-only field shows error: "Guest name is required"
- [  ] Form does not submit with invalid input
- [  ] Modal remains open with error visible
- [  ] No database changes occur

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 9: Long Guest Name (Boundary Testing)

**Objective:** Verify maximum length validation

**Pre-conditions:**
- At least one free IP available

**Steps:**
1. Click "Assign to Guest" on a free IP
2. Enter a guest name with exactly 150 characters
3. Click "Assign" button
4. Verify success
5. Release the IP
6. Click "Assign to Guest" again
7. Enter a guest name with 151+ characters
8. Click "Assign" button
9. Observe validation error

**Expected Results:**
- [  ] 150 characters: Assignment succeeds
- [  ] 151+ characters: Shows error "Guest name must be 150 characters or less"
- [  ] Maximum length is properly enforced

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 10: Visual Styling and UI/UX

**Objective:** Verify visual design and user experience

**Steps:**
1. Navigate to Free IPs page
2. Observe the legend at the top of the page
3. Locate guest-assigned IPs (if any)
4. Hover over guest IPs
5. Test responsive design on different screen sizes

**Expected Results:**
- [  ] Legend includes guest IP indicator with yellow/amber color
- [  ] Guest IPs have distinct yellow/amber background color
- [  ] Guest icon (👤) is clearly visible
- [  ] Guest name is easy to read
- [  ] Buttons have proper hover states
- [  ] Modal is centered and well-styled
- [  ] Colors have sufficient contrast (accessibility)
- [  ] Layout is responsive on different screen sizes
- [  ] UI matches existing Asset Tracker design patterns

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 11: Authentication and Authorization

**Objective:** Verify that only admin users can access guest IP features

**Pre-conditions:**
- Regular (non-admin) user account available

**Steps:**
1. Log out from admin account
2. Log in as a regular user
3. Navigate to Free IPs page
4. Observe if "Assign to Guest" buttons are visible
5. Attempt to directly POST to /assets/guest-ip/assign/
6. Log out and try accessing without authentication

**Expected Results:**
- [  ] Regular users do NOT see "Assign to Guest" buttons
- [  ] Regular users do NOT see "Release" buttons on guest IPs
- [  ] Direct POST requests return 403 Forbidden or redirect to login
- [  ] Unauthenticated users are redirected to login page
- [  ] Only admin users have full access

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 12: Browser Console Check

**Objective:** Verify no JavaScript errors occur

**Steps:**
1. Open browser Developer Tools (F12)
2. Navigate to Console tab
3. Perform all guest IP operations:
   - Open assignment modal
   - Assign IP to guest
   - Release guest IP
   - Search for guest names
4. Observe console for errors or warnings

**Expected Results:**
- [  ] No JavaScript errors in console
- [  ] No network request failures (except expected validation errors)
- [  ] All AJAX requests complete successfully
- [  ] CSRF token is properly included in requests
- [  ] No 404 errors for static resources

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 13: Network Tab Verification

**Objective:** Verify API endpoints respond correctly

**Steps:**
1. Open browser Developer Tools (F12)
2. Navigate to Network tab
3. Assign an IP to a guest
4. Observe the POST request to /assets/guest-ip/assign/
5. Release the guest IP
6. Observe the POST request to /assets/guest-ip/release/

**Expected Results:**
- [  ] POST to /assets/guest-ip/assign/ returns 200 OK
- [  ] Response contains JSON with success: true
- [  ] Response includes ip_address and guest_name fields
- [  ] POST to /assets/guest-ip/release/ returns 200 OK
- [  ] Response contains JSON with success: true
- [  ] Response includes ip_address field
- [  ] CSRF token header is present in all requests

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 14: Regression Testing - Existing Features

**Objective:** Verify no regressions in existing IP management functionality

**Steps:**
1. Test VM creation from free IP (existing feature)
2. Test manual IP assignment to assets
3. Test network device IP management
4. Test general IP list page performance
5. Test IP range filtering/sorting

**Expected Results:**
- [  ] VM creation still works correctly
- [  ] Asset IP assignment is not affected
- [  ] Network device management functions properly
- [  ] Page loads within acceptable time (<3 seconds)
- [  ] Filtering and sorting work as before
- [  ] No broken features due to guest IP changes

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

### Test Case 15: Special Characters in Guest Name

**Objective:** Verify handling of international and special characters

**Steps:**
1. Assign IP to guest with name containing:
   - Accented characters: "José García"
   - Unicode characters: "王小明"
   - Special symbols: "O'Brien-Smith"
2. Verify name displays correctly
3. Search for these names
4. Release the IPs

**Expected Results:**
- [  ] International characters are saved correctly
- [  ] Names display properly in the UI
- [  ] Search works with international characters
- [  ] No encoding issues or data corruption
- [  ] Names with apostrophes and hyphens work correctly

**Actual Results:** {{ TO BE FILLED }}

**Status:** [ ] PASS [ ] FAIL

**Notes:** {{ TO BE FILLED }}

---

## Browser Compatibility Testing

Test the feature on multiple browsers:

### Chrome/Edge (Chromium-based)
- Version: {{ TO BE FILLED }}
- Status: [ ] PASS [ ] FAIL
- Notes: {{ TO BE FILLED }}

### Firefox
- Version: {{ TO BE FILLED }}
- Status: [ ] PASS [ ] FAIL
- Notes: {{ TO BE FILLED }}

### Safari (if available)
- Version: {{ TO BE FILLED }}
- Status: [ ] PASS [ ] FAIL
- Notes: {{ TO BE FILLED }}

---

## Performance Testing

### Page Load Performance
- Initial page load time: {{ TO BE FILLED }}
- With 100+ IPs: {{ TO BE FILLED }}
- With guest IPs assigned: {{ TO BE FILLED }}
- Status: [ ] Acceptable (<3s) [ ] Needs improvement

### Operation Response Time
- Guest IP assignment: {{ TO BE FILLED }}
- Guest IP release: {{ TO BE FILLED }}
- Search response: {{ TO BE FILLED }}
- Status: [ ] Acceptable (<1s) [ ] Needs improvement

---

## Defects Found

### Defect 1
- **Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
- **Description:** {{ TO BE FILLED }}
- **Steps to Reproduce:** {{ TO BE FILLED }}
- **Expected:** {{ TO BE FILLED }}
- **Actual:** {{ TO BE FILLED }}
- **Status:** {{ TO BE FILLED }}

### Defect 2
- **Severity:** [ ] Critical [ ] High [ ] Medium [ ] Low
- **Description:** {{ TO BE FILLED }}
- **Steps to Reproduce:** {{ TO BE FILLED }}
- **Expected:** {{ TO BE FILLED }}
- **Actual:** {{ TO BE FILLED }}
- **Status:** {{ TO BE FILLED }}

---

## Final Assessment

### Overall Test Results
- **Total Test Cases:** 15
- **Passed:** {{ TO BE FILLED }}
- **Failed:** {{ TO BE FILLED }}
- **Blocked:** {{ TO BE FILLED }}
- **Pass Rate:** {{ TO BE FILLED }}%

### Acceptance Criteria Met
- [  ] All test cases pass
- [  ] No console errors or warnings
- [  ] UI is responsive and intuitive
- [  ] No regressions in existing functionality
- [  ] Page loads and operations are fast (<1s)

### Recommendation
[ ] **APPROVED FOR PRODUCTION** - Feature is ready for deployment  
[ ] **CONDITIONAL APPROVAL** - Minor issues need fixing first  
[ ] **NOT APPROVED** - Critical issues must be resolved  

### Comments/Notes
{{ TO BE FILLED }}

---

## Sign-off

**Tester Name:** {{ TO BE FILLED }}  
**Tester Signature:** {{ TO BE FILLED }}  
**Date:** {{ TO BE FILLED }}  

**Product Owner/Manager:** {{ TO BE FILLED }}  
**Approval Signature:** {{ TO BE FILLED }}  
**Date:** {{ TO BE FILLED }}  

---

## How to Use This Report

1. **Preparation:**
   - Ensure Django server is running: `python manage.py runserver`
   - Have admin and regular user credentials ready
   - Open browser with Developer Tools available

2. **Execution:**
   - Work through each test case sequentially
   - Fill in "Actual Results" for each test
   - Mark status as PASS or FAIL
   - Document any issues in the Defects section

3. **Completion:**
   - Calculate pass rate
   - Fill in final assessment
   - Provide recommendation
   - Sign off on the report

4. **Reporting:**
   - Share this completed document with the development team
   - Log any defects in the project's issue tracker
   - Schedule fixes for any failed test cases

---

**END OF MANUAL TEST REPORT**
