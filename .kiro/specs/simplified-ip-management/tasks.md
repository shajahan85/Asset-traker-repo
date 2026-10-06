# Implementation Plan: Simplified IP Management

## Overview

This implementation converts the Asset IP management system from a confusing two-field approach ("Primary IP (LAN)" and "Secondary IP (WiFi)") to a cleaner design with a primary "IP Address" field and support for multiple additional IP addresses with custom labels. The implementation uses Django formsets for dynamic IP entry and preserves all existing data through backward-compatible migrations.

## Tasks

- [x] 1. Create database migrations for ip_label field
  - [x] 1.1 Create schema migration to add ip_label field to AssetIPAddress model
    - Add CharField(max_length=100, blank=True, null=True) to AssetIPAddress
    - Field should allow null/blank for primary IPs
    - Add help text describing the field's purpose
    - _Requirements: 1.4.1, 1.4.2, 1.4.3_

  - [x] 1.2 Create data migration to populate ip_label for existing secondary IPs
    - Query all AssetIPAddress records where is_primary=False and ip_label is null
    - Set ip_label to "Secondary IP" for these records
    - Ensure primary IPs (is_primary=True) retain null ip_label
    - Implement reverse migration to clear ip_label values
    - _Requirements: 1.5.1, 1.5.2, 1.5.3, 1.5.4, 1.5.5_

- [x] 2. Update AssetIPAddress model validation
  - [x] 2.1 Add ip_label validation rules to AssetIPAddress.clean() method
    - Validate that non-primary IPs (is_primary=False) require ip_label
    - Validate that ip_label doesn't contain only whitespace
    - Validate that primary IPs (is_primary=True) don't have ip_label
    - Raise appropriate ValidationError messages for each case
    - _Requirements: 1.4.4, 1.4.5, 1.4.6_

  - [ ]* 2.2 Write unit tests for AssetIPAddress model validation
    - Test creating AssetIPAddress with valid ip_label
    - Test that primary IPs cannot have labels
    - Test that additional IPs require labels
    - Test that whitespace-only labels are rejected
    - Test that null ip_label is allowed for primary IPs
    - _Requirements: 1.4.1, 1.4.4, 1.4.5, 1.4.6_

- [x] 3. Create AdditionalIPForm for formset entries
  - [x] 3.1 Implement AdditionalIPForm ModelForm class
    - Create form inheriting from forms.ModelForm for AssetIPAddress
    - Add ip_type ChoiceField with radio buttons (managed/manual)
    - Include fields: ip_label, ip_address, manual_ip
    - Configure widgets with appropriate CSS classes and placeholders
    - Set ip_label as required, ip_address and manual_ip as optional
    - _Requirements: 1.2.3, 1.2.4, 1.2.5, 1.2.6_

  - [x] 3.2 Implement AdditionalIPForm validation logic
    - Add clean() method to validate IP entry mode consistency
    - Validate that exactly one of ip_address or manual_ip is provided based on ip_type
    - Clear the unused field (managed vs manual) based on selection
    - Add appropriate error messages for missing IPs
    - _Requirements: 1.10.1, 1.10.2, 1.10.3, 1.10.4_

  - [x] 3.3 Implement AdditionalIPForm save method
    - Override save() to set is_primary=False for all instances
    - Handle IP pool assignment for managed IPs (mark as assigned)
    - Ensure manual IPs don't affect IP pool
    - _Requirements: 1.3.4, 1.3.5, 1.9.1_

  - [x] 3.4 Create AdditionalIPFormSet using inlineformset_factory
    - Use inlineformset_factory with Asset as parent, AssetIPAddress as child
    - Configure extra=0, can_delete=True, min_num=0, max_num=10
    - Set form class to AdditionalIPForm
    - _Requirements: 1.2.1, 1.2.2, 1.2.8_

  - [ ]* 3.5 Write unit tests for AdditionalIPForm
    - Test form with valid managed IP data
    - Test form with valid manual IP data
    - Test form validation requires label
    - Test form validation requires IP selection based on ip_type
    - Test that ip_type toggles clear unused IP field
    - _Requirements: 1.2.3, 1.2.4, 1.2.5, 1.2.6, 1.4.4_

