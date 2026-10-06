# Tasks: Guest IP Assignment

## Tasks

- [x] 1. Add guest fields to IPAddress model
  - Extend IPAddress model with fields for guest assignment tracking
  - Add `guest_name` CharField (max_length=150, blank=True, null=True)
  - Add `guest_assigned_date` DateTimeField (blank=True, null=True)
  - Add `guest_assigned_by` CharField (max_length=150, blank=True, null=True)
  - Add `is_guest_assigned()` helper method
  - Create and apply database migration
  - _Files: assets/models.py (IPAddress class)_

- [x] 2. Implement guest IP service methods
  - Add guest assignment and release methods to IPManagementService
  - Implement `assign_ip_to_guest(ip_address, guest_name, admin_user)` method
  - Implement `release_guest_ip(ip_address, admin_user)` method
  - Implement `_is_ip_manually_used(ip_address_str)` helper method
  - Add validation for IP availability before assignment
  - Add validation that IP is guest-assigned before release
  - Use transactions for data safety
  - _Files: assets/services/ip_management_service.py_

- [x] 3. Create guest IP assignment and release views
  - Add AJAX views for guest IP assignment and release operations
  - Create `GuestIPAssignView` class (POST only, admin required)
  - Create `GuestIPReleaseView` class (POST only, admin required)
  - Accept JSON/form POST data with ip_id and guest_name
  - Return JSON responses with success/error status
  - Handle validation errors and exceptions
  - Log assignment/release actions
  - _Files: assets/views.py_

- [x] 4. Add URL routes for guest IP operations
  - Register URL patterns for guest IP assignment and release
  - Add route for `guest-ip/assign/` → GuestIPAssignView
  - Add route for `guest-ip/release/` → GuestIPReleaseView
  - Use descriptive URL names: `guest_ip_assign`, `guest_ip_release`
  - _Files: assets/urls.py_

- [x] 5. Update FreeIPsView to identify guest IPs
  - Modify IP list view context to mark guest-assigned IPs
  - Update `get_context_data()` method in FreeIPsView
  - Check for `ip.guest_name` before other occupant types
  - Set `occupant_type = 'guest'` for guest-assigned IPs
  - Set `occupant_name` to guest_name value
  - Pass IP id to template for AJAX operations
  - _Files: assets/views.py (FreeIPsView class)_

- [x] 6. Update free IPs template with guest UI
  - Add guest assignment/release buttons and modal to IP list page
  - Add guest assignment modal HTML
  - Add "Assign Guest IP" button at top of page (manual IP entry)
  - Add "Release" button for guest-assigned IPs
  - Display guest indicator (👤) and guest name for assigned IPs
  - Add data attributes for IP id and guest name
  - Update legend to include guest IP indicator
  - _Files: assets/templates/assets/free_ips.html_

- [x] 7. Add CSS styling for guest IPs
  - Style guest-assigned IPs distinctly from other IP types
  - Add `.ip-item.guest` class with yellow/warning background
  - Add `.guest-indicator` class for guest name display
  - Add `.assign-guest-btn` and `.release-guest-btn` styles
  - Add `.legend-box.guest` style
  - Ensure colors are accessible and distinct
  - _Files: assets/templates/assets/free_ips.html (inline CSS in extra_css block)_

- [x] 8. Implement guest IP assignment JavaScript
  - Add JavaScript for guest IP assignment modal and AJAX operations
  - Open modal when "Assign Guest IP" button clicked (top of page)
  - Show inputs for BOTH IP address AND guest name (manual entry)
  - Validate IP address format (xxx.xxx.xxx.xxx)
  - Validate guest name is not empty
  - Send AJAX POST to `/guest-ip/assign/` endpoint with `ip_address` parameter
  - Handle success response (reload page)
  - Handle error response (display error message)
  - Disable submit button during request
  - _Files: assets/static/assets/js/guest_ip_assignment.js, assets/templates/assets/free_ips.html_

- [x] 9. Implement guest IP release JavaScript
  - Add JavaScript for guest IP release confirmation and AJAX
  - Attach click handlers to release buttons
  - Show browser confirmation dialog with IP and guest name
  - Send AJAX POST to `/guest-ip/release/` endpoint
  - Handle success response (reload page)
  - Handle error response (show alert)
  - Include CSRF token in request
  - _Files: assets/static/assets/js/guest_ip_assignment.js_

- [x] 10. Update IP search to include guest names
  - Extend IP search functionality to search by guest name
  - Add `data-guest-name` attribute to IP items in template
  - Update search JavaScript to check guest name field
  - Include guest-assigned IPs in search results
  - _Files: assets/templates/assets/free_ips.html (search JavaScript)_

- [x] 11. Manual testing and verification
  - Perform end-to-end testing of guest IP assignment feature
  - Test assigning free IP to guest
  - Verify IP shows as occupied after assignment
  - Test releasing guest IP
  - Verify IP shows as free after release
  - Test search by guest name
  - Test concurrent access scenarios
  - Verify no regressions in existing IP management
  - Test on different browsers (Chrome, Firefox, Edge)

- [x] 12. Update GuestIPAssignView to accept IP address instead of IP ID
  - Modify backend view to accept `ip_address` parameter (string) instead of `ip_id` to support manual IP entry UX
  - Change view to accept `ip_address` parameter (e.g., "192.168.1.100") instead of `ip_id`
  - Look up IPAddress by address field: `IPAddress.objects.get(address=ip_address)`
  - Handle DoesNotExist exception with 404 response
  - Update validation error messages to reference IP address instead of IP ID
  - All other logic remains the same (validation, service call, response)
  - _Files: assets/views.py (GuestIPAssignView class, lines 2317-2382)_
  - _Dependencies: Tasks 3, 8_
