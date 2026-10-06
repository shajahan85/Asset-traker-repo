# Implementation Plan: Multiple IP Addresses per Asset

## Overview

This implementation plan breaks down the Multiple IP Addresses feature into incremental, testable steps. The feature enables assets to have one primary IP address and multiple secondary IP addresses, supporting scenarios where users switch between different network connections (e.g., LAN and WiFi).

The implementation follows this sequence:
1. Create data model and service layer
2. Implement data migration from single-IP to multiple-IP structure
3. Update forms for secondary IP management
4. Create views for IP operations (add/remove/set primary)
5. Update templates to display multiple IPs
6. Implement comprehensive testing

Each task builds on previous steps with validation checkpoints to ensure incremental correctness.

## Tasks

- [ ] 1. Create AssetIPAddress junction model and Asset model extensions
  - Create `assets/models/asset_ip_address.py` with AssetIPAddress model including all fields (asset, ip_address, manual_ip, is_primary, created_at)
  - Add database constraints (CheckConstraint for exactly one IP type)
  - Add indexes for efficient queries (asset+is_primary composite, ip_address)
  - Implement `clean()` method for validation (exactly one IP type, no duplicates per asset)
  - Implement `get_ip_display()` method to return the displayable IP address
  - Add to `assets/models/__init__.py` imports
  - Create `Asset.get_primary_ip()` method in `assets/models/asset.py`
  - Create `Asset.get_secondary_ips()` method
  - Create `Asset.get_all_ips()` method
  - Create `Asset.get_display_primary_ip()` method
  - Create `Asset.has_managed_primary_ip()` method
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 3.1, 3.2, 3.3, 3.4_

- [ ]* 1.1 Write property test for AssetIPAddress model
  - **Property 1: Primary IP Uniqueness**
  - **Validates: Requirements 1.4, 8.1**

- [ ]* 1.2 Write property test for managed IP assignment state
  - **Property 2: Managed IP Assignment State**
  - **Validates: Requirements 1.2, 1.3, 1.6, 2.6**

- [ ]* 1.3 Write unit tests for AssetIPAddress validation
  - Test exactly one IP type constraint
  - Test duplicate IP detection per asset
  - Test get_ip_display() for both managed and manual IPs
  - _Requirements: 8.2, 8.4_

- [ ]* 1.4 Write unit tests for Asset model extensions
  - Test get_primary_ip() returns correct AssetIPAddress
  - Test get_secondary_ips() excludes primary
  - Test get_display_primary_ip() returns correct string
  - Test has_managed_primary_ip() returns correct boolean
  - _Requirements: 1.4, 1.5, 3.1, 3.4_

- [ ] 2. Create AssetIPService for business logic
  - Create `assets/services/asset_ip_service.py` with AssetIPService class
  - Implement `add_secondary_ip(asset, ip_address=None, manual_ip=None, user=None)` static method
  - Implement `remove_secondary_ip(asset_ip, user=None)` static method
  - Implement `set_primary_ip(asset, new_primary_asset_ip, user=None)` static method
  - Implement `migrate_legacy_ip_to_asset_ip(asset)` static method
  - Implement `ensure_primary_ip_exists(asset)` static method
  - All methods must use `transaction.atomic()` for database consistency
  - Implement all validation logic (IP conflicts, primary IP protection, etc.)
  - Mark managed IPs as assigned/unassigned appropriately
  - _Requirements: 1.2, 1.3, 1.6, 1.7, 2.5, 2.6, 3.5, 3.6, 3.7, 5.1, 5.2, 5.3, 8.1, 8.2, 8.4_

- [ ]* 2.1 Write property test for secondary IP association persistence
  - **Property 5: Secondary IP Association Persistence**
  - **Validates: Requirements 2.5**

- [ ]* 2.2 Write property test for multiple secondary IPs support
  - **Property 6: Multiple Secondary IPs Support**
  - **Validates: Requirements 2.7**

- [ ]* 2.3 Write property test for secondary IP removal
  - **Property 7: Secondary IP Removal**
  - **Validates: Requirements 3.5**

- [ ]* 2.4 Write property test for primary IP removal protection
  - **Property 8: Primary IP Removal Protection**
  - **Validates: Requirements 3.7**

- [ ]* 2.5 Write property test for managed IP conflict prevention
  - **Property 12: Managed IP Conflict Prevention**
  - **Validates: Requirements 5.1, 5.2**

