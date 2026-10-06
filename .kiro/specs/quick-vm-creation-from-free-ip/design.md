# Design Document: Quick VM Creation from Free IP

## Overview

This feature adds a streamlined VM creation workflow directly to the Free IP page, eliminating the need for users to navigate to a separate Hyper-V VM management page. The design introduces a modal-based form that allows users to quickly create virtual machines while viewing available IP addresses, improving operational efficiency and reducing context switching.

The implementation leverages the existing HyperVVM model, HyperVService, and IPManagementService infrastructure, adding a new AJAX-based UI layer on top of the Free IP page. The design maintains consistency with the existing codebase architecture while introducing modern UX patterns (modal dialogs, AJAX submissions) for improved user experience.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Free IP Page (View)                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  IP List Display                                        │ │
│  │  - Grouped by IP Range                                  │ │
│  │  - Color-coded (Free/Occupied/VM)                       │ │
│  │  - Search functionality                                 │ │
│  │  - VM relationship display                              │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  "Add VM" Button                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  VM Creation Modal (JavaScript)                         │ │
│  │  - Form fields (VM IP, Base Machine IP, VM Name)       │ │
│  │  - Client-side validation                               │ │
│  │  - AJAX form submission                                 │ │
│  │  - Error display                                        │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ AJAX POST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              QuickVMCreateView (Django View)                 │
│  - Validates form data                                       │
│  - Looks up base machine by IP                               │
│  - Generates default VM name if needed                       │
│  - Calls HyperVService.create_vm()                           │
│  - Returns JSON response                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   HyperVService                              │
│  - create_vm(data, user)                                     │
│  - Handles IP assignment via IPManagementService             │
│  - Creates HyperVVM instance                                 │
│  - Transaction management                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 IPManagementService                          │
│  - assign_ip(ip_address, asset)                              │
│  - Marks IP as assigned                                      │
│  - Updates IP relationships                                  │
└─────────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. User clicks "Add VM" button on Free IP page
2. JavaScript displays modal dialog with form
3. User fills in VM IP, Base Machine IP, and optionally VM name
4. JavaScript validates input client-side
5. Form submits via AJAX to QuickVMCreateView
6. View validates data and looks up base machine
7. View generates default VM name if not provided
8. View calls HyperVService.create_vm()
9. Service assigns IP via IPManagementService
10. Service creates HyperVVM record
11. View returns JSON response (success or error)
12. JavaScript handles response (close modal, refresh page, or show error)

## Components and Interfaces

### 1. Frontend Components

#### Add VM Button
- Location: Free IP page header or prominent position
- Visibility: All authenticated users
- Action: Opens VM Creation Modal

#### VM Creation Modal
- Framework: Bootstrap Modal or custom modal implementation
- Fields:
  - VM IP Address (text input, required)
  - Base Machine IP (text input, required)
  - VM Name (text input, optional)
- Buttons:
  - "Create VM" (submit)
  - "Cancel" (close modal)
- Features:
  - Client-side validation
  - Loading indicator during submission
  - Error message display
  - AJAX form submission

#### JavaScript Module: vm_creation.js
```javascript
// Core functions
- initVMCreationModal()
- validateVMIP(ip)
- validateBaseMachineIP(ip)
- submitVMForm(formData)
- handleSuccess(response)
- handleError(error)
- refreshIPList()
```

### 2. Backend Components

#### QuickVMCreateView (New Django View)
```python
class QuickVMCreateView(AdminRequiredMixin, View):
    """Handle quick VM creation from Free IP page via AJAX."""
    
    def post(self, request):
        """
        Process VM creation request.
        
        Expected POST data:
        - vm_ip: str (IP address for the VM)
        - base_machine_ip: str (IP address of host machine)
        - vm_name: str (optional, auto-generated if empty)
        
        Returns:
        - JSON response with success/error status
        """
```

**Responsibilities:**
- Validate POST data
- Look up base machine by IP (check ip_address field, then manual_ip field)
- Generate default VM name if not provided: "VM-{asset_tag}-{vm_ip}"
- Determine if VM IP is managed or manual
- Call HyperVService.create_vm() with prepared data
- Handle exceptions and return appropriate JSON responses

**Response Format:**
```json
// Success
{
  "success": true,
  "message": "VM created successfully",
  "vm_id": 123,
  "vm_name": "VM-BIDC001-192.168.1.100"
}

// Error
{
  "success": false,
  "error": "Error message",
  "field_errors": {
    "vm_ip": ["IP address is already assigned"],
    "base_machine_ip": ["No base machine found with this IP"]
  }
}
```

