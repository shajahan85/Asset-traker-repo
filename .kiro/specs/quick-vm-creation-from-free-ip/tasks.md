# Implementation Plan: Quick VM Creation from Free IP

## Overview

This implementation adds a streamlined VM creation workflow directly to the Free IP page using a modal-based form with AJAX submission. The feature leverages existing HyperVVM model, HyperVService, and IPManagementService infrastructure while adding a new view and frontend JavaScript module.

## Tasks

- [ ] 1. Create backend view and URL configuration
  - [ ] 1.1 Implement QuickVMCreateView in Django
    - Create new view class in assets/views.py or dedicated views/vm_views.py
    - Implement POST method to handle VM creation requests
    - Add AdminRequiredMixin for authentication
    - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4_
  
  - [ ] 1.2 Implement base machine lookup logic
    - Create lookup_base_machine() helper function
    - Search by managed IP (Asset.ip_address) first
    - Fall back to manual IP (Asset.manual_ip) search
    - Return Asset instance or None
    - _Requirements: 4.2, 4.3, 4.4, 10.4_
  
  - [ ] 1.3 Implement VM IP type determination logic
    - Create determine_vm_ip_type() helper function
    - Check if IP exists in IPAddress table
    - Verify IP is not already assigned
    - Return tuple (is_managed: bool, ip_obj: IPAddress or None)
    - _Requirements: 3.4, 3.5, 10.1, 10.2_
  
  - [ ] 1.4 Implement default VM name generation
    - Generate name format: "VM-{asset_tag}-{vm_ip}"
    - Apply when vm_name field is empty
    - _Requirements: 5.3_
  
  - [ ] 1.5 Implement request validation and error handling
    - Validate POST data (vm_ip, base_machine_ip, vm_name)
    - Validate IPv4 format for both IP fields
    - Handle ValidationError from service layer
    - Handle generic exceptions
    - Return JSON responses with appropriate error messages
    - _Requirements: 3.2, 3.3, 5.7, 5.8, 9.4, 9.5_
  
  - [ ] 1.6 Integrate with HyperVService.create_vm()
    - Prepare data dictionary with name, host_machine, ip_address/manual_ip
    - Call HyperVService.create_vm() with prepared data
    - Handle success and return JSON response with vm_id and vm_name
    - _Requirements: 5.1, 5.2, 5.4_
  
  - [ ] 1.7 Add URL route for QuickVMCreateView
    - Add path to assets/urls.py: 'vms/quick-create/'
    - Name route 'quick_vm_create'
    - _Requirements: 9.1_

- [ ] 2. Create frontend JavaScript module
  - [ ] 2.1 Create vm_creation.js file
    - Create new file in static/js/ directory
    - Set up module structure with initialization function
    - _Requirements: 1.2, 2.1_
  
  - [ ] 2.2 Implement modal display functionality
    - Implement initVMCreationModal() to set up event listeners
    - Handle "Add VM" button click to show modal
    - Handle cancel button click to close modal
    - _Requirements: 1.2, 2.6, 2.7_
  
  - [ ] 2.3 Implement client-side IP validation
    - Create validateVMIP() function for IPv4 format validation
    - Create validateBaseMachineIP() function for IPv4 format validation
    - Display inline error messages for invalid formats
    - Clear errors when user corrects input
    - _Requirements: 3.2, 3.3_
  
  - [ ] 2.4 Implement AJAX form submission
    - Create submitVMForm() function
    - Collect form data (vm_ip, base_machine_ip, vm_name)
    - Include CSRF token in request
    - Send POST request to QuickVMCreateView endpoint
    - _Requirements: 9.1_
  
  - [ ] 2.5 Implement loading indicator
    - Show spinner on submit button during request
    - Disable submit button during request
    - _Requirements: 9.2_
  
  - [ ] 2.6 Implement success response handling
    - Create handleSuccess() function
    - Display success message
    - Close modal
    - Refresh page to show new VM
    - _Requirements: 5.4, 5.5, 5.6, 9.3_
  
  - [ ] 2.7 Implement error response handling
    - Create handleError() function
    - Display general error messages
    - Display field-specific error messages
    - Keep modal open on errors
    - _Requirements: 5.7, 5.8, 9.4, 9.5_

- [ ] 3. Update Free IP page template
  - [ ] 3.1 Add "Add VM" button to page header
    - Add button with id="addVMButton"
    - Position near existing "Export Free IPs to Excel" button
    - _Requirements: 1.1, 1.2_
  
  - [ ] 3.2 Add VM creation modal HTML structure
    - Create modal with Bootstrap classes
    - Add form fields: VM IP (required), Base Machine IP (required), VM Name (optional)
    - Add submit and cancel buttons
    - Add error message containers
    - Add loading spinner element
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  
  - [ ] 3.3 Include vm_creation.js script
    - Add script tag to load vm_creation.js
    - Initialize module on page load
    - _Requirements: 1.2, 9.1_
  
  - [ ] 3.4 Add CSRF token for AJAX requests
    - Include Django CSRF token in template
    - Make token accessible to JavaScript
    - _Requirements: 9.1_

