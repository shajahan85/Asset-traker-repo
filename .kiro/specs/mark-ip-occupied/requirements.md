# Requirements Document

## Introduction

This feature adds the ability for administrators to manually mark free IP addresses as "occupied" directly from the Free IPs page. This is needed when network activity is detected on an IP (e.g., via network scan) but the specific device or asset is unknown. The IP should appear as occupied without being tied to a specific asset or guest, distinguishing it from normal asset assignments and guest assignments.

## Glossary

- **Free_IPs_Page**: The page at `/assets/ips/free/` that displays all IP addresses grouped by range with free/occupied status
- **IPAddress**: The Django model representing an IP address record, with fields for assignment status, asset linkage, and guest info
- **IPManagementService**: The service class responsible for IP address operations (assign, release, guest assign)
- **Admin_User**: An authenticated user with administrator privileges who can perform IP management actions
- **Occupied_IP**: An IP address that has been manually marked as in-use without being linked to a specific asset or guest
- **Mark_Occupied_Button**: A UI control that appears on hover over a free IP item, allowing the admin to initiate the mark-as-occupied action
- **Password_Prompt**: A modal dialog that requests the admin password before confirming a destructive or sensitive action

## Requirements

### Requirement 1: Display Mark as Occupied Button on Hover

**User Story:** As an admin, I want to see a "Mark as Occupied" button when I hover over a free IP address, so that I can quickly mark IPs that are detected as in-use.

#### Acceptance Criteria

1. WHILE the Admin_User hovers over a free IP item on the Free_IPs_Page, THE Mark_Occupied_Button SHALL become visible on that IP item
2. WHEN the Admin_User moves the cursor away from the free IP item, THE Mark_Occupied_Button SHALL be hidden
3. THE Mark_Occupied_Button SHALL only appear on IP items with occupant type "free"
4. THE Mark_Occupied_Button SHALL not appear on IP items that are already occupied, assigned to a guest, or assigned to a VM

### Requirement 2: Password Verification Before Marking

**User Story:** As an admin, I want to confirm my identity with a password before marking an IP as occupied, so that accidental or unauthorized changes are prevented.

#### Acceptance Criteria

1. WHEN the Admin_User clicks the Mark_Occupied_Button, THE System SHALL display the Password_Prompt modal
2. THE Password_Prompt SHALL include a password input field and the IP address being marked
3. WHEN the Admin_User submits a valid password, THE System SHALL proceed with marking the IP as occupied
4. IF the Admin_User submits an incorrect password, THEN THE System SHALL display an error message indicating the password is incorrect
5. WHEN the Admin_User cancels the Password_Prompt, THE System SHALL close the modal without making changes

### Requirement 3: Mark IP as Occupied in Backend

**User Story:** As an admin, I want the system to persist the occupied status of the IP, so that the IP no longer appears as free after marking.

#### Acceptance Criteria

1. WHEN a valid mark-occupied request is received, THE IPManagementService SHALL mark the IPAddress as assigned with `is_assigned` set to True
2. THE IPManagementService SHALL record a marker indicating the IP was manually marked as occupied (distinct from asset assignment or guest assignment)
3. THE IPManagementService SHALL record the username of the Admin_User who performed the action
4. THE IPManagementService SHALL record the timestamp of when the IP was marked as occupied
5. IF the IPAddress is already assigned when the request is processed, THEN THE IPManagementService SHALL return a validation error

### Requirement 4: Display Occupied Status on Free IPs Page

**User Story:** As an admin, I want manually-marked occupied IPs to display with a distinct visual indicator, so that I can differentiate them from asset-assigned or guest-assigned IPs.

#### Acceptance Criteria

1. WHEN an IP has been manually marked as occupied, THE Free_IPs_Page SHALL display the IP item with the "occupied" styling (red background)
2. THE Free_IPs_Page SHALL display a label indicating the IP was manually marked (e.g., "Manually Occupied")
3. THE Free_IPs_Page SHALL display the username of the admin who marked the IP
4. THE Free_IPs_Page SHALL display the date when the IP was marked as occupied

### Requirement 5: API Endpoint for Mark as Occupied

**User Story:** As a developer, I want a dedicated AJAX endpoint for marking IPs as occupied, so that the frontend can perform the action without a full page reload.

#### Acceptance Criteria

1. THE System SHALL expose a POST endpoint for marking an IP as occupied
2. THE endpoint SHALL require authentication and admin privileges
3. WHEN a valid request is received with correct password and IP address, THE endpoint SHALL return a success response with the updated IP status
4. IF the password verification fails, THEN THE endpoint SHALL return an error response with HTTP status 403
5. IF the specified IP address does not exist, THEN THE endpoint SHALL return an error response with HTTP status 404
6. IF the IP address is already assigned, THEN THE endpoint SHALL return an error response with HTTP status 400
