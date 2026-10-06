# Design: Guest IP Assignment

## Architecture Overview

The Guest IP Assignment feature extends the existing IP management system with a lightweight, temporary assignment mechanism for office guests. The design leverages existing patterns (AJAX modals, IPManagementService) and adds minimal new database structures.

## Design Approach

**Choice: Extend IPAddress model with guest fields vs. Create separate GuestIPAssignment model**

**Selected:** Extend IPAddress model with guest-specific fields

**Rationale:**
- Simpler implementation with fewer joins
- Guest assignments are mutually exclusive with asset/VM/network device assignments
- Easier to query and display in existing IP list views
- Maintains consistency with existing manual_ip pattern
- Lower database query overhead

## Data Model Changes

### IPAddress Model Extensions

Add new fields to `assets/models.py`:

```python
class IPAddress(models.Model):
    # ... existing fields ...
    
    # Guest assignment fields
    guest_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Name of guest assigned this IP temporarily"
    )
    guest_assigned_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this IP was assigned to a guest"
    )
    guest_assigned_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Username of admin who assigned this IP to guest"
    )
    
    def is_guest_assigned(self):
        """Check if this IP is currently assigned to a guest."""
        return bool(self.guest_name)
```

**Migration Notes:**
- All fields are nullable and blank=True for backward compatibility
- Existing IPs will have NULL values for guest fields
- No data migration required

## Service Layer Design

### IPManagementService Extensions

Add methods to `assets/services/ip_management_service.py`:

```python
@staticmethod
def assign_ip_to_guest(ip_address, guest_name, admin_user):
    """
    Assign IP address to a guest temporarily.
    
    Args:
        ip_address: IPAddress instance to assign
        guest_name: str, name of the guest
        admin_user: User instance of admin making assignment
        
    Raises:
        ValidationError: If IP is already assigned
    """
    from django.utils import timezone
    from django.core.exceptions import ValidationError
    
    with transaction.atomic():
        # Refresh from DB to ensure latest state
        ip_address.refresh_from_db()
        
        # Validate IP is actually free
        if ip_address.is_assigned or ip_address.guest_name:
            raise ValidationError("This IP address is already assigned.")
        
        # Check for manual IP conflicts
        if IPManagementService._is_ip_manually_used(ip_address.address):
            raise ValidationError("This IP address is in use as a manual IP.")
        
        # Assign to guest
        ip_address.is_assigned = True
        ip_address.guest_name = guest_name.strip()
        ip_address.guest_assigned_date = timezone.now()
        ip_address.guest_assigned_by = admin_user.username
        ip_address.save()

@staticmethod
def release_guest_ip(ip_address, admin_user):
    """
    Release IP address from guest assignment.
    
    Args:
        ip_address: IPAddress instance to release
        admin_user: User instance of admin releasing IP
        
    Raises:
        ValidationError: If IP is not guest-assigned
    """
    from django.utils import timezone
    from django.core.exceptions import ValidationError
    
    with transaction.atomic():
        # Refresh from DB to ensure latest state
        ip_address.refresh_from_db()
        
        # Validate this is a guest assignment
        if not ip_address.guest_name:
            raise ValidationError("This IP is not assigned to a guest.")
        
        # Release the IP
        ip_address.is_assigned = False
        ip_address.guest_name = None
        ip_address.guest_assigned_date = None
        ip_address.guest_assigned_by = None
        ip_address.freed_date = timezone.now()
        ip_address.save()

@staticmethod
def _is_ip_manually_used(ip_address_str):
    """Check if an IP is used as manual IP by any entity."""
    from assets.models import Asset, NetworkDevice, HyperVVM
    
    # Check assets
    if Asset.objects.filter(manual_ip=ip_address_str, status='active').exists():
        return True
    
    # Check network devices
    if NetworkDevice.objects.filter(manual_ip=ip_address_str).exists():
        return True
    
    # Check VMs
    if HyperVVM.objects.filter(manual_ip=ip_address_str, is_active=True).exists():
        return True
    
    return False
```

## View Layer Design

### New Views

Add to `assets/views.py`:

```python
class GuestIPAssignView(AdminRequiredMixin, View):
    """Handle AJAX request to assign IP to guest."""
    
    def post(self, request):
        """Process guest IP assignment."""
        try:
            ip_id = request.POST.get('ip_id')
            guest_name = request.POST.get('guest_name', '').strip()
            
            # Validate inputs
            if not ip_id or not guest_name:
                return JsonResponse({
                    'success': False,
                    'error': 'IP ID and guest name are required.'
                }, status=400)
            
            # Get IP address
            ip_address = IPAddress.objects.get(id=ip_id)
            
            # Assign to guest using service
            IPManagementService.assign_ip_to_guest(
                ip_address,
                guest_name,
                request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'IP {ip_address.address} assigned to {guest_name}',
                'ip_address': ip_address.address,
                'guest_name': guest_name
            })
            
        except IPAddress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'IP address not found.'
            }, status=404)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error assigning IP: {str(e)}'
            }, status=500)


class GuestIPReleaseView(AdminRequiredMixin, View):
    """Handle AJAX request to release guest IP."""
    
    def post(self, request):
        """Process guest IP release."""
        try:
            ip_id = request.POST.get('ip_id')
            
            # Validate input
            if not ip_id:
                return JsonResponse({
                    'success': False,
                    'error': 'IP ID is required.'
                }, status=400)
            
            # Get IP address
            ip_address = IPAddress.objects.get(id=ip_id)
            
            # Store guest name for response
            guest_name = ip_address.guest_name
            
            # Release using service
            IPManagementService.release_guest_ip(
                ip_address,
                request.user
            )
            
            return JsonResponse({
                'success': True,
                'message': f'IP {ip_address.address} released from {guest_name}',
                'ip_address': ip_address.address
            })
            
        except IPAddress.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'IP address not found.'
            }, status=404)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error releasing IP: {str(e)}'
            }, status=500)
```

### URL Routes

Add to `assets/urls.py`:

```python
path('guest-ip/assign/', views.GuestIPAssignView.as_view(), name='guest_ip_assign'),
path('guest-ip/release/', views.GuestIPReleaseView.as_view(), name='guest_ip_release'),
```

## Template Changes

### Free IPs Page Updates

Modify `assets/templates/assets/free_ips.html`:

1. **Update IP item rendering** to show guest indicator:

```html
<div class="ip-item {% if ip.occupant_type == 'guest' %}guest{% elif ip.occupant_type == 'vm' %}vm{% elif ip.occupant_type == 'free' %}free{% else %}occupied{% endif %}"
     data-ip-id="{{ ip.id }}"
     data-occupant-type="{{ ip.occupant_type }}"
     data-guest-name="{{ ip.guest_name|default:'' }}">
    {{ ip.address }}
    {% if ip.occupant_type == 'guest' %}
        <small class="guest-indicator">👤 Guest: {{ ip.guest_name }}</small>
        <button class="release-guest-btn" data-ip-id="{{ ip.id }}" data-ip-address="{{ ip.address }}" data-guest-name="{{ ip.guest_name }}">Release</button>
    {% elif ip.occupant_type == 'free' %}
        <button class="assign-guest-btn" data-ip-id="{{ ip.id }}" data-ip-address="{{ ip.address }}">Assign to Guest</button>
    {% elif ... %}
        <!-- existing VM/asset/network device display -->
    {% endif %}
</div>
```

2. **Add guest IP styling**:

```css
.ip-item.guest {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
    color: #856404;
}

.guest-indicator {
    display: block;
    font-size: 0.75rem;
    color: #856404;
    margin-top: 2px;
}

.assign-guest-btn,
.release-guest-btn {
    display: block;
    margin-top: 5px;
    padding: 4px 8px;
    font-size: 0.75rem;
    border: none;
    border-radius: 3px;
    cursor: pointer;
    transition: all 0.2s;
}

.assign-guest-btn {
    background-color: #28a745;
    color: white;
}

.assign-guest-btn:hover {
    background-color: #218838;
}

.release-guest-btn {
    background-color: #ffc107;
    color: #856404;
}

.release-guest-btn:hover {
    background-color: #e0a800;
}

.legend-box.guest {
    background-color: #fff3cd;
    border: 1px solid #ffc107;
}
```

3. **Add guest assignment modal**:

```html
<div id="guestAssignmentModal" class="modal-overlay">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">Assign IP to Guest</h3>
                <button type="button" class="modal-close">&times;</button>
            </div>
            <div class="modal-body">
                <p>Assign IP <strong id="assignIPAddress"></strong> to:</p>
                <form id="guestAssignmentForm">
                    {% csrf_token %}
                    <input type="hidden" id="assignIPId" name="ip_id">
                    <div class="form-group">
                        <label for="guestName">Guest Name <span class="required">*</span></label>
                        <input type="text" class="form-control" id="guestName" name="guest_name" required maxlength="150" placeholder="Enter guest's name">
                    </div>
                    <div id="assignFormErrors" class="alert-error"></div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary btn-cancel">Cancel</button>
                <button type="button" id="confirmAssignButton" class="btn btn-primary">Assign</button>
            </div>
        </div>
    </div>
</div>
```

### JavaScript Implementation

