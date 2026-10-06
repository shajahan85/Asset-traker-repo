# Requirements Document

## Introduction

This feature enables tracking of testing devices (mobile phones and tablets) that are assigned to team members for testing purposes. These devices consume IP addresses and need to be tracked separately from regular IT assets. The system will manage device assignments, track usage history, and integrate with the existing IP address management system. The feature provides a dedicated interface following the same patterns as the existing Network Device and Hyper-V VM tracking modules.

## Glossary

- **Testing_Device**: A mobile phone or tablet used for testing purposes by the team
- **Device_Assignment**: The relationship between a Testing_Device and a User or Team
- **IP_Management_System**: The existing system that tracks IP addresses and their assignment status
- **Admin_User**: A user with administrative privileges who can manage testing devices
- **Device_Type**: The category of testing device (Mobile Phone, Tablet)
- **Device_Status**: The current state of the device (Available, In Use, Under Repair)
- **Assignment_History**: A chronological record of Testing_Device assignments to users
- **Team_Model**: The existing hierarchical team structure in the Asset Tracker
- **Branch_Model**: The existing branch/location structure in the Asset Tracker
- **Export_Service**: The existing service that exports data to Excel format

## Requirements

### Requirement 1: Store Testing Device Information

**User Story:** As an admin, I want to store comprehensive testing device information, so that I can track device details and assignments.

#### Acceptance Criteria

1. THE Testing_Device SHALL store a device name (e.g., "iPhone 12 Pro", "Samsung Galaxy Tab S8")
2. THE Testing_Device SHALL store a device type from the predefined list (Mobile Phone, Tablet)
3. THE Testing_Device SHALL store an optional model/specifications field
4. THE Testing_Device SHALL store an OS/version field (e.g., "iOS 15", "Android 12")
5. THE Testing_Device SHALL store a serial number or IMEI for unique identification
6. THE Testing_Device SHALL store an assigned IP address reference
7. THE Testing_Device SHALL store a user/team assignment field
8. THE Testing_Device SHALL store a branch reference
9. THE Testing_Device SHALL store a device status from the predefined list (Available, In Use, Under Repair)
10. THE Testing_Device SHALL store creation and modification timestamps
11. THE Testing_Device SHALL enforce uniqueness of serial numbers/IMEI across all testing devices
12. THE Testing_Device SHALL enforce uniqueness of IP addresses across all testing devices

### Requirement 2: Create Testing Devices

**User Story:** As an admin, I want to create new testing device records, so that I can register devices available for testing.

#### Acceptance Criteria

1. WHEN an Admin_User submits a valid testing device form, THE System SHALL create a new Testing_Device record
2. THE System SHALL require device name, device type, OS/version, serial number/IMEI, and branch fields for Testing_Device creation
3. THE System SHALL allow optional fields for model/specifications, IP address, user assignment, team assignment, and status
4. WHEN a Testing_Device is created with an IP address from the IP_Management_System, THE System SHALL mark that IP address as occupied
5. WHEN a Testing_Device is created with a manual IP address, THE System SHALL store the IP address without marking it in the IP_Management_System
6. IF an Admin_User attempts to create a Testing_Device with an IP address already assigned to another device or asset, THEN THE System SHALL reject the creation and display an error message
7. IF an Admin_User attempts to create a Testing_Device with a duplicate serial number/IMEI, THEN THE System SHALL reject the creation and display an error message
8. WHEN a Testing_Device is successfully created, THE System SHALL redirect the Admin_User to the testing device list page
9. WHEN a Testing_Device is successfully created, THE System SHALL display a success message

### Requirement 3: Edit Testing Devices

**User Story:** As an admin, I want to edit existing testing device records, so that I can update device information when changes occur.

#### Acceptance Criteria

1. WHEN an Admin_User submits an updated testing device form, THE System SHALL update the Testing_Device record
2. THE System SHALL allow updating all Testing_Device fields including device name, device type, model/specifications, OS/version, serial number/IMEI, IP address, user assignment, team assignment, branch, and device status
3. WHEN a Testing_Device IP address is changed from one managed IP to another, THE IP_Management_System SHALL mark the old IP address as free and the new IP address as occupied
4. WHEN a Testing_Device IP address is changed from a managed IP to a manual IP, THE IP_Management_System SHALL mark the old IP address as free
5. WHEN a Testing_Device IP address is changed from a manual IP to a managed IP, THE IP_Management_System SHALL mark the new IP address as occupied
6. IF an Admin_User attempts to change an IP address to one already assigned to another device or asset, THEN THE System SHALL reject the update and display an error message
7. IF an Admin_User attempts to change a serial number/IMEI to one already used by another device, THEN THE System SHALL reject the update and display an error message
8. WHEN a Testing_Device is successfully updated, THE System SHALL redirect the Admin_User to the testing device list page
9. WHEN a Testing_Device is successfully updated, THE System SHALL display a success message

### Requirement 4: Delete Testing Devices