- [ ]* 2.6 Write property test for IP reassignment after release
  - **Property 13: IP Reassignment After Release**
  - **Validates: Requirements 5.3**

- [ ]* 2.7 Write property test for managed IP release state
  - **Property 3: Managed IP Release State**
  - **Validates: Requirements 1.7, 3.6**

- [ ]* 2.8 Write property test for asset primary IP requirement
  - **Property 21: Asset Primary IP Requirement**
  - **Validates: Requirements 8.1**

- [ ]* 2.9 Write property test for no duplicate IPs per asset
  - **Property 22: No Duplicate IPs Per Asset**
  - **Validates: Requirements 8.2, 8.4**

- [ ]* 2.10 Write unit tests for AssetIPService
  - Test add_secondary_ip success cases (managed and manual)
  - Test add_secondary_ip error cases (already assigned, duplicate on asset, both types provided)
  - Test remove_secondary_ip success and error cases
  - Test set_primary_ip success and validation
  - Test migrate_legacy_ip_to_asset_ip for both managed and manual IPs
  - Test ensure_primary_ip_exists fixes multiple/zero primary situations
  - _Requirements: 1.2, 1.3, 1.6, 1.7, 2.5, 2.6, 3.5, 3.7, 5.1, 5.2, 8.1, 8.2, 8.4_

- [ ] 3. Create and run data migration
  - Generate Django migration file for AssetIPAddress model: `python manage.py makemigrations assets`
  - Create data migration script to migrate existing Asset.ip_address and Asset.manual_ip to AssetIPAddress
  - Data migration should create AssetIPAddress records with is_primary=True for all existing IPs
  - Skip assets already migrated (check if primary IP exists)
  - Run migration: `python manage.py migrate assets`
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 3.1 Write integration test for data migration
  - Create test assets with ip_address and manual_ip
  - Run migration
  - Verify AssetIPAddress records created with is_primary=True
  - Verify is_assigned states preserved
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 4. Checkpoint - Ensure model and service tests pass
  - Run all model and service tests
  - Verify data migration completed successfully
  - Ask user if any questions arise

- [ ] 5. Create SecondaryIPForm for adding secondary IPs
  - Create `assets/forms/secondary_ip_form.py` with SecondaryIPForm class
  - Add ip_type choice field (managed/manual) with radio buttons
  - Add ip_address ModelChoiceField for managed IPs (filtered to 192.168.10/11/50/70.x ranges, is_assigned=False)
  - Add manual_ip GenericIPAddressField for manual IPs (IPv4 protocol)
  - Implement `__init__` to populate available managed IPs using get_filtered_free_ips()
  - Implement `clean()` method to validate exactly one IP type provided based on ip_type selection
  - Add JavaScript-friendly field IDs and classes for dynamic form behavior
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3_

- [ ]* 5.1 Write property test for available IP filtering
  - **Property 4: Available IP Filtering**
  - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ]* 5.2 Write property test for manual IP IPv4 validation
  - **Property 9: Manual IP IPv4 Validation**
  - **Validates: Requirements 4.2, 4.3**

- [ ]* 5.3 Write unit tests for SecondaryIPForm
  - Test form renders with correct fields
  - Test validation requires exactly one IP type
  - Test managed IP dropdown contains only filtered free IPs
  - Test manual IP accepts valid IPv4 format
  - Test manual IP rejects invalid format
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 4.1, 4.2, 4.3_

- [ ] 6. Update AssetForm to support primary IP type selection
  - Modify `assets/forms/asset_forms.py` AssetForm class
  - Add primary_ip_type choice field (managed/manual) with radio buttons
  - Update `__init__` to detect and pre-select IP type when editing (check asset.get_primary_ip())
  - Update `save()` method to create AssetIPAddress record for primary IP
  - When creating new primary, remove old primary if exists (for updates)
  - Mark managed IPs as assigned/unassigned appropriately in save()
  - Keep existing ip_address and manual_ip fields for backward compatibility during transition
  - _Requirements: 1.2, 1.3, 1.6, 2.1, 4.1, 8.1, 8.3_

- [ ]* 6.1 Write unit tests for AssetForm updates
  - Test form detects managed primary IP on edit
  - Test form detects manual primary IP on edit
  - Test save() creates AssetIPAddress with is_primary=True
  - Test save() marks managed IP as assigned
  - Test save() replaces old primary IP when updating
  - _Requirements: 1.2, 1.3, 1.6, 8.1, 8.3_

