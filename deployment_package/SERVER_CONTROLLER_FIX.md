# Server Controller Bug Fix - HyperV VM Relationship

## Issue Fixed
**Error:** `AttributeError: Cannot find 'hyperv_vms' on Asset object`

The Server Controller feature was using an incorrect relationship name to access Hyper-V VMs.

## Root Cause
The `HyperVVM` model defines the relationship with `related_name='hosted_vms'`, but the code was trying to access it as `hyperv_vms`.

**Correct relationship in models/hyperv_vm.py:**
```python
host_machine = models.ForeignKey(
    'Asset',
    on_delete=models.PROTECT,
    related_name='hosted_vms',  # ← This is the correct name
    help_text="Physical machine hosting this VM"
)
```

## Files Fixed

### 1. `assets/views_server_controller.py`
**Changes:**
- Line 24: `.prefetch_related('hyperv_vms')` → `.prefetch_related('hosted_vms')`
- Line 91: `self.object.hyperv_vms.all()` → `self.object.hosted_vms.all()`
- Line 269: `asset.hyperv_vms.all()` → `asset.hosted_vms.all()`
- Line 270-271: Fixed VM attribute names:
  - `vm.vm_name` → `vm.name`
  - `vm.ip_address` → `vm.get_display_ip()`

### 2. `assets/templates/assets/server_controller_list.html`
**Changes:**
- Line 121: `{% with vms=asset.hyperv_vms.all %}` → `{% with vms=asset.hosted_vms.all %}`
- Line 123: Updated tooltip to use correct VM attributes:
  - `vm.vm_name` → `vm.name`
  - `vm.ip_address|default:'No IP'` → `vm.get_display_ip`

### 3. `assets/templates/assets/server_controller_form.html`
**Changes:**
- Line 118: `vm.vm_name` → `vm.name`
- Line 119: `vm.ip_address|default:"—"` → `vm.get_display_ip`
- Line 120: Updated status display to show power status and active state

## Verification
✅ Server reloaded successfully without errors
✅ Page loads with HTTP 302 redirect to login (correct authentication behavior)
✅ No AttributeError in server logs

## Deployment Notes
All fixed files have been updated in the deployment package:
- `/deployment_package/assets/views_server_controller.py`
- `/deployment_package/assets/templates/assets/server_controller_list.html`
- `/deployment_package/assets/templates/assets/server_controller_form.html`

Simply replace these files on the server and restart Django.

## Testing Checklist
After deployment:
1. ✓ Navigate to Server Controllers page (no error)
2. Test free/reassign/scrap workflows
3. Verify SC badge appears in Freed Systems page
4. Test edit form with VMs display
5. Test export functionality
6. Verify dynamic IP filtering (move system in/out of 50.x range)