- [x] 4. Update AssetForm for simplified primary IP
  - [x] 4.1 Modify AssetForm primary IP field labels and structure
    - Change primary_ip_type label to "IP Address" (remove "(LAN)" suffix)
    - Update form labels dict to change ip_address label to "IP Address (Managed)"
    - Update manual_ip label to "IP Address (Manual)"
    - Remove secondary_ip_type, secondary_ip_address, secondary_manual_ip fields
    - _Requirements: 1.1.1, 1.1.2_

  - [x] 4.2 Simplify AssetForm save() method to handle only primary IP
    - Remove secondary IP handling logic from save() method
    - Keep only primary IP creation/update logic
    - Ensure is_primary=True and ip_label=None for primary IPs
    - Handle IP pool assignment for managed primary IPs
    - Wrap operations in transaction.atomic()
    - _Requirements: 1.3.1, 1.3.2, 1.3.3, 1.3.4, 1.3.5, 1.9.1_

  - [ ]* 4.3 Write unit tests for updated AssetForm
    - Test form creates asset with managed primary IP
    - Test form creates asset with manual primary IP
    - Test form allows asset with no primary IP
    - Test form validates manual IP as valid IPv4
    - Test IP pool is updated when managed IP is assigned
    - _Requirements: 1.1.3, 1.1.4, 1.1.5, 1.1.6, 1.9.1_

- [ ] 5. Checkpoint - Ensure model and form tests pass
  - Run model and form unit tests
  - Verify migrations apply successfully
  - Ensure all tests pass, ask the user if questions arise

- [ ] 6. Update asset create view to handle formset
  - [ ] 6.1 Modify AssetCreateView to include AdditionalIPFormSet in context
    - Override get_context_data() to instantiate formset
    - Handle POST data by passing to formset
    - Handle GET requests with empty formset
    - _Requirements: 1.2.1_

  - [ ] 6.2 Implement formset validation in AssetCreateView.form_valid()
    - Check formset.is_valid() before saving
    - Return form_invalid() if formset has errors
    - Save asset first, then set formset.instance and save formset
    - Wrap all saves in transaction.atomic()
    - _Requirements: 1.2.7, 1.6.1, 1.6.2, 1.6.3_

- [ ] 7. Update asset edit view to handle formset
  - [ ] 7.1 Modify AssetUpdateView to include AdditionalIPFormSet with existing data
    - Override get_context_data() to instantiate formset with instance
    - Filter queryset to only non-primary IPs (is_primary=False)
    - Handle POST data by passing to formset
    - _Requirements: 1.2.1, 1.2.2_

  - [ ] 7.2 Implement formset saving in AssetUpdateView.form_valid()
    - Validate formset alongside main form
    - Save formset (handles updates, deletions, new entries automatically)
    - Release deleted managed IPs back to IP pool
    - Wrap operations in transaction.atomic()
    - _Requirements: 1.2.8, 1.9.3, 1.9.4_

  - [ ]* 7.3 Write integration tests for create and update views
    - Test creating asset with primary IP only
    - Test creating asset with primary IP and 2 additional IPs
    - Test creating asset with managed and manual additional IPs
    - Test updating asset to add additional IPs
    - Test updating asset to remove additional IP
    - Test that removed managed IPs are released to pool
    - Test formset validation errors are displayed
    - _Requirements: 1.2.1, 1.2.2, 1.2.7, 1.2.8, 1.9.1, 1.9.3_

- [ ] 8. Create template for primary IP section
  - [ ] 8.1 Update asset_form.html template with simplified primary IP section
    - Change section heading to "IP Address" (remove "Primary" and "LAN")
    - Render primary_ip_type radio buttons with proper styling
    - Create div for managed IP field with id="primary-managed-ip-group"
    - Create div for manual IP field with id="primary-manual-ip-group", initially hidden
    - Display validation errors for each field
    - _Requirements: 1.1.1, 1.1.2, 1.1.3, 1.1.4_