- [ ] 7. Update ReassignmentForm to support multiple IPs
  - Modify `assets/forms/asset_forms.py` ReassignmentForm class
  - Add primary_ip_type choice field (managed/manual) with radio buttons
  - Add ip_address ModelChoiceField for managed primary IP (filtered to available IPs)
  - Keep manual_ip field for manual primary IP
  - Update `__init__` to pre-populate with asset's current primary IP
  - Update `__init__` to include current managed IP in queryset for updates
  - Update `clean()` method to validate primary IP selection based on ip_type
  - Form will handle primary IP only; secondary IPs managed via separate views
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 7.1 Write unit tests for ReassignmentForm updates
  - Test form pre-populates with current primary IP (managed and manual)
  - Test form validation requires primary IP
  - Test managed IP queryset includes current IP even if assigned
  - Test clean() validates IP based on ip_type selection
  - _Requirements: 6.1, 6.2, 6.5_

- [ ] 8. Create views for secondary IP management
  - Create `assets/views/asset_ip_views.py` with view classes
  - Implement AddSecondaryIPView (GET displays form, POST processes addition)
  - Implement RemoveSecondaryIPView (POST processes removal with confirmation)
  - Implement SetPrimaryIPView (POST changes primary IP designation)
  - All views require AdminRequiredMixin permission
  - Use AssetIPService methods for all operations
  - Add success/error messages using Django messages framework
  - Redirect to asset_detail after operations
  - _Requirements: 2.1, 2.2, 2.5, 2.7, 3.5, 3.6, 6.3, 6.4, 6.5_

- [ ]* 8.1 Write integration tests for secondary IP views
  - Test AddSecondaryIPView GET displays form with available IPs
  - Test AddSecondaryIPView POST adds managed secondary IP
  - Test AddSecondaryIPView POST adds manual secondary IP
  - Test AddSecondaryIPView POST rejects already assigned IP
  - Test RemoveSecondaryIPView POST removes secondary IP
  - Test RemoveSecondaryIPView POST rejects removing primary IP
  - Test SetPrimaryIPView POST changes primary designation
  - _Requirements: 2.1, 2.2, 2.5, 2.7, 3.5, 3.7, 6.3, 6.4, 6.5_

- [ ] 9. Add URL patterns for secondary IP views
  - Update `assets/urls.py` to add URL patterns
  - Add `path('assets/<int:pk>/add-secondary-ip/', AddSecondaryIPView.as_view(), name='add_secondary_ip')`
  - Add `path('assets/ip/<int:pk>/remove/', RemoveSecondaryIPView.as_view(), name='remove_secondary_ip')`
  - Add `path('assets/ip/<int:pk>/set-primary/', SetPrimaryIPView.as_view(), name='set_primary_ip')`
  - _Requirements: 2.1, 3.5, 6.5_

- [ ] 10. Create template for adding secondary IPs
  - Create `assets/templates/assets/add_secondary_ip.html` template
  - Display current primary IP prominently
  - Display current secondary IPs list with remove buttons
  - Render SecondaryIPForm with IP type radio buttons
  - Add JavaScript to toggle between managed IP dropdown and manual IP text input based on selected ip_type
  - Include CSRF token and form validation error display
  - Add "Add Secondary IP" button to submit form
  - Add "Cancel" button to return to asset detail
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 3.1, 3.2, 3.3, 4.1_

- [ ] 11. Update asset detail template to display multiple IPs
  - Modify `assets/templates/assets/asset_detail.html` template
  - Display primary IP with "(Primary)" label prominently
  - Display secondary IPs list with labels "(Secondary - Managed)" or "(Secondary - Manual)"
  - Add "Add Secondary IP" button linking to add_secondary_ip view (admin only)
  - Add "Remove" button next to each secondary IP (POST to remove_secondary_ip view)
  - Add "Set as Primary" button next to each secondary IP (POST to set_primary_ip view)
  - Show whether each IP is managed or manual
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 6.2_

- [ ] 12. Update asset list template to display primary IP
  - Modify `assets/templates/assets/asset_list.html` template
  - Replace direct ip_address/manual_ip access with `asset.get_display_primary_ip()`
  - Display only primary IP in list view (secondary IPs visible only in detail view)
  - _Requirements: 3.1_

