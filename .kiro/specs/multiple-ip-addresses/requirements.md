# Requirements Document

## Introduction

This document defines requirements for supporting multiple IP addresses per system in the Asset Tracker application. Currently, each asset can have only one IP address (either a managed IP from the IPAddress pool or a manually entered IP). This feature enables assets to have multiple IP addresses to support scenarios where users switch between different network connections (e.g., LAN and WiFi).

## Glossary

- **Asset_Tracker**: The Asset Tracker application system
- **Asset**: A system (Desktop, Laptop, or All-in-One PC) tracked in the application
- **IP_Manager**: The IP address management subsystem
- **Primary_IP**: The main IP address assigned to an asset
- **Secondary_IP**: Any additional IP address assigned to an asset beyond the primary
- **Managed_IP**: An IP address from the IPAddress pool that is tracked and managed by IP_Manager
- **Manual_IP**: An IP address entered manually that is not tracked in IP_Manager
- **IP_Pool**: The collection of IPAddress records available for assignment
- **Asset_Form**: The user interface form for creating and editing assets
- **Reassignment_Form**: The user interface form for reassigning freed systems

## Requirements

### Requirement 1: Multiple IP Address Assignment

**User Story:** As an IT administrator, I want to assign multiple IP addresses to a single asset, so that I can track systems that switch between different network connections.

#### Acceptance Criteria

1. THE Asset_Tracker SHALL support assigning multiple IP addresses to a single Asset
2. WHEN a Primary_IP is assigned, THE Asset_Tracker SHALL mark the IP as occupied in IP_Pool
3. WHEN a Secondary_IP is assigned, THE Asset_Tracker SHALL mark the IP as occupied in IP_Pool
4. THE Asset_Tracker SHALL maintain at most one Primary_IP per Asset
5. THE Asset_Tracker SHALL support zero or more Secondary_IP addresses per Asset
6. FOR ALL managed IP addresses assigned to an Asset, THE IP_Manager SHALL set is_assigned to True
7. WHEN an IP address is removed from an Asset, THE IP_Manager SHALL set is_assigned to False

### Requirement 2: Add Secondary IP Interface

**User Story:** As an IT administrator, I want to add a second IP address to an existing asset, so that I can track both LAN and WiFi addresses for users who switch networks.

#### Acceptance Criteria

1. WHEN viewing an Asset, THE Asset_Form SHALL display an option to add a Secondary_IP
2. WHEN adding a Secondary_IP, THE Asset_Form SHALL present available IP addresses from IP_Pool
3. WHEN adding a Secondary_IP, THE Asset_Form SHALL filter available IPs to ranges 192.168.10.x, 192.168.11.x, 192.168.50.x, and 192.168.70.x
4. WHEN adding a Secondary_IP, THE Asset_Form SHALL display only unassigned IP addresses
5. WHEN a Secondary_IP is selected, THE Asset_Tracker SHALL save the association to the Asset
6. WHEN a Secondary_IP is added, THE IP_Manager SHALL mark the IP as assigned
7. THE Asset_Form SHALL support adding multiple Secondary_IP addresses sequentially

### Requirement 3: IP Address Display and Management

**User Story:** As an IT administrator, I want to view all IP addresses assigned to an asset, so that I can understand the complete network configuration.

#### Acceptance Criteria

1. WHEN displaying an Asset, THE Asset_Tracker SHALL show the Primary_IP prominently
2. WHEN displaying an Asset with Secondary_IP addresses, THE Asset_Tracker SHALL list all Secondary_IP addresses
3. WHEN displaying IP addresses, THE Asset_Tracker SHALL clearly distinguish between Primary_IP and Secondary_IP
4. WHEN displaying IP addresses, THE Asset_Tracker SHALL show whether each IP is a Managed_IP or Manual_IP
5. THE Asset_Tracker SHALL provide a mechanism to remove a Secondary_IP from an Asset
6. WHEN a Secondary_IP is removed, THE IP_Manager SHALL mark the IP as unassigned
7. THE Asset_Tracker SHALL NOT allow removing the Primary_IP if Secondary_IP addresses exist without reassigning a Secondary_IP as the new Primary_IP

### Requirement 4: Manual IP Support for Secondary Addresses