- [ ] 9. Create template for additional IPs formset section
  - [ ] 9.1 Add additional IPs section to asset_form.html template
    - Add section with heading "Additional IP Addresses"
    - Render formset.management_form
    - Create container div with id="additional-ip-forms"
    - Add "Add Additional IP" button
    - Add empty form template div (hidden) for JavaScript cloning
    - _Requirements: 1.2.1, 1.8.1, 1.8.2_

  - [ ] 9.2 Create template loop for rendering additional IP forms
    - Loop through formset forms and render each in a bordered div
    - Include hidden DELETE checkbox for existing forms
    - Render ip_label field with label and error display
    - Render ip_type radio buttons
    - Create managed IP field div with class "additional-managed-ip-group"
    - Create manual IP field div with class "additional-manual-ip-group", initially hidden
    - Add "Remove" button for each form
    - _Requirements: 1.2.3, 1.2.4, 1.2.5, 1.2.6, 1.2.8, 1.8.3, 1.8.4_

- [ ] 10. Implement JavaScript for dynamic IP type toggling
  - [ ] 10.1 Add JavaScript to toggle primary IP field visibility
    - Add event listeners to primary_ip_type radio buttons
    - Show primary-managed-ip-group when "managed" selected
    - Show primary-manual-ip-group when "manual" selected
    - Initialize visibility on page load based on current selection
    - _Requirements: 1.1.3, 1.1.4_

  - [ ] 10.2 Add JavaScript function to toggle additional IP field visibility
    - Create setupAdditionalIPTypeToggle() function
    - Add event listeners to ip_type radios within each additional IP form
    - Show/hide managed vs manual fields based on selection
    - Initialize visibility for existing forms on page load
    - _Requirements: 1.2.4, 1.2.5, 1.2.6_

- [ ] 11. Implement JavaScript for dynamic form add/remove
  - [ ] 11.1 Implement "Add Additional IP" button functionality
    - Get current form count from TOTAL_FORMS hidden field
    - Clone empty form template HTML
    - Replace __prefix__ placeholder with current form index
    - Append new form to forms container
    - Increment TOTAL_FORMS count
    - Setup IP type toggle for new form
    - Setup remove button for new form
    - _Requirements: 1.8.1, 1.8.2, 1.8.5_

  - [ ] 11.2 Implement "Remove" button functionality
    - Add click event listeners to all remove buttons
    - For existing forms: check DELETE checkbox and hide form
    - For new forms: remove from DOM and decrement TOTAL_FORMS
    - Re-index remaining forms after removal
    - _Requirements: 1.8.3, 1.8.4, 1.8.5_

  - [ ] 11.3 Implement form re-indexing function
    - Create reindexForms() function
    - Update data-form-index attribute for each visible form
    - Update field names to use sequential indexes
    - Update field IDs to use sequential indexes
    - Update label for attributes to match new IDs
    - _Requirements: 1.8.5_

- [ ] 12. Checkpoint - Test form functionality manually
  - Test primary IP radio toggles show/hide correct fields
  - Test additional IP type radios toggle managed/manual fields
  - Test "Add Additional IP" adds new form correctly
  - Test "Remove" button works for new and existing forms
  - Test form submission with multiple additional IPs
  - Ensure all tests pass, ask the user if questions arise

- [ ] 13. Update asset detail view template
  - [ ] 13.1 Modify asset detail template to display primary IP with simplified label
    - Change "Primary IP (LAN)" label to "IP Address"
    - Display primary IP using asset.get_primary_ip().get_ip_display()
    - Show "No IP assigned" when asset has no primary IP
    - _Requirements: 1.7.1, 1.7.4, 1.11.1_

  - [ ] 13.2 Add additional IPs section to asset detail template
    - Query asset.asset_ip_addresses.filter(is_primary=False)
    - Display list of additional IPs only if any exist
    - For each additional IP, show ip_label as a badge and IP address
    - Use Bootstrap badge component for labels
    - _Requirements: 1.7.2, 1.7.3, 1.7.5_

- [ ] 14. Update asset list view template
  - [ ] 14.1 Simplify IP address column in asset list table
    - Change column header from "Primary IP (LAN)" to "IP Address"
    - Display only primary IP using asset.get_primary_ip().get_ip_display()
    - Show "—" for assets with no primary IP
    - Do not display additional IPs in list view
    - _Requirements: 1.11.1, 1.11.2, 1.11.3, 1.11.4, 1.11.5_