#### URL Configuration
```python
# assets/urls.py
path('vms/quick-create/', QuickVMCreateView.as_view(), name='quick_vm_create'),
```

### 3. Service Layer Integration

#### HyperVService.create_vm() Enhancement
The existing `create_vm()` method will be used as-is, but the view will prepare data appropriately:

```python
# Data preparation in QuickVMCreateView
data = {
    'name': vm_name,  # Generated or provided
    'host_machine': base_machine_asset,  # Looked up by IP
    'ip_address': ip_address_obj if is_managed else None,
    'manual_ip': vm_ip if not is_managed else None,
    'notes': ''
}
```

#### Base Machine Lookup Logic
```python
def lookup_base_machine(ip_address_str):
    """
    Look up Asset by IP address.
    
    Search order:
    1. Asset.ip_address (managed IP)
    2. Asset.manual_ip (manual IP)
    
    Returns:
        Asset instance or None
    """
    # Try managed IP first
    try:
        ip_obj = IPAddress.objects.get(address=ip_address_str)
        if ip_obj.assigned_to_asset:
            return ip_obj.assigned_to_asset
    except IPAddress.DoesNotExist:
        pass
    
    # Try manual IP
    asset = Asset.objects.filter(
        manual_ip=ip_address_str,
        status='active'
    ).first()
    
    return asset
```

#### VM IP Handling Logic
```python
def determine_vm_ip_type(vm_ip_str):
    """
    Determine if VM IP is managed or manual.
    
    Returns:
        tuple: (is_managed: bool, ip_obj: IPAddress or None)
    """
    try:
        ip_obj = IPAddress.objects.get(address=vm_ip_str)
        if not ip_obj.is_assigned:
            return (True, ip_obj)
        else:
            raise ValidationError("IP address is already assigned")
    except IPAddress.DoesNotExist:
        # Manual IP
        return (False, None)
```

### 4. Template Updates

#### free_ips.html Modifications
1. Add "Add VM" button to page header
2. Add modal HTML structure
3. Include vm_creation.js script
4. Add CSRF token for AJAX requests

```html
<!-- Add VM Button -->
<div class="header-actions">
    <h1>IP Addresses</h1>
    <button id="addVMButton" class="btn btn-primary">Add VM</button>
    <a href="{% url 'export_free_ips' %}" class="btn btn-success">Export Free IPs to Excel</a>
</div>

<!-- VM Creation Modal -->
<div id="vmCreationModal" class="modal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Create Virtual Machine</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="vmCreationForm">
                    <div class="mb-3">
                        <label for="vmIP" class="form-label">VM IP Address *</label>
                        <input type="text" class="form-control" id="vmIP" name="vm_ip" required>
                        <div class="invalid-feedback"></div>
                    </div>
                    <div class="mb-3">
                        <label for="baseMachineIP" class="form-label">Base Machine IP *</label>
                        <input type="text" class="form-control" id="baseMachineIP" name="base_machine_ip" required>
                        <div class="invalid-feedback"></div>
                    </div>
                    <div class="mb-3">
                        <label for="vmName" class="form-label">VM Name (optional)</label>
                        <input type="text" class="form-control" id="vmName" name="vm_name">
                        <small class="form-text text-muted">Leave empty to auto-generate</small>
                    </div>
                    <div id="formErrors" class="alert alert-danger d-none"></div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" id="createVMButton" class="btn btn-primary">
                    <span class="spinner-border spinner-border-sm d-none" role="status"></span>
                    Create VM
                </button>
            </div>
        </div>
    </div>
</div>
```

## Data Models

No new models are required. The feature uses existing models:

### HyperVVM (Existing)
```python
class HyperVVM(models.Model):
    name = models.CharField(max_length=200, unique=True)
    host_machine = models.ForeignKey(Asset, on_delete=models.PROTECT)
    ip_address = models.ForeignKey(IPAddress, null=True, blank=True)
    manual_ip = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

### Asset (Existing)
Used for base machine lookup via `ip_address` or `manual_ip` fields.

### IPAddress (Existing)
Used for managed IP assignment and validation.

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Modal Display on Button Click

*For any* authenticated user, when the "Add VM" button is clicked, the VM Creation Modal should become visible.

**Validates: Requirements 1.2**

### Property 2: Cancel Button Closes Modal Without Side Effects

*For any* modal state, when the cancel button is clicked, the modal should close and no HyperVVM record should be created.

**Validates: Requirements 2.7**

### Property 3: IPv4 Validation

*For any* string input to the VM IP field, the system should accept it if and only if it is a valid IPv4 address format.

**Validates: Requirements 3.2**

### Property 4: Invalid IP Format Error Display

*For any* invalid IPv4 format submitted, the system should display an error message indicating the IP format is invalid.

**Validates: Requirements 3.3**

### Property 5: Assigned IP Rejection

*For any* IP address that is already assigned (is_assigned=True or used by another VM), attempting to create a VM with that IP should fail with an error message indicating the IP is already in use.

**Validates: Requirements 3.4, 3.5**

### Property 6: Base Machine Lookup by Managed IP

*For any* Asset with an assigned IPAddress, when that IP address string is provided as the Base Machine IP, the system should find and return that Asset.

**Validates: Requirements 4.2**

### Property 7: Base Machine Lookup by Manual IP

*For any* Asset with a manual_ip value and no ip_address, when that manual IP string is provided as the Base Machine IP, the system should find and return that Asset.

**Validates: Requirements 4.3**

### Property 8: Base Machine Not Found Error

*For any* IP address string that does not match any Asset's ip_address or manual_ip, the system should display an error message indicating no base machine was found with that IP.

**Validates: Requirements 4.4**

### Property 9: Default VM Name Generation

*For any* base machine Asset and VM IP address, when the VM name field is empty, the system should generate a name in the format "VM-{asset_tag}-{vm_ip}".

**Validates: Requirements 5.3**

### Property 10: Service Call with Correct Parameters

*For any* valid VM creation request, the view should call HyperVService.create_vm() with a data dictionary containing name, host_machine, and either ip_address or manual_ip.

**Validates: Requirements 5.1, 5.2**

### Property 11: Success Feedback and Modal Closure

*For any* successful VM creation, the system should display a success message, close the modal, and refresh the IP list to show the new VM.

**Validates: Requirements 5.4, 5.5, 5.6**

### Property 12: Validation Error Display

*For any* ValidationError raised by HyperVService.create_vm(), the modal should display the validation error message and remain open.

**Validates: Requirements 5.7, 9.5**

### Property 13: Generic Error Handling

*For any* non-ValidationError exception during VM creation, the modal should display a generic error message and remain open.

**Validates: Requirements 5.8**

### Property 14: VM Display with Blue Background

*For any* created VM, the Free IP page should display the VM's IP address with a blue background color (CSS class 'vm').

**Validates: Requirements 6.1**

### Property 15: VM Name Display

*For any* created VM, the Free IP page should display the VM name below the VM IP address.

**Validates: Requirements 6.2**

### Property 16: VM Detail Link

*For any* created VM, the Free IP page should display a clickable link to the VM detail page with the correct URL.

**Validates: Requirements 6.3**

### Property 17: Host Machine IP Display

*For any* VM displayed on the Free IP page, the system should display the host machine's IP address in the VM relationship section.

**Validates: Requirements 6.4**

### Property 18: Host Machine Link

*For any* VM displayed on the Free IP page, the system should display a clickable link to the host machine's detail page.

**Validates: Requirements 6.5**

### Property 19: Hosted VMs List Display

*For any* base machine Asset that hosts one or more VMs, the Free IP page should display a list of all hosted VMs below the base machine's IP.

**Validates: Requirements 7.1**

### Property 20: Hosted VM Information Completeness

*For any* VM in the hosted VMs list, the display should include both the VM name and VM IP address.

**Validates: Requirements 7.2**

### Property 21: Hosted VM Links

*For any* VM in the hosted VMs list, there should be a clickable link to that VM's detail page.

**Validates: Requirements 7.3**

### Property 22: VM Search Result Display

*For any* VM IP address, when searched, the search function should display that VM IP in the search results.

**Validates: Requirements 8.1**

### Property 23: Host IP in Search Results

*For any* VM IP address in search results, the system should display the base machine IP in brackets next to the VM IP.

**Validates: Requirements 8.2**

### Property 24: Search Functionality Preservation

*For any* IP address or assigned person name, the search function should continue to return matching results as it did before this feature.

**Validates: Requirements 8.3**

### Property 25: AJAX Form Submission

*For any* VM creation form submission, the form data should be sent via AJAX (XMLHttpRequest or Fetch API) rather than a traditional form POST.

**Validates: Requirements 9.1**

### Property 26: Loading Indicator Display

*For any* VM creation form submission, a loading indicator should be visible while the AJAX request is in progress.

**Validates: Requirements 9.2**

### Property 27: Success Response Handling

*For any* successful AJAX response, the modal should close and the IP list should refresh to show the newly created VM.

**Validates: Requirements 9.3**

### Property 28: Error Response Handling

*For any* failed AJAX response, the modal should remain open and display the error message.

**Validates: Requirements 9.4**

### Property 29: Manual VM IP Storage

*For any* VM created with a manual IP (not in IPAddress table), the system should store the IP value in the HyperVVM.manual_ip field.

**Validates: Requirements 10.2**

### Property 30: Manual IP Non-Assignment

*For any* VM created with a manual IP, the system should not create or modify any IPAddress record.

**Validates: Requirements 10.3**

### Property 31: Manual IP Base Machine Support

*For any* base machine Asset using manual_ip instead of ip_address, the base machine lookup should successfully find that Asset.

**Validates: Requirements 10.4**

### Property 32: Manual IP Display

*For any* VM with a manual_ip value, the Free IP page should display that manual IP value.

**Validates: Requirements 10.5**

## Error Handling

### Client-Side Validation Errors
- Invalid IP format: Display inline error below field
- Empty required fields: Display inline error below field
- Errors should be cleared when user corrects input

### Server-Side Validation Errors
- IP already assigned: Return field error for vm_ip
- Base machine not found: Return field error for base_machine_ip
- Duplicate VM name: Return field error for vm_name
- Invalid IP format (server-side check): Return field error for vm_ip

### Service Layer Errors
- ValidationError from HyperVService: Display specific error message
- Database errors: Display generic error message
- Transaction rollback on any error

### Network Errors
- AJAX request timeout: Display "Request timed out" message
- Network failure: Display "Network error, please try again" message
- Server 500 error: Display "Server error, please contact administrator" message

### Error Response Format
```json
{
  "success": false,
  "error": "General error message",
  "field_errors": {
    "vm_ip": ["Specific error for VM IP field"],
    "base_machine_ip": ["Specific error for base machine IP field"]
  }
}
```

## Testing Strategy

### Unit Testing

Unit tests will focus on specific examples, edge cases, and error conditions:

1. **View Tests**
   - Test QuickVMCreateView with valid data
   - Test with missing required fields
   - Test with invalid IP formats
   - Test with already assigned IPs
   - Test with non-existent base machine IPs
   - Test default name generation
   - Test manual IP handling

2. **Base Machine Lookup Tests**
   - Test lookup by managed IP
   - Test lookup by manual IP
   - Test lookup failure scenarios

3. **VM IP Type Determination Tests**
   - Test managed IP detection
   - Test manual IP detection
   - Test already assigned IP rejection

4. **JavaScript Tests**
   - Test modal open/close
   - Test form validation
   - Test AJAX submission
   - Test success/error handling
   - Test loading indicator

### Property-Based Testing

Property tests will verify universal properties across all inputs using Hypothesis (Python) and fast-check (JavaScript):

**Python Property Tests (using Hypothesis):**

1. **Property Test: IPv4 Validation**
   - Generate random strings
   - Verify only valid IPv4 addresses pass validation
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 3: IPv4 Validation**
   - Iterations: 100

2. **Property Test: Base Machine Lookup**
   - Generate random Assets with various IP configurations
   - Verify lookup finds correct Asset for any valid IP
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 6: Base Machine Lookup by Managed IP**
   - Iterations: 100

3. **Property Test: Default Name Generation**
   - Generate random asset tags and IP addresses
   - Verify name format is always "VM-{tag}-{ip}"
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 9: Default VM Name Generation**
   - Iterations: 100

4. **Property Test: Manual IP Non-Assignment**
   - Generate random manual IPs
   - Create VMs with manual IPs
   - Verify no IPAddress records are created or modified
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 30: Manual IP Non-Assignment**
   - Iterations: 100

**JavaScript Property Tests (using fast-check):**

1. **Property Test: Modal State Management**
   - Generate random sequences of open/close actions
   - Verify modal state is always consistent
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 1: Modal Display on Button Click**
   - Iterations: 100

2. **Property Test: Form Validation**
   - Generate random form inputs
   - Verify validation rules are consistently applied
   - Tag: **Feature: quick-vm-creation-from-free-ip, Property 3: IPv4 Validation**
   - Iterations: 100

### Integration Testing

1. **End-to-End VM Creation Flow**
   - Test complete flow from button click to VM display
   - Verify database state after creation
   - Verify IP assignment state

2. **Search Integration**
   - Test VM search functionality
   - Verify VM-host relationships in search results

3. **Page Refresh Integration**
   - Test that newly created VMs appear correctly
   - Verify color coding and styling
   - Verify links are functional

### Configuration

- All property tests configured to run minimum 100 iterations
- Use Django TestCase with transaction support for database tests
- Use Selenium or Playwright for JavaScript integration tests
- Mock external dependencies where appropriate
- Use factory_boy for test data generation

