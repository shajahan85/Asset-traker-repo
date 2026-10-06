# Requirements Document

## Introduction

This feature redesigns the IP address entry system in Django Asset Tracker to eliminate user confusion. The current implementation uses confusing labels ("Primary IP (LAN)" and "Secondary IP (WiFi)") that don't match real-world usage patterns. Users need a simpler primary IP field and the ability to add multiple additional IP addresses with custom descriptions for devices with multiple network interfaces.

## Glossary

- **System**: The Django Asset Tracker application
- **Asset**: A tracked IT asset (Desktop, Laptop, or All-in-One PC)
- **Primary_IP**: The main IP address for an asset (no special label, just "IP Address")
- **Additional_IP**: Any supplementary IP address beyond the primary IP
- **IP_Label**: A user-defined description for an Additional_IP (e.g., "Mobile IP", "WiFi IP", "System IP")
- **Managed_IP**: An IP address selected from the managed IP address pool
- **Manual_IP**: An IP address entered manually by the user (not tracked in IP management)
- **IP_Pool**: The collection of available IP addresses managed by the System
- **AssetIPAddress**: The junction model linking Assets to their IP addresses
- **Asset_Form**: The Django form used to create and edit Assets
- **IP_Entry_Mode**: The selection between Managed_IP or Manual_IP entry

## Requirements

### Requirement 1: Simplify Primary IP Address Entry

**User Story:** As a user, I want a simple "IP Address" field without confusing labels, so that I can quickly assign an IP to an asset without being confused by "Primary" or "LAN" terminology.

#### Acceptance Criteria

1. THE Asset_Form SHALL display "IP Address" as the label for the primary IP field (not "Primary IP (LAN)")
2. THE Asset_Form SHALL provide radio button options for IP_Entry_Mode selection (Managed_IP or Manual_IP)
3. WHEN a user selects Managed_IP mode, THE Asset_Form SHALL display a dropdown of available IPs from the IP_Pool
4. WHEN a user selects Manual_IP mode, THE Asset_Form SHALL display a text input field for manual IP entry
5. THE System SHALL validate Manual_IP entries as valid IPv4 addresses
6. THE Asset_Form SHALL allow the primary IP field to be optional (assets may not have IPs)

### Requirement 2: Support Multiple Additional IP Addresses

**User Story:** As a user, I want to add multiple additional IP addresses to an asset, so that I can track devices with multiple network interfaces (e.g., laptop with LAN and WiFi).

#### Acceptance Criteria

1. THE Asset_Form SHALL provide an "Additional IP Addresses" section below the primary IP field
2. THE Additional_IP section SHALL allow users to add zero or more additional IPs
3. WHEN a user adds an Additional_IP, THE Asset_Form SHALL provide an IP_Label text field for description
4. WHEN a user adds an Additional_IP, THE Asset_Form SHALL provide IP_Entry_Mode options (Managed_IP or Manual_IP)
5. WHEN Managed_IP mode is selected for an Additional_IP, THE Asset_Form SHALL display a dropdown of available IPs from the IP_Pool
6. WHEN Manual_IP mode is selected for an Additional_IP, THE Asset_Form SHALL display a text input field
7. THE System SHALL validate that each Additional_IP has a unique combination of IP address and IP_Label within an Asset
8. THE Asset_Form SHALL allow users to remove Additional_IP entries before saving

### Requirement 3: Preserve IP Address Data Model

**User Story:** As a system maintainer, I want the existing data model to remain compatible, so that existing assets retain their IP assignments without data loss.

#### Acceptance Criteria

1. THE System SHALL continue using the AssetIPAddress junction model for storing IP associations
2. THE System SHALL maintain the is_primary field to distinguish primary from additional IPs
3. THE System SHALL maintain support for both Managed_IP (ip_address field) and Manual_IP (manual_ip field)
4. WHEN an Asset has a primary IP, THE System SHALL set is_primary to True in AssetIPAddress
5. WHEN an Asset has Additional_IPs, THE System SHALL set is_primary to False in AssetIPAddress for those entries
6. THE System SHALL preserve existing AssetIPAddress records during the migration

### Requirement 4: Add IP Label Field to AssetIPAddress

**User Story:** As a user, I want to label each additional IP with a description, so that I understand what each IP address is used for (e.g., "WiFi", "Mobile", "VPN").

#### Acceptance Criteria

1. THE AssetIPAddress model SHALL include an ip_label field for storing IP descriptions
2. THE ip_label field SHALL accept text strings up to 100 characters
3. THE ip_label field SHALL be optional (null/blank allowed)
4. WHEN an AssetIPAddress has is_primary set to False, THE Asset_Form SHALL require an ip_label value
5. WHEN an AssetIPAddress has is_primary set to True, THE ip_label field SHALL be null or empty
6. THE System SHALL validate that ip_label values do not contain only whitespace

### Requirement 5: Migrate Existing Secondary IPs

**User Story:** As a system maintainer, I want existing secondary IPs to be converted to additional IPs, so that no data is lost during the system upgrade.

#### Acceptance Criteria