Add `assets/static/assets/js/guest_ip_assignment.js`:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('guestAssignmentModal');
    const assignButtons = document.querySelectorAll('.assign-guest-btn');
    const releaseButtons = document.querySelectorAll('.release-guest-btn');
    const closeButtons = modal.querySelectorAll('.modal-close, .btn-cancel');
    const confirmButton = document.getElementById('confirmAssignButton');
    const guestNameInput = document.getElementById('guestName');
    
    // Open assignment modal
    assignButtons.forEach(button => {
        button.addEventListener('click', function() {
            const ipId = this.dataset.ipId;
            const ipAddress = this.dataset.ipAddress;
            
            document.getElementById('assignIPId').value = ipId;
            document.getElementById('assignIPAddress').textContent = ipAddress;
            guestNameInput.value = '';
            document.getElementById('assignFormErrors').textContent = '';
            
            modal.style.display = 'flex';
            guestNameInput.focus();
        });
    });
    
    // Close modal
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            modal.style.display = 'none';
        });
    });
    
    // Confirm assignment
    confirmButton.addEventListener('click', function() {
        const ipId = document.getElementById('assignIPId').value;
        const guestName = guestNameInput.value.trim();
        
        if (!guestName) {
            document.getElementById('assignFormErrors').textContent = 'Guest name is required';
            return;
        }
        
        // Disable button during request
        confirmButton.disabled = true;
        
        // Send AJAX request
        fetch('/guest-ip/assign/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: new URLSearchParams({
                ip_id: ipId,
                guest_name: guestName
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to show updated IP status
                window.location.reload();
            } else {
                document.getElementById('assignFormErrors').textContent = data.error;
                confirmButton.disabled = false;
            }
        })
        .catch(error => {
            document.getElementById('assignFormErrors').textContent = 'Network error occurred';
            confirmButton.disabled = false;
        });
    });
    
    // Handle release buttons
    releaseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const ipId = this.dataset.ipId;
            const ipAddress = this.dataset.ipAddress;
            const guestName = this.dataset.guestName;
            
            if (!confirm(`Release IP ${ipAddress} from guest ${guestName}?`)) {
                return;
            }
            
            // Send AJAX request
            fetch('/guest-ip/release/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: new URLSearchParams({
                    ip_id: ipId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Reload page to show updated IP status
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                }
            })
            .catch(error => {
                alert('Network error occurred');
            });
        });
    });
});
```

## View Context Updates

Update `FreeIPsView.get_context_data()` in `assets/views.py`:

```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    
    ip_ranges = self.get_queryset()
    
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            ip = ip_data['ip']
            
            # Check for guest assignment first
            if ip.guest_name:
                ip.occupant_type = 'guest'
                ip.occupant_name = ip.guest_name
            # ... existing VM/network device/asset checks ...
    
    context['ip_ranges'] = ip_ranges
    return context
```

## Database Migration

Create migration file:

```bash
python manage.py makemigrations assets --name add_guest_ip_fields
```

Expected migration operations:
- Add `guest_name` CharField (nullable, blank, max_length=150)
- Add `guest_assigned_date` DateTimeField (nullable, blank)
- Add `guest_assigned_by` CharField (nullable, blank, max_length=150)

## Search Integration

Update existing IP search in `free_ips.html` JavaScript to include guest names:

```javascript
const occupantName = item.getAttribute('data-occupant-name') || '';
const guestName = item.getAttribute('data-guest-name') || '';

if (ipAddress.includes(searchTerm) || 
    title.includes(searchTerm) || 
    occupantName.includes(searchTerm) ||
    guestName.includes(searchTerm)) {
    // Show IP
}
```

## Testing Strategy

### Unit Tests

Test `IPManagementService` methods:
1. `assign_ip_to_guest()` - success case
2. `assign_ip_to_guest()` - already assigned error
3. `assign_ip_to_guest()` - manual IP conflict error
4. `release_guest_ip()` - success case
5. `release_guest_ip()` - not guest-assigned error

### Integration Tests

Test views:
1. GuestIPAssignView - valid POST
2. GuestIPAssignView - invalid IP ID
3. GuestIPAssignView - missing guest name
4. GuestIPReleaseView - valid POST
5. GuestIPReleaseView - invalid IP ID

### Manual Testing Checklist

1. Assign free IP to guest - verify occupied status
2. Release guest IP - verify free status
3. Search by guest name - verify results
4. Concurrent assignment attempts - verify handling
5. Refresh page after assignment - verify persistence
6. Visual styling - verify guest IPs distinct from other types

## Deployment Plan

1. Apply database migration
2. Deploy code changes (models, services, views, templates, static files)
3. Restart Django application
4. Verify no regressions in existing IP management
5. Test guest assignment workflow
6. Monitor for errors

## Rollback Plan

If issues occur:
1. Revert code changes
2. Migration is safe to leave (nullable fields don't break existing functionality)
3. Or rollback migration if needed: `python manage.py migrate assets <previous_migration>`

## Performance Considerations

- Guest assignment queries are single-row updates (fast)
- No N+1 query issues (guest fields on same model)
- Minimal impact on IP list page load (2-3 extra fields per IP)
- AJAX operations prevent full page reloads

## Security Considerations

- Admin-only access enforced via `AdminRequiredMixin`
- CSRF protection on all POST requests
- Input validation (guest name max length, required fields)
- Database transaction safety prevents race conditions
- SQL injection prevented by ORM

## Future Enhancements (Out of Scope)

- Guest IP assignment history table (separate audit log)
- Automatic expiration after X hours
- Email notifications
- Guest IP usage reports
- Bulk guest assignment
- Guest self-service portal
