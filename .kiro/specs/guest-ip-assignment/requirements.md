# Requirements: Guest IP Assignment

## Overview
Enable temporary IP address assignment to office guests with a simple workflow for assignment and release. Guest-assigned IPs should appear as occupied in the IP management system and automatically return to free status when released.

## User Stories

### US-1: Assign IP to Guest
**As an** admin user  
**I want to** quickly assign a free IP address to an office guest with their name  
**So that** I can track which IPs are temporarily assigned to visitors

**Acceptance Criteria:**
- Admin can select any free IP address from the Free IPs page
- System prompts for guest name (required field)
- Upon assignment, IP immediately shows as "occupied" (not "free") on the Free IPs page
- Guest name displays next to the assigned IP address
- Assignment is tracked in the IPAddress model
- No page reload required (AJAX-based interaction)

### US-2: Release Guest IP
**As an** admin user  
**I want to** release an IP address when a guest leaves  
**So that** the IP returns to the free pool for reuse

**Acceptance Criteria:**
- Admin can click a "Release" button next to guest-assigned IPs
- System confirms the release action
- Upon release, IP immediately shows as "free" on the Free IPs page
- Guest assignment record is cleared from the IP
- Freed date is updated on the IP address
- No page reload required (AJAX-based interaction)

### US-3: Visual Distinction for Guest IPs
**As an** admin user  
**I want to** easily identify which IPs are assigned to guests  
**So that** I can distinguish them from asset-assigned IPs and VMs

**Acceptance Criteria:**
- Guest-assigned IPs have a distinct visual indicator (e.g., icon or label)
- Guest name is prominently displayed next to the IP
- Guest IPs use the same "occupied" styling but with additional guest identifier
- Hovering over guest IP shows tooltip with guest name and assignment date

### US-4: Guest Assignment History
**As an** admin user  
**I want to** see when a guest IP was assigned and by whom  
**So that** I can track temporary IP usage for auditing purposes

**Acceptance Criteria:**
- System records assignment timestamp
- System records which admin user made the assignment
- Assignment information is available when viewing IP details
- Guest assignment data is preserved even after release (for audit trail)

## Functional Requirements

### FR-1: Guest IP Assignment Model
- Extend IPAddress model or create GuestIPAssignment model to track:
  - Guest name (required, max 150 characters)
  - Assignment date/time (auto-populated)
  - Assigned by user (admin username)
  - Release date/time (nullable, set when released)
  - Released by user (nullable, admin username who released)

### FR-2: Assignment Workflow
- Only free IPs can be assigned to guests
- Assignment marks IP as occupied (is_assigned=True or equivalent flag)
- Guest name field supports international characters
- Assignment is immediate (no multi-step form)

### FR-3: Release Workflow
- Only guest-assigned IPs can be released via this workflow
- Release immediately frees the IP (is_assigned=False)
- Release updates freed_date timestamp
- Release clears guest assignment but preserves history record

### FR-4: IP List Page Integration
- Add "Assign to Guest" button/action for free IPs
- Add "Release Guest" button/action for guest-assigned IPs
- Display guest name with guest-assigned IPs
- Use existing AJAX patterns from VM creation modal
- No full page reload required

### FR-5: Search and Filter Support
- Existing IP search should find guest-assigned IPs by guest name
- Guest-assigned IPs appear in search results with guest identifier

## Non-Functional Requirements

### NFR-1: Performance
- Assignment and release operations complete within 1 second
- No impact on existing IP list page load time
- AJAX operations use efficient database queries

### NFR-2: Usability
- Guest assignment requires minimal clicks (2-3 max)
- UI is intuitive and consistent with existing patterns
- Clear visual feedback for assignment/release success

### NFR-3: Security
- Only admin users can assign/release guest IPs
- Guest assignment validates IP is actually free before assignment
- Concurrent assignment attempts are handled safely (database-level constraints)

### NFR-4: Data Integrity
- Guest assignments don't conflict with existing IP assignments
- Database constraints prevent duplicate assignments
- Transaction-safe operations prevent data inconsistencies

## Business Rules

### BR-1: Assignment Restrictions
- Only IPs with is_assigned=False can be assigned to guests
- One IP can only be assigned to one guest at a time
- Guest name is required (cannot be empty)

### BR-2: Release Restrictions
- Only guest-assigned IPs can be released via guest release workflow
- Release action is immediate and cannot be undone
- Released IPs return to general free IP pool

### BR-3: Display Logic
- Free IPs show green background with "Free" label
- Guest-assigned IPs show as occupied (red/occupied background) with "Guest: [name]" label
- Asset/VM/Network Device assigned IPs remain unchanged

## Dependencies

- Existing IPAddress model
- Existing IPManagementService
- Existing Free IPs page template and views
- Django admin authentication system
- Existing AJAX modal patterns (from VM creation feature)

## Out of Scope

- Scheduled/time-based automatic release of guest IPs
- Guest self-service IP assignment
- Email notifications for guest IP assignment
- Integration with guest management system
- Bulk guest IP assignment
- Guest IP assignment reports/analytics

## Success Criteria

1. Admins can assign free IPs to guests in under 5 seconds
2. Guest-assigned IPs immediately show as occupied on IP list page
3. Released guest IPs immediately show as free on IP list page
4. Guest names are searchable in IP search
5. No regressions in existing IP management functionality
6. Zero downtime deployment