- [ ] 13. Checkpoint - Ensure all form and view tests pass
  - Run all form validation tests
  - Run all view integration tests
  - Test forms in browser manually
  - Ask user if any questions arise

- [ ]* 14. Write property test for manual IP isolation from managed pool
  - **Property 10: Manual IP Isolation from Managed Pool**
  - **Validates: Requirements 4.4**

- [ ]* 15. Write property test for mixed IP type support
  - **Property 11: Mixed IP Type Support**
  - **Validates: Requirements 4.6**

- [ ]* 16. Write property test for manual IP no conflict checking
  - **Property 14: Manual IP No Conflict Checking**
  - **Validates: Requirements 5.4**

- [ ]* 17. Write property test for manual IP duplicate permission
  - **Property 15: Manual IP Duplicate Permission**
  - **Validates: Requirements 5.5**

- [ ]* 18. Write property test for freed asset IP preservation
  - **Property 16: Freed Asset IP Preservation**
  - **Validates: Requirements 6.1**

- [ ]* 19. Write property test for reassignment secondary addition
  - **Property 17: Reassignment Secondary Addition**
  - **Validates: Requirements 6.3**

- [ ]* 20. Write property test for reassignment secondary removal
  - **Property 18: Reassignment Secondary Removal**
  - **Validates: Requirements 6.4**

- [ ]* 21. Write property test for reassignment primary change
  - **Property 19: Reassignment Primary Change**
  - **Validates: Requirements 6.5**

- [ ]* 22. Write property test for scrapping releases managed IPs
  - **Property 20: Scrapping Releases Managed IPs**
  - **Validates: Requirements 6.6**

- [ ] 23. Add signal handler for releasing IPs on deletion
  - Create or update `assets/signals.py`
  - Add post_delete signal handler for AssetIPAddress model
  - When AssetIPAddress is deleted, mark associated managed IP as unassigned
  - Set freed_date timestamp on managed IP
  - Clear assigned_to_asset reference
  - Register signal in `assets/apps.py` ready() method
  - _Requirements: 1.7, 3.6, 6.6_

- [ ]* 23.1 Write integration test for signal handler
  - Test deleting AssetIPAddress releases managed IP
  - Test deleting Asset cascades and releases all managed IPs
  - Test signal does not affect manual IPs
  - _Requirements: 1.7, 3.6, 6.6_

- [ ] 24. Update freed asset handling to preserve IPs
  - Review freed asset logic in views/services to ensure AssetIPAddress records are preserved when asset is freed
  - Verify freed assets retain all IP associations in database
  - Update freed asset tests to verify IP preservation
  - _Requirements: 6.1_

- [ ] 25. Update scrapped asset handling to release IPs
  - Review scrapped asset logic in views/services
  - When asset is scrapped, iterate through all managed IPs (asset.get_all_ips() where ip_address is not None)
  - Mark each managed IP as unassigned (is_assigned=False, assigned_to_asset=None, freed_date=now)
  - Update scrapped asset tests to verify IP release
  - _Requirements: 6.6_

- [ ] 26. Final integration testing
  - Test complete workflow: create asset with primary IP → add secondary IP → remove secondary IP
  - Test complete workflow: create asset → add multiple secondary IPs (mixed managed and manual)
  - Test complete workflow: edit asset primary IP (change from managed to manual)
  - Test complete workflow: free asset → reassign with different primary IP
  - Test complete workflow: asset with multiple IPs → scrap asset → verify IPs released
  - Test edge case: attempt to remove primary IP (should fail)
  - Test edge case: attempt to add duplicate IP to same asset (should fail)
  - Test edge case: attempt to add already assigned managed IP (should fail)
  - _Requirements: All requirements_

- [ ] 27. Final checkpoint - Ensure all tests pass
  - Run complete test suite: `python manage.py test assets`
  - Run property-based tests with minimum 100 iterations each
  - Verify all 22 correctness properties pass
  - Fix any remaining issues
  - Ask user if any questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property tests validate universal correctness properties across randomized inputs (minimum 100 iterations)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows and database operations
- Checkpoints ensure incremental validation
- All database operations use `transaction.atomic()` for consistency
- Signal handlers ensure IP state consistency on deletion
- Templates use Bootstrap classes for styling consistency
- JavaScript enhances form UX but is not required for core functionality