**User Story:** As an admin, I want to delete testing device records, so that I can remove devices that are no longer in the inventory.

#### Acceptance Criteria

1. WHEN an Admin_User confirms deletion of a Testing_Device, THE System SHALL delete the Testing_Device record
2. WHEN a Testing_Device with a managed IP address is deleted, THE IP_Management_System SHALL mark the associated IP address as free
3. WHEN a Testing_Device with assignment history is deleted, THE System SHALL preserve the Assignment_History records
4. THE System SHALL require confirmation before deleting a Testing_Device
5. WHEN a Testing_Device is successfully deleted, THE System SHALL redirect the Admin_User to the testing device list page
6. WHEN a Testing_Device is successfully deleted, THE System SHALL display a success message

### Requirement 5: List Testing Devices with Filtering

**User Story:** As a user, I want to view a list of all testing devices with filtering options, so that I can find specific devices quickly.

#### Acceptance Criteria

1. THE System SHALL provide a dedicated page listing all Testing_Device records
2. THE Testing_Device list SHALL display device name, device type, user assignment, team assignment, IP address, branch, and device status for each device
3. THE Testing_Device list SHALL display devices in a sortable table format ordered by device name
4. THE Testing_Device list SHALL provide filter options for device name search
5. THE Testing_Device list SHALL provide filter options for user assignment search
6. THE Testing_Device list SHALL provide filter options for team assignment
7. THE Testing_Device list SHALL provide filter options for IP address search
8. THE Testing_Device list SHALL provide filter options for branch
9. THE Testing_Device list SHALL provide filter options for device type
10. THE Testing_Device list SHALL provide filter options for device status
11. WHEN filter criteria are applied, THE System SHALL display only Testing_Device records matching all selected filters
12. THE System SHALL preserve filter selections when navigating back to the list page
13. THE Testing_Device list SHALL provide links to edit and delete each device for Admin_User accounts

### Requirement 6: Track Assignment History

**User Story:** As an admin, I want to track the assignment history of testing devices, so that I can see who used which device and when.

#### Acceptance Criteria

1. WHEN a Testing_Device user assignment is created or changed, THE System SHALL create an Assignment_History record
2. THE Assignment_History SHALL store the Testing_Device reference, assigned user, assigned team, assignment start timestamp, and assignment end timestamp
3. WHEN a Testing_Device user assignment is changed, THE System SHALL set the end timestamp on the previous Assignment_History record
4. WHEN a Testing_Device user assignment is removed, THE System SHALL set the end timestamp on the current Assignment_History record
5. THE System SHALL provide a view showing Assignment_History for a specific Testing_Device
6. THE Assignment_History view SHALL display all historical assignments in chronological order with most recent first
7. FOR EACH Assignment_History record, THE System SHALL display the assigned user, assigned team, start date, and end date
8. WHEN an assignment is currently active, THE Assignment_History view SHALL display "Present" for the end date
9. THE System SHALL allow filtering Assignment_History by user, team, or date range

### Requirement 7: Display Testing Devices in Free IP Page

**User Story:** As a user, I want to see testing devices on the Free IP page, so that I can understand which IPs are occupied by testing devices.

#### Acceptance Criteria

1. WHEN a Testing_Device occupies a managed IP address, THE Free_IP_Page SHALL display that IP address as occupied
2. WHEN a user hovers over an IP address occupied by a Testing_Device, THE Free_IP_Page SHALL display the device name and assigned user in the tooltip
3. THE Free_IP_Page SHALL visually distinguish IP addresses occupied by testing devices from those occupied by assets, network devices, and VMs
4. THE Free_IP_Page SHALL support searching for Testing_Device records by device name or assigned user
5. WHEN a Testing_Device uses a manual IP address, THE Free_IP_Page SHALL not display that IP address

### Requirement 8: Export Testing Devices to Excel

**User Story:** As an admin, I want to export testing device data to Excel, so that I can analyze or share device information externally.

#### Acceptance Criteria

1. THE System SHALL provide an export button on the testing device list page
2. WHEN an Admin_User clicks the export button, THE System SHALL generate an Excel file containing all visible Testing_Device records
3. THE Excel export SHALL include columns for device name, device type, model/specifications, OS/version, serial number/IMEI, IP address, user assignment, team assignment, branch, and device status
4. WHEN filters are applied to the testing device list, THE Excel export SHALL include only the filtered Testing_Device records
5. THE System SHALL use the existing Export_Service pattern for consistency
6. THE Excel file SHALL be named with a timestamp (e.g., "testing_devices_2024-01-15.xlsx")
7. WHEN the export is complete, THE System SHALL trigger a file download in the user's browser

### Requirement 9: Restrict Management to Admin Users

**User Story:** As a system administrator, I want to restrict testing device management to admin users only, so that unauthorized users cannot modify device records.

#### Acceptance Criteria