- [ ] 15. Add duplicate IP validation
  - [ ] 15.1 Implement formset-level validation to prevent duplicate IPs on same asset
    - Override AdditionalIPFormSet.clean() method
    - Collect all IP addresses from forms (both managed and manual)
    - Check for duplicates within the formset
    - Check for duplicates against primary IP
    - Raise ValidationError if duplicate found with message "This IP is already assigned to this asset"
    - _Requirements: 1.6.1, 1.6.2, 1.6.3_

  - [ ]* 15.2 Write tests for duplicate IP validation
    - Test that duplicate manual IPs on same asset are rejected
    - Test that duplicate managed IPs on same asset are rejected
    - Test that primary IP matching additional IP is rejected
    - Test that same IP on different assets is allowed (manual IPs)
    - Test error message is displayed correctly
    - _Requirements: 1.6.1, 1.6.2, 1.6.3, 1.6.4_

- [ ] 16. Update IP pool management for additional IPs
  - [ ] 16.1 Ensure IP pool correctly tracks additional managed IPs
    - Verify AdditionalIPForm.save() marks managed IPs as assigned
    - Verify update view releases deleted managed IPs
    - Test that asset deletion releases all managed IPs (verify existing CASCADE behavior)
    - _Requirements: 1.9.1, 1.9.2, 1.9.3, 1.9.4, 1.9.5_

  - [ ]* 16.2 Write integration tests for IP pool management
    - Test creating asset with managed additional IP marks it assigned
    - Test updating asset to remove managed additional IP releases it
    - Test deleting asset releases all managed IPs (primary and additional)
    - Test that changing managed IP releases old and assigns new
    - Test that manual IPs don't affect IP pool
    - _Requirements: 1.9.1, 1.9.2, 1.9.3, 1.9.4_

- [ ] 17. Verify timestamp preservation
  - [ ] 17.1 Ensure created_at timestamps are set correctly
    - Verify AssetIPAddress.created_at uses auto_now_add=True
    - Test that new IP assignments get current timestamp
    - Verify existing timestamps are preserved during updates
    - _Requirements: 1.12.1, 1.12.2_

  - [ ] 17.2 Verify freed_date tracking for managed IPs
    - Confirm IPAddress model's freed_date is updated when IPs released
    - Test removal of managed additional IP sets freed_date
    - Verify existing IP release behavior is maintained
    - _Requirements: 1.12.3, 1.12.4, 1.12.5_

- [ ] 18. Final checkpoint and testing
  - Run full test suite (unit + integration tests)
  - Manually test complete create workflow with multiple IPs
  - Manually test complete update workflow with add/remove IPs
  - Verify asset list and detail views display correctly
  - Test with existing data to ensure backward compatibility
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional test tasks and can be skipped for faster MVP delivery
- All implementation tasks build incrementally: migrations → models → forms → views → templates → JavaScript
- Checkpoints ensure validation at key integration points
- The design uses Python/Django with standard patterns (ModelForm, formsets, templates)
- JavaScript provides progressive enhancement - forms work without it
- All operations use database transactions to ensure data consistency
- IP pool management logic is preserved from existing implementation
- Backward compatibility is maintained through nullable ip_label field and data migration

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1"] },
    { "id": 2, "tasks": ["2.2", "3.1"] },
    { "id": 3, "tasks": ["3.2", "3.3"] },
    { "id": 4, "tasks": ["3.4", "3.5", "4.1"] },
    { "id": 5, "tasks": ["4.2"] },
    { "id": 6, "tasks": ["4.3", "6.1"] },
    { "id": 7, "tasks": ["6.2", "7.1"] },
    { "id": 8, "tasks": ["7.2", "7.3", "8.1"] },
    { "id": 9, "tasks": ["9.1", "9.2", "10.1"] },
    { "id": 10, "tasks": ["10.2", "11.1"] },
    { "id": 11, "tasks": ["11.2", "11.3"] },
    { "id": 12, "tasks": ["13.1", "13.2", "14.1"] },
    { "id": 13, "tasks": ["15.1"] },
    { "id": 14, "tasks": ["15.2", "16.1"] },
    { "id": 15, "tasks": ["16.2", "17.1"] },
    { "id": 16, "tasks": ["17.2"] }
  ]
}
```
