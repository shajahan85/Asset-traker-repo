# Server Controller IP Filter Feature

## Overview
Added IP address filtering to the Server Controllers page with intelligent VM detection.

## Feature Description

### IP Filter Input
A new filter field has been added to the Server Controller page that allows filtering by IP address.

**Location:** First field in the filter section

**Functionality:**
1. **Direct Asset Filtering:** Enter an asset's IP address to find that specific server controller
2. **VM IP Detection:** Enter a VM's IP address to automatically show the **host machine** and **all its VMs**

### Smart VM Detection

When you enter an IP that belongs to a Hyper-V VM:
- ✅ The system automatically identifies the host machine
- ✅ Shows the host machine with all its associated VMs
- ✅ Highlights the matched VM in yellow
- ✅ Displays a notice: "🔍 Filtering by VM IP: [IP] ([VM Name])"

### Visual Enhancements

**VM Display in Table:**
- Shows VM count badge
- Lists all VMs with their IP addresses below the badge
- Highlights the filtered VM in yellow background

**Filter Notice:**
When filtering by VM IP, a yellow notice box appears showing:
- The filtered IP address
- The VM name
- Message: "Showing host machine and all associated VMs"

## Usage Examples

### Example 1: Find Server by IP
```
Enter: 192.168.50.15
Result: Shows the server controller with that IP
```

### Example 2: Find Host by VM IP
```
Enter: 192.168.70.100
Result: 
- Identifies that this is a VM IP
- Shows the host machine (e.g., 192.168.50.15)
- Displays all VMs on that host
- Highlights the VM with 192.168.70.100
```

### Example 3: Combined Filters
```
IP Filter: 192.168.50
Team: IT Department
Result: Shows all IT Department server controllers in 50.x range
```

## Implementation Details

### Backend Changes (`views_server_controller.py`)

**Modified Method:** `ServerControllerListView.get_queryset()`

**Logic:**
1. Check if `ip_filter` parameter exists
2. Query `HyperVVM` table for matching IP
3. If VM found: Filter assets by `vm.host_machine.pk`
4. If no VM: Filter assets by IP address directly
5. Apply additional filters (team, branch, search)

**Context Variables Added:**
- `ip_filter` - The entered IP filter value
- `filtered_by_vm` - Boolean indicating VM IP filtering
- `filtered_vm_ip` - The filtered VM IP address
- `filtered_vm_name` - The name of the filtered VM

### Frontend Changes (`server_controller_list.html`)

**New Elements:**
1. IP filter input field (first in filter section)
2. Helper text: "💡 Enter VM IP to see host machine + all VMs"
3. Yellow notice box when filtering by VM IP
4. Enhanced VM display with individual VM listings
5. Yellow highlight for matched VM

**VM Display Enhancement:**
- Badge showing VM count
- Expandable list of VMs with IPs
- Conditional highlighting for filtered VM

## Database Queries

**VM IP Lookup:**
```python
HyperVVM.objects.filter(
    Q(ip_address__address__icontains=ip_filter) |
    Q(manual_ip__icontains=ip_filter)
).first()
```

**Asset Filtering (when VM found):**
```python
Asset.objects.filter(pk=vm_with_ip.host_machine.pk)
```

**Asset Filtering (direct IP):**
```python
Asset.objects.filter(
    Q(asset_ip_addresses__ip_address__address__icontains=ip_filter) |
    Q(manual_ip__icontains=ip_filter)
).distinct()
```

## User Interface

### Filter Section Layout
```
┌─────────────────────────────────────────────────┐
│ IP Address: [192.168.50.10_______________] 💡   │
│ Search: [Asset tag or assigned to...]          │
│ Team: [-- All Teams --]                         │
│ Branch: [-- All Branches --]                    │
│ [Apply Filters] [Clear Filters]                │
└─────────────────────────────────────────────────┘
```

### VM Display in Table
```
┌────────────────────────────────┐
│ 🔵 3 VMs                       │
│ • VM-Web-01: 192.168.70.101   │
│ • VM-DB-01: 192.168.70.102    │
│ • VM-App-01: 192.168.70.103   │  ← Highlighted if filtered
└────────────────────────────────┘
```

## Benefits

1. **Quick Access:** Find any server controller by any IP (host or VM)
2. **Context Awareness:** Automatically shows related systems
3. **Visual Feedback:** Clear indication when filtering by VM IP
4. **Comprehensive View:** See all VMs on a host at once
5. **Flexible Search:** Partial IP matching supported

## Technical Notes

- Works with both tracked IPs (`ip_address` FK) and manual IPs (`manual_ip` field)
- Case-insensitive matching with `icontains`
- Compatible with existing filters (team, branch, search)
- Preserves tab state (active/freed) during filtering
- No database migrations required

## Files Modified

1. `assets/views_server_controller.py` - Backend filtering logic
2. `assets/templates/assets/server_controller_list.html` - UI components

## Testing Checklist

- [ ] Enter server IP - shows correct server
- [ ] Enter VM IP - shows host machine
- [ ] VM IP filter displays notice box
- [ ] Filtered VM is highlighted in yellow
- [ ] All VMs display with correct IPs
- [ ] Partial IP matching works
- [ ] Combine with other filters
- [ ] Clear filters removes IP filter
- [ ] Works on both Active and Freed tabs

## Future Enhancements (Optional)

- Add autocomplete for IP addresses
- Show VM IP ranges in tooltip
- Add "Show all VMs" toggle
- Export filtered results
- Recent IP filter history

---

**Created:** September 9, 2026  
**Feature:** IP Filter with VM Detection  
**Status:** ✅ Implemented and Ready for Deployment
