# Implementation Plan: Mark IP as Occupied

## Overview

This implementation adds a "Mark as Occupied" action to the Free IPs page, allowing admins to flag free IPs as occupied with password verification. It introduces new model fields, a service method, an AJAX endpoint, and frontend UI components (hover button + password modal) following existing patterns in the codebase.

## Tasks

- [x] 1. Add model fields and create migration
  - [x] 1.1 Add manually_occupied, occupied_by, and occupied_date fields to IPAddress model
    - Add `manually_occupied = models.BooleanField(default=False)` field
    - Add `occupied_by = models.CharField(max_length=150, blank=True, null=True)` field
    - Add `occupied_date = models.DateTimeField(blank=True, null=True)` field
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 1.2 Generate and apply Django migration
    - Run `python manage.py makemigrations` to generate migration file
    - Run `python manage.py migrate` to apply the migration
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 2. Implement service method and backend view
  - [x] 2.1 Add mark_ip_occupied() method to IPManagementService
    - Add static method in `assets/services/ip_management_service.py`
    - Use `transaction.atomic()` for DB safety
    - Refresh IP from DB, validate it is free (`is_assigned=False`)
    - Set `is_assigned=True`, `manually_occupied=True`, `occupied_by=admin_user.username`, `occupied_date=timezone.now()`
    - Raise `ValidationError` if IP is already assigned
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 2.2 Create MarkIPOccupiedView in assets/views.py
    - Create class-based view extending `AdminRequiredMixin, View`
    - Implement `post()` method to extract `ip_address` and `password` from POST data
    - Validate required inputs are present (return 400 if missing)
    - Verify password with `check_password(password, request.user.password)` (return 403 if incorrect)
    - Look up IPAddress by address string (return 404 if not found)
    - Call `IPManagementService.mark_ip_occupied()` (return 400 if ValidationError)
    - Return JSON success response with ip_address and occupied_by
    - Handle unexpected errors with 500 response and logging
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 2.3, 2.4_
  
  - [x] 2.3 Add URL pattern for MarkIPOccupiedView
    - Add `path('ip/mark-occupied/', MarkIPOccupiedView.as_view(), name='mark_ip_occupied')` to `assets/urls.py`
    - _Requirements: 5.1_

- [x] 3. Checkpoint - Verify backend logic
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Update Free IPs template with hover button and modal
  - [x] 4.1 Add "Mark as Occupied" hover button to free IP items
    - Add button with class `mark-occupied-btn` inside `.ip-item` for items with `occupant_type == 'free'`
    - Set `data-ip-address` attribute with the IP address value
    - Apply CSS hover-reveal pattern matching existing `.release-guest-btn` styling
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  
  - [x] 4.2 Add password confirmation modal to free_ips.html
    - Create `markOccupiedModal` with password input field
    - Display the IP address being marked (read-only)
    - Add submit and cancel buttons
    - Add error message container div
    - Follow existing `guestAssignmentModal` structure
    - _Requirements: 2.1, 2.2, 2.5_
  
  - [x] 4.3 Add JavaScript for AJAX mark-occupied flow
    - Attach click handler to `.mark-occupied-btn` buttons to open modal with pre-filled IP
    - On form submit, send AJAX POST to `{% url 'mark_ip_occupied' %}` with IP and password
    - Include CSRF token in request
    - On success: update IP item styling from free to occupied, add label text
    - On error: display error message in modal
    - On cancel: close modal without changes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 5.1, 5.3_

- [x] 5. Update FreeIPsView context for manually-occupied display
  - [x] 5.1 Update occupant type logic in FreeIPsView
    - Ensure IPs with `manually_occupied=True` get `occupant_type = 'occupied'` in the view context
    - Display "Manually Occupied" label text for these IPs
    - Display `occupied_by` username and `occupied_date` in the IP item
    - Apply red background styling (existing `occupied` class)
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 6. Checkpoint - Verify full frontend flow
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 7. Write unit tests for backend
  - [ ]* 7.1 Write tests for mark_ip_occupied service method
    - Test success case: free IP becomes manually occupied
    - Test failure case: already-assigned IP raises ValidationError
    - Test that occupied_by and occupied_date are set correctly
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 7.2 Write tests for MarkIPOccupiedView
    - Test correct password returns 200 success
    - Test incorrect password returns 403
    - Test missing IP address returns 400
    - Test missing password returns 400
    - Test non-existent IP returns 404
    - Test already-assigned IP returns 400
    - Test unauthenticated request is rejected
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ]* 8. Write property-based tests
  - [ ]* 8.1 Write property test for free IP marking removes from free list
    - **Property 1: Marking an occupied IP removes it from free list**
    - **Validates: Requirements 3.1, 3.2**
    - Generate random free IPs and admin users with Hypothesis
    - Verify `is_assigned=True` and `manually_occupied=True` after mark
    - Verify IP no longer in `IPAddress.objects.filter(is_assigned=False)` query
    - Run minimum 100 iterations
  
  - [ ]* 8.2 Write property test for already-assigned rejection
    - **Property 2: Already-assigned IPs cannot be marked occupied**
    - **Validates: Requirements 3.5, 5.6**
    - Generate random already-assigned IPs with Hypothesis
    - Verify `ValidationError` is raised
    - Verify IP state is unchanged after failed call
    - Run minimum 100 iterations
  
  - [ ]* 8.3 Write property test for admin and timestamp recording
    - **Property 3: Manual occupation records admin and timestamp**
    - **Validates: Requirements 3.3, 3.4**
    - Generate random admin users and free IPs with Hypothesis
    - Verify `occupied_by == admin_user.username` after mark
    - Verify `occupied_date` is within the execution time window
    - Run minimum 100 iterations
  
  - [ ]* 8.4 Write property test for password verification gating
    - **Property 4: Password verification gates the action**
    - **Validates: Requirements 2.3, 2.4, 5.4**
    - Generate random incorrect password strings with Hypothesis
    - Verify endpoint returns HTTP 403
    - Verify IP remains unchanged (still free)
    - Run minimum 100 iterations
  
  - [ ]* 8.5 Write property test for round-trip consistency
    - **Property 5: Round-trip consistency of manual occupation state**
    - **Validates: Requirements 4.2, 4.3, 4.4**
    - Generate random mark operations with Hypothesis
    - Verify reading back from DB returns consistent `manually_occupied`, `occupied_by`, `occupied_date` values
    - Run minimum 100 iterations

- [x] 9. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation follows existing patterns: `assign_ip_to_guest()` for service, `AssignGuestIPView` for view, `guestAssignmentModal` for template
- Password verification uses `django.contrib.auth.hashers.check_password`
- All AJAX responses use `{"success": true/false, ...}` JSON format
- Property tests use Hypothesis (already configured in this project)
- CSS uses existing `.mark-occupied-btn` hover-reveal pattern matching `.release-guest-btn`

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["2.1", "2.3"] },
    { "id": 3, "tasks": ["2.2"] },
    { "id": 4, "tasks": ["4.1", "4.2", "5.1"] },
    { "id": 5, "tasks": ["4.3"] },
    { "id": 6, "tasks": ["7.1", "7.2"] },
    { "id": 7, "tasks": ["8.1", "8.2", "8.3", "8.4", "8.5"] }
  ]
}
```