1. THE System SHALL require Admin_User authentication for testing device create, edit, and delete operations
2. THE System SHALL allow all authenticated users to view the testing device list page
3. IF a non-admin user attempts to access testing device management pages, THEN THE System SHALL redirect them to the login page
4. THE System SHALL display testing device management action buttons (create, edit, delete) only to Admin_User accounts
5. THE Testing_Device list page SHALL be accessible to all authenticated users for visibility

### Requirement 10: Integrate with Team and Branch Models

**User Story:** As an admin, I want testing devices to use existing team and branch structures, so that device assignments align with organizational structure.

#### Acceptance Criteria

1. THE Testing_Device SHALL reference the existing Branch_Model for branch assignment
2. THE Testing_Device SHALL reference the existing Team_Model for team assignment
3. WHEN creating or editing a Testing_Device, THE System SHALL display available branches from the Branch_Model
4. WHEN a branch is selected, THE System SHALL display only teams belonging to that branch
5. THE System SHALL allow a Testing_Device to be assigned to a user without a team assignment
6. THE System SHALL allow a Testing_Device to be assigned to a team without a specific user assignment
7. THE System SHALL enforce that if a team is assigned, the Testing_Device branch must match the team's branch
8. WHEN a Testing_Device is assigned to a team, THE System SHALL allow assignment to a parent team or a sub-team

### Requirement 11: Validate Testing Device Data

**User Story:** As an admin, I want the system to validate testing device data, so that only valid information can be entered.

#### Acceptance Criteria

1. WHEN an Admin_User enters an IP address for a Testing_Device, THE System SHALL validate that it is a valid IPv4 address
2. IF an Admin_User enters an invalid IP address format, THEN THE System SHALL reject the submission and display a validation error message
3. THE System SHALL validate that device name, device type, OS/version, serial number/IMEI, and branch are provided before allowing Testing_Device creation
4. THE System SHALL validate that serial number/IMEI is unique across all Testing_Device records
5. THE System SHALL validate that if a managed IP address is provided, it is not already assigned to another device or asset
6. THE System SHALL use the same IP address validation rules for Testing_Device records as for Asset and Network_Device records

### Requirement 12: Support Manual and Managed IP Addresses

**User Story:** As an admin, I want to assign either managed or manual IP addresses to testing devices, so that I can track devices with IPs outside the managed ranges.

#### Acceptance Criteria

1. WHEN creating a Testing_Device, THE System SHALL allow selecting an IP address from the IP_Management_System dropdown
2. WHEN creating a Testing_Device, THE System SHALL allow manual entry of an IP address
3. THE System SHALL allow a Testing_Device to have no IP address assigned
4. THE System SHALL prevent assigning both a managed IP address and a manual IP address to the same Testing_Device
5. WHEN a managed IP address is selected, THE System SHALL mark that IP as occupied in the IP_Management_System
6. WHEN a manual IP address is entered, THE System SHALL store the IP address but not mark it in the IP_Management_System
7. THE Testing_Device list page SHALL display both managed and manual IP addresses in the IP address column

### Requirement 13: Testing Device Status Transitions

**User Story:** As an admin, I want to track device status changes, so that I can manage device availability.

#### Acceptance Criteria

1. THE System SHALL allow changing Testing_Device status from any status to any other status
2. WHEN a Testing_Device status is changed to "Under Repair", THE System SHALL allow the device to remain assigned to a user
3. WHEN a Testing_Device status is changed to "Available", THE System SHALL allow clearing the user assignment
4. THE System SHALL record status changes in the Testing_Device modification timestamp
5. THE Testing_Device list page SHALL visually distinguish devices by status using color coding or icons

### Requirement 14: Display Assignment Information

**User Story:** As a user, I want to see who is using each testing device, so that I know which devices are available.

#### Acceptance Criteria

1. THE Testing_Device list page SHALL display the currently assigned user for each device
2. THE Testing_Device list page SHALL display the currently assigned team for each device
3. WHEN a Testing_Device has no user assignment, THE System SHALL display "Available" or "Unassigned"
4. WHEN a Testing_Device is assigned to a sub-team, THE System SHALL display the full team hierarchy (e.g., "Parent Team > Sub-Team")
5. THE Testing_Device list page SHALL highlight devices with status "Available" for easy identification

### Requirement 15: Testing Device Form User Experience

**User Story:** As an admin, I want an intuitive form for managing testing devices, so that I can efficiently enter and update device information.

#### Acceptance Criteria

1. THE Testing_Device form SHALL use the same UI patterns as existing Asset, Network_Device, and Hyper_V_VM forms
2. THE Testing_Device form SHALL support both dropdown IP selection and manual IP entry with a toggle or separate input field
3. WHEN a branch is selected, THE Testing_Device form SHALL dynamically update the team dropdown to show only teams from that branch
4. THE Testing_Device form SHALL display validation errors inline next to the relevant fields
5. THE Testing_Device form SHALL pre-populate existing values when editing a Testing_Device
6. THE Testing_Device form SHALL provide a cancel button that returns to the testing device list page without saving changes
7. THE Testing_Device form SHALL set default status to "Available" for new Testing_Device records
