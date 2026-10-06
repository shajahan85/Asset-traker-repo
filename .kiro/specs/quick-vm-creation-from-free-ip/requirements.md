# Requirements Document

## Introduction

This feature adds quick virtual machine creation capability directly from the Free IP page. Currently, users must navigate to a separate Hyper-V VM management page to create VMs. This feature streamlines the workflow by allowing users to create VMs directly from the Free IP page where they can see available IP addresses, reducing navigation overhead and improving efficiency.

## Glossary

- **Free_IP_Page**: The web page that displays all IP addresses grouped by range with their occupancy status (free, occupied, or VM)
- **VM_Creation_Modal**: A modal dialog that appears when the user clicks the "Add VM" button
- **VM**: Virtual Machine tracked in the HyperVVM model
- **Base_Machine**: The physical host Asset that runs the virtual machine (referenced as host_machine in HyperVVM model)
- **VM_IP**: The IP address assigned to the virtual machine
- **Base_Machine_IP**: The IP address of the physical host machine
- **IP_Management_Service**: Service layer that handles IP address assignment and release operations
- **HyperV_Service**: Service layer that handles VM creation, update, and deletion operations
- **Search_Function**: The existing IP search functionality on the Free IP page

## Requirements

### Requirement 1: Add VM Button

**User Story:** As a user, I want to see an "Add VM" button on the Free IP page, so that I can quickly create a VM without navigating to a separate page.

#### Acceptance Criteria

1. THE Free_IP_Page SHALL display an "Add VM" button in a prominent location
2. WHEN the user clicks the "Add VM" button, THE Free_IP_Page SHALL display the VM_Creation_Modal
3. THE "Add VM" button SHALL be visible to all authenticated users

### Requirement 2: VM Creation Modal Form

**User Story:** As a user, I want to enter VM details in a modal form, so that I can create a VM quickly without leaving the Free IP page.

#### Acceptance Criteria

1. THE VM_Creation_Modal SHALL display a form with the following fields: VM IP address, VM name, and Base Machine IP
2. THE VM_Creation_Modal SHALL mark the VM IP address field as required
3. THE VM_Creation_Modal SHALL mark the Base Machine IP field as required
4. THE VM_Creation_Modal SHALL mark the VM name field as optional
5. THE VM_Creation_Modal SHALL provide a submit button labeled "Create VM"
6. THE VM_Creation_Modal SHALL provide a cancel button to close the modal without creating a VM
7. WHEN the user clicks the cancel button, THE VM_Creation_Modal SHALL close without making any changes

### Requirement 3: VM IP Address Input

**User Story:** As a user, I want to enter or select a VM IP address, so that I can assign an IP to the new virtual machine.

#### Acceptance Criteria

1. THE VM_Creation_Modal SHALL allow the user to enter a VM IP address manually
2. THE VM_Creation_Modal SHALL validate that the entered VM IP address is a valid IPv4 address
3. WHEN the user submits an invalid IP address format, THE VM_Creation_Modal SHALL display an error message indicating the IP format is invalid
4. THE VM_Creation_Modal SHALL check if the entered VM IP address is already assigned
5. WHEN the user submits an already assigned VM IP address, THE VM_Creation_Modal SHALL display an error message indicating the IP is already in use

### Requirement 4: Base Machine IP Lookup

**User Story:** As a user, I want to enter the Base Machine IP address, so that the system can identify which physical host will run the VM.

#### Acceptance Criteria

1. THE VM_Creation_Modal SHALL allow the user to enter a Base Machine IP address
2. WHEN the user submits the form, THE Free_IP_Page SHALL search for an Asset with an ip_address field matching the entered Base Machine IP
3. IF no Asset is found with the ip_address field, THE Free_IP_Page SHALL search for an Asset with a manual_ip field matching the entered Base Machine IP
4. IF no Asset is found with either ip_address or manual_ip matching the Base Machine IP, THE VM_Creation_Modal SHALL display an error message indicating no base machine was found with that IP
5. THE error message SHALL be descriptive and inform the user that the base machine IP was not found

### Requirement 5: VM Creation Processing

**User Story:** As a user, I want the system to create the VM when I submit valid data, so that the VM is registered in the system.