1. THE System SHALL provide a database migration for the ip_label field addition
2. THE migration SHALL preserve all existing AssetIPAddress records
3. WHEN an existing AssetIPAddress has is_primary set to False, THE migration SHALL set ip_label to "Secondary IP"
4. WHEN an existing AssetIPAddress has is_primary set to True, THE migration SHALL leave ip_label as null
5. THE migration SHALL complete successfully without data loss

### Requirement 6: Prevent Duplicate IP Assignments

**User Story:** As a system maintainer, I want to prevent duplicate IP addresses on the same asset, so that the system maintains data integrity.

#### Acceptance Criteria

1. WHEN a user attempts to save an Asset, THE System SHALL validate that no IP address appears multiple times on the same Asset
2. IF a duplicate Managed_IP is detected on the same Asset, THEN THE System SHALL display an error message "This IP is already assigned to this asset"
3. IF a duplicate Manual_IP is detected on the same Asset, THEN THE System SHALL display an error message "This IP is already assigned to this asset"
4. THE System SHALL allow the same IP address to be used by different Assets (when using Manual_IP)
5. THE System SHALL prevent assigning the same Managed_IP to multiple Assets

### Requirement 7: Display All IPs in Asset Views

**User Story:** As a user, I want to see all IP addresses assigned to an asset, so that I have complete visibility into the asset's network configuration.

#### Acceptance Criteria

1. WHEN viewing an Asset detail page, THE System SHALL display the primary IP address prominently
2. WHEN an Asset has Additional_IPs, THE System SHALL display them in a list below the primary IP
3. FOR EACH Additional_IP displayed, THE System SHALL show both the IP address and its IP_Label
4. WHEN an Asset has no primary IP, THE System SHALL display "No IP assigned"
5. WHEN an Asset has no Additional_IPs, THE System SHALL not display the Additional_IPs section

### Requirement 8: Support Dynamic IP Entry Form

**User Story:** As a user, I want to dynamically add and remove additional IP fields in the form, so that I can manage multiple IPs without page reloads.

#### Acceptance Criteria

1. THE Asset_Form SHALL provide an "Add Additional IP" button in the Additional_IP section
2. WHEN the "Add Additional IP" button is clicked, THE System SHALL dynamically add a new set of Additional_IP fields (IP_Label, IP_Entry_Mode, IP input)
3. THE System SHALL provide a "Remove" button for each Additional_IP entry
4. WHEN a "Remove" button is clicked, THE System SHALL remove that Additional_IP entry from the form
5. THE System SHALL preserve all Additional_IP entries when form validation fails and the form is redisplayed with errors

### Requirement 9: Maintain IP Pool Management

**User Story:** As a system maintainer, I want managed IP addresses to continue using the existing IP pool system, so that IP allocation remains centralized and conflict-free.

#### Acceptance Criteria

1. WHEN a Managed_IP is selected for Primary_IP or Additional_IP, THE System SHALL mark that IP as assigned in the IP_Pool
2. WHEN an Asset with Managed_IPs is deleted, THE System SHALL mark those IPs as unassigned in the IP_Pool
3. WHEN a Managed_IP is removed from an Asset, THE System SHALL mark that IP as unassigned in the IP_Pool
4. THE System SHALL prevent selecting already-assigned Managed_IPs in the dropdown options
5. THE System SHALL include the currently-assigned Managed_IP in dropdown options when editing an existing Asset

### Requirement 10: Validate IP Entry Mode Consistency

**User Story:** As a system maintainer, I want to ensure each IP entry uses exactly one entry mode, so that data integrity is maintained.

#### Acceptance Criteria

1. THE System SHALL enforce that each AssetIPAddress record has exactly one of ip_address or manual_ip populated
2. IF both ip_address and manual_ip are provided for the same entry, THEN THE System SHALL display an error message "Cannot have both managed and manual IP"
3. IF neither ip_address nor manual_ip is provided for the same entry, THEN THE System SHALL display an error message "Either managed or manual IP must be provided"
4. THE System SHALL enforce this validation at both the form level and model level

### Requirement 11: Update Asset List Display

**User Story:** As a user, I want to see the primary IP address in the asset list view, so that I can quickly identify assets by their IP addresses.

#### Acceptance Criteria

1. WHEN viewing the Asset list page, THE System SHALL display the primary IP address in a dedicated column
2. WHEN an Asset has a Managed_IP as primary, THE System SHALL display the IP address
3. WHEN an Asset has a Manual_IP as primary, THE System SHALL display the IP address
4. WHEN an Asset has no primary IP, THE System SHALL display an empty cell or "—"
5. THE System SHALL not display Additional_IPs in the list view (only in detail view)

### Requirement 12: Preserve IP Assignment History

**User Story:** As a system maintainer, I want IP assignment history to be preserved, so that we can track when IPs were assigned and released.

#### Acceptance Criteria

1. THE AssetIPAddress model SHALL maintain the created_at timestamp field
2. WHEN a new IP is assigned to an Asset, THE System SHALL automatically set created_at to the current timestamp
3. THE System SHALL preserve freed_date in the IPAddress model for tracking when IPs are released
4. WHEN a Managed_IP is removed from an Asset, THE System SHALL update freed_date in the IPAddress model
5. THE System SHALL maintain the existing IP assignment tracking behavior