- [ ] 4. Checkpoint - Test VM creation flow
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Update Free IP page display logic
  - [ ] 5.1 Ensure VM IP display with blue background
    - Verify existing CSS class 'vm' is applied to VM IPs
    - Verify blue background color is rendered
    - _Requirements: 6.1_
  
  - [ ] 5.2 Ensure VM name and link display
    - Verify VM name is displayed below VM IP
    - Verify link to VM detail page is rendered
    - _Requirements: 6.2, 6.3_
  
  - [ ] 5.3 Ensure base machine relationship display
    - Verify base machine IP is displayed in VM relationship section
    - Verify link to base machine detail page is rendered
    - _Requirements: 6.4, 6.5_
  
  - [ ] 5.4 Ensure hosted VMs list display
    - Verify list of hosted VMs appears below base machine IP
    - Verify VM names and IPs are displayed
    - Verify links to VM detail pages are rendered
    - Verify visual indentation for hierarchy
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 6. Update search functionality
  - [ ] 6.1 Verify VM IP search results
    - Ensure VM IPs appear in search results
    - Ensure base machine IP is displayed in brackets
    - Ensure blue background color is applied
    - _Requirements: 8.1, 8.2, 8.4_
  
  - [ ] 6.2 Verify existing search functionality
    - Test search by IP address
    - Test search by assigned person name
    - Ensure no regressions
    - _Requirements: 8.3_

- [ ] 7. Handle manual IP support
  - [ ] 7.1 Verify manual VM IP storage
    - Test VM creation with manual IP (not in IPAddress table)
    - Verify IP is stored in HyperVVM.manual_ip field
    - Verify no IPAddress record is created or modified
    - _Requirements: 10.1, 10.2, 10.3_
  
  - [ ] 7.2 Verify manual IP base machine lookup
    - Test base machine lookup with manual_ip
    - Verify Asset is found correctly
    - _Requirements: 10.4_
  
  - [ ] 7.3 Verify manual IP display
    - Test display of VM with manual IP
    - Verify manual IP value is shown on Free IP page
    - _Requirements: 10.5_

- [ ]* 8. Write unit tests for backend
  - [ ]* 8.1 Write tests for QuickVMCreateView
    - Test POST with valid data
    - Test POST with missing required fields
    - Test POST with invalid IP formats
    - Test POST with already assigned IP
    - Test POST with non-existent base machine IP
    - Test default name generation
    - Test manual IP handling
    - _Requirements: 2.2, 2.3, 3.2, 3.3, 3.4, 3.5, 4.4, 5.3, 10.2_
  
  - [ ]* 8.2 Write tests for base machine lookup
    - Test lookup by managed IP
    - Test lookup by manual IP
    - Test lookup failure scenarios
    - _Requirements: 4.2, 4.3, 4.4, 10.4_
  
  - [ ]* 8.3 Write tests for VM IP type determination
    - Test managed IP detection
    - Test manual IP detection
    - Test already assigned IP rejection
    - _Requirements: 3.4, 3.5, 10.1, 10.2_

- [ ]* 9. Write property-based tests
  - [ ]* 9.1 Write property test for IPv4 validation
    - **Property 3: IPv4 Validation**
    - **Validates: Requirements 3.2**
    - Generate random strings with Hypothesis
    - Verify only valid IPv4 addresses pass validation
    - Run 100 iterations
  
  - [ ]* 9.2 Write property test for base machine lookup
    - **Property 6: Base Machine Lookup by Managed IP**
    - **Validates: Requirements 4.2**
    - Generate random Assets with various IP configurations
    - Verify lookup finds correct Asset for any valid IP
    - Run 100 iterations
  
  - [ ]* 9.3 Write property test for default name generation
    - **Property 9: Default VM Name Generation**
    - **Validates: Requirements 5.3**
    - Generate random asset tags and IP addresses
    - Verify name format is always "VM-{tag}-{ip}"
    - Run 100 iterations
  
  - [ ]* 9.4 Write property test for manual IP non-assignment
    - **Property 30: Manual IP Non-Assignment**
    - **Validates: Requirements 10.2, 10.3**
    - Generate random manual IPs
    - Create VMs with manual IPs
    - Verify no IPAddress records are created or modified
    - Run 100 iterations

- [ ]* 10. Write JavaScript tests
  - [ ]* 10.1 Write tests for modal functionality
    - Test modal open on button click
    - Test modal close on cancel
    - Test modal state management
    - _Requirements: 1.2, 2.6, 2.7_
  
  - [ ]* 10.2 Write tests for form validation
    - Test IPv4 validation for VM IP field
    - Test IPv4 validation for Base Machine IP field
    - Test error message display
    - Test error clearing on correction
    - _Requirements: 3.2, 3.3_
  
  - [ ]* 10.3 Write tests for AJAX submission
    - Test form data collection
    - Test CSRF token inclusion
    - Test loading indicator display
    - Test success response handling
    - Test error response handling
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 11. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- The implementation uses existing HyperVService.create_vm() method without modification
- Frontend uses Bootstrap for modal styling (or custom modal if Bootstrap not available)
- AJAX requests use Fetch API or XMLHttpRequest depending on browser support requirements
- Property tests use Hypothesis for Python and fast-check for JavaScript
- All property tests configured to run minimum 100 iterations
