# Secondary IP Implementation Summary

## Overview
Updated the AssetForm to allow adding both primary and secondary IP addresses in the same form. This is useful for devices like laptops that have both LAN (primary) and WiFi (secondary) connections.

## Changes Made

### 1. Form Fields (assets/forms/asset_forms.py)

#### New Fields Added:
- `secondary_ip_type`: Radio buttons to select between managed/manual IP type
- `secondary_ip_address`: Dropdown for selecting managed IPs from the pool
- `secondary_manual_ip`: Text input for entering manual IPs

#### Form Initialization (`__init__` method):
- Pre-populates secondary IP fields when editing an asset with existing secondary IP
- Filters secondary IP dropdown to exclude the primary IP (prevents duplication)
- Uses `get_filtered_free_ips()` to show only available IPs from ranges: 192.168.10.x, 192.168.11.x, 192.168.50.x, 192.168.70.x

#### Save Method:
- Handles creation/update of primary IP (existing logic)
- **NEW**: Handles creation/update/deletion of secondary IP
- For managed secondary IPs:
  - Creates AssetIPAddress record with `is_primary=False`
  - Marks IP as assigned in the IP pool
- For manual secondary IPs:
  - Creates AssetIPAddress record with manual IP and `is_primary=False`
- If secondary IP fields are empty, removes existing secondary IP (if any)

### 2. Template (assets/templates/assets/asset_form.html)

#### Primary IP Section:
- Changed label to "Primary IP (LAN)" for clarity
- Existing radio buttons and fields remain unchanged

#### Secondary IP Section (NEW):
- Label: "Secondary IP (WiFi) - Optional"
- Radio buttons to select between managed/manual
- Dropdown for managed IPs (filtered to exclude primary IP)
- Text input for manual IPs
- Help text explaining the optional nature

#### JavaScript Updates:
- Added `handleSecondaryIPTypeChange()` function to toggle secondary IP fields based on radio selection
- Initialization logic to set correct field visibility on page load
- Auto-detection of secondary IP type when editing (managed vs manual)

## Use Case Example

**Scenario**: Laptop user has:
- LAN IP (192.168.10.100) when at desk - saved as **primary IP**
- WiFi IP (192.168.50.200) for meetings - saved as **secondary IP**

Both IPs are now stored and tracked in the system.

## Testing

All tests passed successfully:
- ✓ Form has all required secondary IP fields
- ✓ Form initialization with default values
- ✓ Loading existing asset with secondary IP
- ✓ Saving asset with managed primary and managed secondary IPs
- ✓ Saving asset with managed primary and manual secondary IP
- ✓ Saving asset without secondary IP (optional field)

## Database Schema

Uses existing `AssetIPAddress` junction model:
- `asset` (FK to Asset)
- `ip_address` (FK to IPAddress, nullable)
- `manual_ip` (GenericIPAddressField, nullable)
- `is_primary` (Boolean) - **False for secondary IPs**
- `created_at` (DateTime)

## Notes

- Secondary IP is **optional** - forms can be saved without it
- Primary IP cannot be same as secondary IP (validation in dropdown)
- When updating secondary IP, old IP is properly released if it was managed
- Both managed and manual secondary IPs are supported
- Multiple secondary IPs not currently supported (only first secondary is used)