**User Story:** As an IT administrator, I want to add manual IP addresses as secondary IPs, so that I can track IP addresses outside the managed IP ranges.

#### Acceptance Criteria

1. WHEN adding a Secondary_IP, THE Asset_Form SHALL provide an option to enter a Manual_IP
2. WHEN a Manual_IP is entered as Secondary_IP, THE Asset_Tracker SHALL validate the IP address format
3. THE Asset_Tracker SHALL accept IPv4 addresses in the format XXX.XXX.XXX.XXX for Manual_IP
4. WHEN a Manual_IP is saved as Secondary_IP, THE IP_Manager SHALL NOT mark any Managed_IP as assigned
5. THE Asset_Tracker SHALL store Manual_IP addresses separately from Managed_IP addresses
6. THE Asset_Tracker SHALL support mixing Managed_IP and Manual_IP as Secondary_IP addresses for a single Asset

### Requirement 5: IP Conflict Prevention

**User Story:** As an IT administrator, I want the system to prevent IP address conflicts, so that no two assets have the same managed IP address assigned simultaneously.

#### Acceptance Criteria

1. WHEN assigning a Managed_IP as Primary_IP or Secondary_IP, THE IP_Manager SHALL verify the IP is not already assigned
2. IF a Managed_IP is already assigned to another Asset, THEN THE Asset_Tracker SHALL reject the assignment and display an error message
3. THE Asset_Tracker SHALL allow the same Managed_IP to be assigned to multiple assets IF the IP is first unassigned from previous assets
4. WHEN assigning a Manual_IP, THE Asset_Tracker SHALL NOT perform conflict checking against IP_Pool
5. WHEN assigning a Manual_IP, THE Asset_Tracker SHALL allow duplicate Manual_IP addresses across different Assets

### Requirement 6: Freed System Reassignment with Multiple IPs

**User Story:** As an IT administrator, I want to reassign freed systems with their IP addresses intact, so that I can maintain IP address continuity when reassigning systems.

#### Acceptance Criteria

1. WHEN a system with multiple IP addresses is freed, THE Asset_Tracker SHALL preserve all IP address associations
2. WHEN reassigning a freed system, THE Reassignment_Form SHALL display all currently assigned IP addresses
3. WHEN reassigning a freed system, THE Reassignment_Form SHALL allow adding additional Secondary_IP addresses
4. WHEN reassigning a freed system, THE Reassignment_Form SHALL allow removing Secondary_IP addresses
5. WHEN reassigning a freed system, THE Reassignment_Form SHALL allow changing the Primary_IP
6. WHEN a freed system is scrapped, THE IP_Manager SHALL mark all associated Managed_IP addresses as unassigned

### Requirement 7: Data Migration from Single IP to Multiple IPs

**User Story:** As a system maintainer, I want existing single IP addresses to be automatically migrated to the new multiple IP structure, so that no data is lost during the upgrade.

#### Acceptance Criteria

1. WHEN the multiple IP feature is deployed, THE Asset_Tracker SHALL preserve all existing Primary_IP assignments
2. WHEN the multiple IP feature is deployed, THE Asset_Tracker SHALL preserve all existing Manual_IP values
3. THE Asset_Tracker SHALL treat existing ip_address foreign key values as Primary_IP
4. THE Asset_Tracker SHALL treat existing manual_ip field values as Primary_IP Manual_IP
5. WHEN the migration completes, THE Asset_Tracker SHALL maintain all existing is_assigned states in IP_Pool

### Requirement 8: IP Address Validation and Business Rules

**User Story:** As an IT administrator, I want the system to enforce IP address business rules, so that data remains consistent and valid.

#### Acceptance Criteria

1. THE Asset_Tracker SHALL require at least one IP address (Primary_IP) for each Asset
2. THE Asset_Tracker SHALL prevent assigning the same Managed_IP as both Primary_IP and Secondary_IP on the same Asset
3. IF an Asset has both ip_address and manual_ip, THEN THE Asset_Tracker SHALL treat ip_address as Primary_IP
4. WHEN adding a Secondary_IP, THE Asset_Form SHALL validate that the IP is not already assigned to the same Asset
5. THE Asset_Tracker SHALL support assets with zero Secondary_IP addresses
6. THE Asset_Tracker SHALL support assets with multiple Secondary_IP addresses (no hard limit)