#### Acceptance Criteria

1. WHEN the user submits valid VM data, THE Free_IP_Page SHALL call HyperV_Service.create_vm() with the VM data
2. THE Free_IP_Page SHALL pass the VM name, Base_Machine reference, and VM IP address to HyperV_Service.create_vm()
3. IF the VM name field is empty, THE Free_IP_Page SHALL generate a default name in the format "VM-{Base_Machine_Asset_Tag}-{VM_IP}"
4. WHEN HyperV_Service.create_vm() succeeds, THE Free_IP_Page SHALL display a success message
5. WHEN HyperV_Service.create_vm() succeeds, THE VM_Creation_Modal SHALL close
6. WHEN HyperV_Service.create_vm() succeeds, THE Free_IP_Page SHALL refresh to show the newly created VM
7. WHEN HyperV_Service.create_vm() fails with a ValidationError, THE VM_Creation_Modal SHALL display the validation error message
8. WHEN HyperV_Service.create_vm() fails with any other error, THE VM_Creation_Modal SHALL display a generic error message

### Requirement 6: VM Display on Free IP Page

**User Story:** As a user, I want to see the newly created VM displayed on the Free IP page, so that I can verify it was created successfully.

#### Acceptance Criteria

1. WHEN a VM is created, THE Free_IP_Page SHALL display the VM IP with a blue background color
2. THE Free_IP_Page SHALL display the VM name below the VM IP address
3. THE Free_IP_Page SHALL display a link to the VM detail page
4. THE Free_IP_Page SHALL display the Base Machine IP in the VM relationship section
5. THE Free_IP_Page SHALL display a link to the Base Machine in the VM relationship section

### Requirement 7: Base Machine VM List Display

**User Story:** As a user, I want to see which VMs are hosted on a base machine, so that I can understand the VM-host relationships.

#### Acceptance Criteria

1. WHEN a Base_Machine hosts one or more VMs, THE Free_IP_Page SHALL display a list of hosted VMs below the Base_Machine IP
2. THE hosted VM list SHALL display each VM name and VM IP address
3. THE hosted VM list SHALL provide clickable links to each VM detail page
4. THE hosted VM list SHALL be visually indented to show the hierarchical relationship

### Requirement 8: Search Function Enhancement

**User Story:** As a user, I want to search for a VM IP and see its base machine IP, so that I can quickly find VM-host relationships.

#### Acceptance Criteria

1. WHEN the user searches for a VM IP address, THE Search_Function SHALL display the VM IP in the search results
2. WHEN the user searches for a VM IP address, THE Search_Function SHALL display the Base Machine IP in brackets next to the VM IP
3. THE Search_Function SHALL continue to support searching by IP address and assigned person name
4. THE Search_Function SHALL highlight matching VM IPs with the blue background color

### Requirement 9: AJAX Form Submission

**User Story:** As a user, I want the VM creation form to submit without a full page reload, so that I have a smooth user experience.

#### Acceptance Criteria

1. WHEN the user submits the VM creation form, THE VM_Creation_Modal SHALL submit the form data via AJAX
2. THE VM_Creation_Modal SHALL display a loading indicator while the request is processing
3. WHEN the AJAX request succeeds, THE VM_Creation_Modal SHALL close and refresh the IP list
4. WHEN the AJAX request fails, THE VM_Creation_Modal SHALL display the error message without closing
5. THE VM_Creation_Modal SHALL remain open if there are validation errors so the user can correct them

### Requirement 10: Manual IP Support

**User Story:** As a user, I want to create VMs with manual IP addresses, so that I can track VMs that use IPs outside the managed IP ranges.

#### Acceptance Criteria

1. THE VM_Creation_Modal SHALL allow the user to enter a manual VM IP address
2. WHEN the user enters a manual VM IP, THE Free_IP_Page SHALL store it in the HyperVVM.manual_ip field
3. WHEN the user enters a manual VM IP, THE Free_IP_Page SHALL not assign it to an IPAddress record
4. THE Free_IP_Page SHALL support Base Machines that use manual_ip instead of ip_address
5. WHEN displaying a VM with a manual IP, THE Free_IP_Page SHALL show the manual IP value
