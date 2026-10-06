# Technical Design Document: Simplified IP Management

## Overview

This feature redesigns the IP address entry system in Django Asset Tracker to provide a more intuitive user experience. The current implementation uses confusing labels ("Primary IP (LAN)" and "Secondary IP (WiFi)") that restrict users to only two IP addresses. The new design introduces a cleaner "IP Address" label for the primary IP and supports multiple additional IP addresses with user-defined labels (e.g., "WiFi IP", "Mobile IP", "VPN IP").

### Key Design Decisions

1. **Minimal Data Model Changes**: Add only the `ip_label` field to the existing `AssetIPAddress` model to maintain backward compatibility
2. **Django Formsets**: Use `inlineformset_factory` to handle dynamic additional IP entries instead of custom JavaScript-heavy solutions
3. **Progressive Enhancement**: JavaScript enhances the UX but the form remains functional without it
4. **Preserve Existing IP Pool Logic**: Maintain the current managed IP allocation system without modification

### Architecture

The implementation follows Django's standard patterns for handling related model instances:

```
Asset (1) ----< (N) AssetIPAddress >---- (1) IPAddress
                      |
                      +-- ip_label (NEW)
                      +-- is_primary
                      +-- manual_ip
```

The form architecture uses:
- **Main Form**: `AssetForm` for Asset model fields and primary IP
- **Inline Formset**: `AdditionalIPFormSet` for additional IP addresses
- **JavaScript Enhancement**: Dynamic add/remove buttons with form cloning

## Architecture

### Component Overview


```
┌─────────────────────────────────────────────────────┐
│              Asset Create/Edit View                 │
│  (assets/views/asset_create_view.py)                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              AssetForm + Formset                    │
│  (assets/forms/asset_forms.py)                      │
│                                                      │
│  • AssetForm (main asset fields + primary IP)       │
│  • AdditionalIPFormSet (inline formset)             │
│    └─ AdditionalIPForm (per additional IP)          │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Template Layer                         │
│  (assets/templates/assets/asset_form.html)          │
│                                                      │
│  • Primary IP section                               │
│  • Additional IPs section (formset rendering)       │
│  • JavaScript for dynamic add/remove                │
└────────────────┬────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────┐
│              Data Models                            │
│  (assets/models/)                                   │
│                                                      │
│  • Asset                                            │
│  • AssetIPAddress (with new ip_label field)         │
│  • IPAddress                                        │
└─────────────────────────────────────────────────────┘
```

### Data Flow

**Creating an Asset with IPs:**
1. User submits form with primary IP and N additional IPs
2. View validates `AssetForm` and `AdditionalIPFormSet`
3. Save Asset instance
4. Create `AssetIPAddress` for primary IP (is_primary=True, ip_label=null)
5. Formset creates `AssetIPAddress` instances for additional IPs (is_primary=False, with ip_label)
6. Update IP pool: mark managed IPs as assigned

**Editing an Asset:**
1. View loads Asset and queries related `AssetIPAddress` records
2. Primary IP populates `AssetForm` fields
3. Additional IPs populate formset initial data
4. Form submission follows same validation and save flow
5. Formset handles updates, deletions, and new entries automatically

## Components and Interfaces

### 1. Database Migration


**File**: `assets/migrations/XXXX_add_ip_label.py`

```python
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('assets', 'XXXX_previous_migration'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='assetipaddress',
            name='ip_label',
            field=models.CharField(
                max_length=100,
                blank=True,
                null=True,
                help_text="Description label for this IP address (e.g., 'WiFi', 'Mobile')"
            ),
        ),
    ]
```

**Data Migration for Existing Records:**

```python
# File: assets/migrations/XXXX_populate_ip_labels.py
from django.db import migrations

def populate_ip_labels(apps, schema_editor):
    """Set default ip_label for existing secondary IPs."""
    AssetIPAddress = apps.get_model('assets', 'AssetIPAddress')
    
    # Set label "Secondary IP" for all existing secondary (non-primary) IPs
    AssetIPAddress.objects.filter(
        is_primary=False,
        ip_label__isnull=True
    ).update(ip_label="Secondary IP")

def reverse_populate_ip_labels(apps, schema_editor):
    """Reverse operation - clear ip_label."""
    AssetIPAddress = apps.get_model('assets', 'AssetIPAddress')
    AssetIPAddress.objects.filter(is_primary=False).update(ip_label=None)

class Migration(migrations.Migration):
    dependencies = [
        ('assets', 'XXXX_add_ip_label'),
    ]
    
    operations = [
        migrations.RunPython(
            populate_ip_labels,
            reverse_code=reverse_populate_ip_labels
        ),
    ]
```

**Migration Strategy:**
- Migration is non-destructive: adds nullable field
- Existing data remains intact
- Data migration sets sensible default ("Secondary IP") for existing non-primary IPs
- Primary IPs retain null ip_label
- Rollback supported via reverse migration

### 2. Model Updates


**File**: `assets/models/asset_ip_address.py`

**Changes to `AssetIPAddress` model:**

```python
class AssetIPAddress(models.Model):
    """Junction model for many-to-many relationship between Assets and IP addresses."""
    
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='asset_ip_addresses',
        db_index=True
    )
    ip_address = models.ForeignKey(
        'IPAddress',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='asset_ip_associations',
        help_text="Managed IP from IP pool (mutually exclusive with manual_ip)"
    )
    manual_ip = models.GenericIPAddressField(
        protocol='IPv4',
        null=True,
        blank=True,
        validators=[validate_ipv4_address],
        help_text="Manually entered IP (mutually exclusive with ip_address)"
    )
    is_primary = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True if this is the primary IP for the asset"
    )
    ip_label = models.CharField(  # NEW FIELD
        max_length=100,
        blank=True,
        null=True,
        help_text="Description label for this IP address (e.g., 'WiFi', 'Mobile')"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    # ... existing Meta, __str__, clean(), get_ip_display() methods remain unchanged
```

**Validation Rules (added to `clean()` method):**

```python
def clean(self):
    """Validate AssetIPAddress business rules."""
    super().clean()
    
    # Existing validation...
    
    # NEW: Validate ip_label for non-primary IPs
    if not self.is_primary and not self.ip_label:
        raise ValidationError({
            'ip_label': 'Label is required for additional IP addresses.'
        })
    
    # NEW: Validate ip_label doesn't contain only whitespace
    if self.ip_label and not self.ip_label.strip():
        raise ValidationError({
            'ip_label': 'Label cannot contain only whitespace.'
        })
    
    # NEW: Primary IPs should not have labels
    if self.is_primary and self.ip_label:
        raise ValidationError({
            'ip_label': 'Primary IP should not have a label.'
        })
```

**No changes required to `Asset` model** - existing helper methods (`get_primary_ip()`, `get_secondary_ips()`) continue to work.

### 3. Form Layer


**File**: `assets/forms/asset_forms.py`

#### 3.1 AssetForm Updates

**Primary IP Section Changes:**

```python
class AssetForm(forms.ModelForm):
    """Form for creating and updating assets."""
    
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP (from IP pool)'),
        ('manual', 'Manual IP (enter manually)'),
    ]
    
    # RENAMED: primary_ip_type (was primary_ip_type)
    primary_ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='IP Address',  # CHANGED: was 'Primary IP'
        initial='managed',
        required=False
    )
    
    # REMOVED: secondary_ip_type, secondary_ip_address, secondary_manual_ip
    # These are now handled by the formset
```

**Label Changes:**

```python
labels = {
    'ip_address': 'IP Address (Managed)',  # CHANGED: was 'Primary IP (Managed)'
    'manual_ip': 'IP Address (Manual)',    # CHANGED: was 'Primary IP (Manual)'
    # ... other labels remain unchanged
}
```

**Save Method Updates:**

The `save()` method will be simplified - it will only handle the primary IP. Additional IPs are handled by the formset.

```python
def save(self, commit=True):
    """Save asset and primary IP association."""
    from django.db import transaction
    from assets.models import AssetIPAddress
    
    asset = super().save(commit=commit)
    
    if commit:
        with transaction.atomic():
            # Handle primary IP only
            primary_ip_type = self.cleaned_data.get('primary_ip_type')
            old_primary = asset.get_primary_ip()
            
            if primary_ip_type == 'managed':
                ip_address = self.cleaned_data.get('ip_address')
                if ip_address:
                    # Release old managed IP if changing
                    if old_primary and old_primary.ip_address != ip_address:
                        if old_primary.ip_address:
                            old_primary.ip_address.is_assigned = False
                            old_primary.ip_address.assigned_to_asset = None
                            old_primary.ip_address.save()
                        old_primary.delete()
                        old_primary = None
                    
                    # Create new primary if needed
                    if not old_primary:
                        AssetIPAddress.objects.create(
                            asset=asset,
                            ip_address=ip_address,
                            manual_ip=None,
                            is_primary=True,
                            ip_label=None
                        )
                    
                    # Mark as assigned
                    ip_address.is_assigned = True
                    ip_address.assigned_to_asset = asset
                    ip_address.save()
            
            elif primary_ip_type == 'manual':
                manual_ip = self.cleaned_data.get('manual_ip')
                if manual_ip:
                    # Similar logic for manual IP
                    # ... (implementation similar to managed IP)
    
    return asset
```

#### 3.2 Additional IP Formset


**New Component: Additional IP Form**

```python
class AdditionalIPForm(forms.ModelForm):
    """Form for a single additional IP address."""
    
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP'),
        ('manual', 'Manual IP'),
    ]
    
    ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input ip-type-radio'}),
        initial='managed',
        required=True
    )
    
    class Meta:
        model = AssetIPAddress
        fields = ['ip_label', 'ip_address', 'manual_ip']
        widgets = {
            'ip_label': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., WiFi, Mobile, VPN'
            }),
            'ip_address': forms.Select(attrs={
                'class': 'form-control ip-managed-select'
            }),
            'manual_ip': forms.TextInput(attrs={
                'class': 'form-control ip-manual-input',
                'placeholder': 'e.g., 192.168.1.100'
            }),
        }
        labels = {
            'ip_label': 'Label',
            'ip_address': 'IP Address',
            'manual_ip': 'IP Address',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate managed IP dropdown with filtered IPs
        self.fields['ip_address'].queryset = get_filtered_free_ips()
        self.fields['ip_address'].empty_label = 'Select IP Address'
        self.fields['ip_address'].required = False
        self.fields['manual_ip'].required = False
        self.fields['ip_label'].required = True
        
        # Pre-select ip_type based on existing data
        if self.instance and self.instance.pk:
            if self.instance.ip_address:
                self.fields['ip_type'].initial = 'managed'
            elif self.instance.manual_ip:
                self.fields['ip_type'].initial = 'manual'
    
    def clean(self):
        """Validate IP entry."""
        cleaned_data = super().clean()
        ip_type = cleaned_data.get('ip_type')
        ip_address = cleaned_data.get('ip_address')
        manual_ip = cleaned_data.get('manual_ip')
        
        # Exactly one IP must be provided
        if ip_type == 'managed' and not ip_address:
            self.add_error('ip_address', 'Please select an IP address.')
        elif ip_type == 'manual' and not manual_ip:
            self.add_error('manual_ip', 'Please enter an IP address.')
        
        # Clear the unused field
        if ip_type == 'managed':
            cleaned_data['manual_ip'] = None
        else:
            cleaned_data['ip_address'] = None
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save additional IP and mark as non-primary."""
        instance = super().save(commit=False)
        instance.is_primary = False
        
        # Handle IP pool assignment for managed IPs
        if commit:
            instance.save()
            if instance.ip_address:
                instance.ip_address.is_assigned = True
                instance.ip_address.assigned_to_asset = instance.asset
                instance.ip_address.save()
        
        return instance
```

**Formset Factory:**

```python
from django.forms import inlineformset_factory

AdditionalIPFormSet = inlineformset_factory(
    Asset,
    AssetIPAddress,
    form=AdditionalIPForm,
    extra=0,  # No extra empty forms by default
    can_delete=True,
    can_order=False,
    min_num=0,
    max_num=10,  # Reasonable limit
    validate_min=False,
    validate_max=True
)
```

**Formset Configuration Parameters:**
- `extra=0`: Don't show extra empty forms (JavaScript adds them)
- `can_delete=True`: Allow removing additional IPs
- `min_num=0`: Additional IPs are optional
- `max_num=10`: Prevent abuse (reasonable limit)
- Parent model: `Asset`
- Child model: `AssetIPAddress`

### 4. View Layer


**File**: `assets/views/asset_create_view.py` and `asset_update_view.py`

#### 4.1 Create View Updates

```python
from django.views.generic import CreateView
from django.db import transaction
from assets.forms import AssetForm, AdditionalIPFormSet

class AssetCreateView(LoginRequiredMixin, CreateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    
    def get_context_data(self, **kwargs):
        """Add formset to context."""
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['additional_ip_formset'] = AdditionalIPFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['additional_ip_formset'] = AdditionalIPFormSet(
                instance=self.object
            )
        
        return context
    
    def form_valid(self, form):
        """Validate both form and formset."""
        context = self.get_context_data()
        additional_ip_formset = context['additional_ip_formset']
        
        # Validate formset
        if not additional_ip_formset.is_valid():
            return self.form_invalid(form)
        
        # Save in transaction
        with transaction.atomic():
            # Save asset and primary IP
            self.object = form.save()
            
            # Save additional IPs
            additional_ip_formset.instance = self.object
            additional_ip_formset.save()
        
        return redirect(self.get_success_url())
```

#### 4.2 Update View Updates

```python
class AssetUpdateView(LoginRequiredMixin, UpdateView):
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    
    def get_context_data(self, **kwargs):
        """Add formset with existing additional IPs."""
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['additional_ip_formset'] = AdditionalIPFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            # Filter to only non-primary IPs for the formset
            context['additional_ip_formset'] = AdditionalIPFormSet(
                instance=self.object,
                queryset=self.object.asset_ip_addresses.filter(is_primary=False)
            )
        
        return context
    
    def form_valid(self, form):
        """Validate and save form and formset."""
        context = self.get_context_data()
        additional_ip_formset = context['additional_ip_formset']
        
        if not additional_ip_formset.is_valid():
            return self.form_invalid(form)
        
        with transaction.atomic():
            # Save asset and primary IP
            self.object = form.save()
            
            # Save additional IPs (handles updates and deletions)
            additional_ip_formset.save()
            
            # Release any deleted managed IPs
            for deleted_form in additional_ip_formset.deleted_forms:
                if deleted_form.instance.ip_address:
                    ip = deleted_form.instance.ip_address
                    ip.is_assigned = False
                    ip.assigned_to_asset = None
                    ip.save()
        
        return redirect(self.get_success_url())
```

**Key View Responsibilities:**
- Instantiate both `AssetForm` and `AdditionalIPFormSet`
- Pass formset to template via context
- Validate both form and formset
- Save both in a database transaction
- Handle IP pool updates for deleted IPs

### 5. Template Layer


**File**: `assets/templates/assets/asset_form.html`

#### 5.1 Primary IP Section

```html
<!-- Primary IP Section -->
<div class="form-section">
    <h5>IP Address</h5>
    
    <!-- IP Type Selection -->
    <div class="form-group">
        {{ form.primary_ip_type.label_tag }}
        <div class="radio-group">
            {% for radio in form.primary_ip_type %}
                <div class="form-check form-check-inline">
                    {{ radio.tag }}
                    <label class="form-check-label" for="{{ radio.id_for_label }}">
                        {{ radio.choice_label }}
                    </label>
                </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Managed IP Field -->
    <div class="form-group" id="primary-managed-ip-group">
        {{ form.ip_address.label_tag }}
        {{ form.ip_address }}
        {% if form.ip_address.errors %}
            <div class="text-danger">{{ form.ip_address.errors }}</div>
        {% endif %}
    </div>
    
    <!-- Manual IP Field -->
    <div class="form-group" id="primary-manual-ip-group" style="display:none;">
        {{ form.manual_ip.label_tag }}
        {{ form.manual_ip }}
        {% if form.manual_ip.errors %}
            <div class="text-danger">{{ form.manual_ip.errors }}</div>
        {% endif %}
    </div>
</div>
```

#### 5.2 Additional IPs Section

```html
<!-- Additional IP Addresses Section -->
<div class="form-section">
    <h5>Additional IP Addresses</h5>
    <p class="text-muted">Add supplementary IP addresses (e.g., WiFi, Mobile, VPN)</p>
    
    <!-- Formset Management Form -->
    {{ additional_ip_formset.management_form }}
    
    <!-- Additional IP Forms Container -->
    <div id="additional-ip-forms">
        {% for form in additional_ip_formset %}
            <div class="additional-ip-form border rounded p-3 mb-3" data-form-index="{{ forloop.counter0 }}">
                <!-- Deletion checkbox (hidden by default) -->
                {% if form.instance.pk %}
                    <div style="display:none;">
                        {{ form.DELETE }}
                    </div>
                {% endif %}
                
                <!-- IP Label -->
                <div class="form-group">
                    {{ form.ip_label.label_tag }}
                    {{ form.ip_label }}
                    {% if form.ip_label.errors %}
                        <div class="text-danger">{{ form.ip_label.errors }}</div>
                    {% endif %}
                </div>
                
                <!-- IP Type Selection -->
                <div class="form-group">
                    <label>IP Type</label>
                    <div class="radio-group">
                        {% for radio in form.ip_type %}
                            <div class="form-check form-check-inline">
                                {{ radio.tag }}
                                <label class="form-check-label" for="{{ radio.id_for_label }}">
                                    {{ radio.choice_label }}
                                </label>
                            </div>
                        {% endfor %}
                    </div>
                </div>
                
                <!-- Managed IP Field -->
                <div class="form-group additional-managed-ip-group">
                    {{ form.ip_address.label_tag }}
                    {{ form.ip_address }}
                    {% if form.ip_address.errors %}
                        <div class="text-danger">{{ form.ip_address.errors }}</div>
                    {% endif %}
                </div>
                
                <!-- Manual IP Field -->
                <div class="form-group additional-manual-ip-group" style="display:none;">
                    {{ form.manual_ip.label_tag }}
                    {{ form.manual_ip }}
                    {% if form.manual_ip.errors %}
                        <div class="text-danger">{{ form.manual_ip.errors }}</div>
                    {% endif %}
                </div>
                
                <!-- Remove Button -->
                <button type="button" class="btn btn-sm btn-danger remove-additional-ip">
                    Remove
                </button>
            </div>
        {% endfor %}
    </div>
    
    <!-- Add Button -->
    <button type="button" class="btn btn-secondary" id="add-additional-ip">
        + Add Additional IP
    </button>
    
    <!-- Empty Form Template (hidden) -->
    <div id="empty-additional-ip-form" style="display:none;">
        <!-- Clone of the form structure with __prefix__ placeholder -->
        <!-- This will be used by JavaScript to add new forms -->
    </div>
</div>
```

#### 5.3 JavaScript for Dynamic Forms


```html
<script>
document.addEventListener('DOMContentLoaded', function() {
    // Handle primary IP type toggle
    const primaryIpTypeRadios = document.querySelectorAll('input[name="primary_ip_type"]');
    const primaryManagedGroup = document.getElementById('primary-managed-ip-group');
    const primaryManualGroup = document.getElementById('primary-manual-ip-group');
    
    primaryIpTypeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'managed') {
                primaryManagedGroup.style.display = 'block';
                primaryManualGroup.style.display = 'none';
            } else {
                primaryManagedGroup.style.display = 'none';
                primaryManualGroup.style.display = 'block';
            }
        });
    });
    
    // Initialize visibility based on current selection
    const selectedPrimaryType = document.querySelector('input[name="primary_ip_type"]:checked');
    if (selectedPrimaryType) {
        selectedPrimaryType.dispatchEvent(new Event('change'));
    }
    
    // Handle additional IP type toggles
    function setupAdditionalIPTypeToggle(formDiv) {
        const ipTypeRadios = formDiv.querySelectorAll('.ip-type-radio');
        const managedGroup = formDiv.querySelector('.additional-managed-ip-group');
        const manualGroup = formDiv.querySelector('.additional-manual-ip-group');
        
        ipTypeRadios.forEach(radio => {
            radio.addEventListener('change', function() {
                if (this.value === 'managed') {
                    managedGroup.style.display = 'block';
                    manualGroup.style.display = 'none';
                } else {
                    managedGroup.style.display = 'none';
                    manualGroup.style.display = 'block';
                }
            });
        });
        
        // Initialize visibility
        const selectedType = formDiv.querySelector('.ip-type-radio:checked');
        if (selectedType) {
            selectedType.dispatchEvent(new Event('change'));
        }
    }
    
    // Setup toggles for existing forms
    document.querySelectorAll('.additional-ip-form').forEach(setupAdditionalIPTypeToggle);
    
    // Add additional IP
    const addButton = document.getElementById('add-additional-ip');
    const formsContainer = document.getElementById('additional-ip-forms');
    const emptyForm = document.getElementById('empty-additional-ip-form');
    const totalFormsInput = document.querySelector('input[name="asset_ip_addresses-TOTAL_FORMS"]');
    
    addButton.addEventListener('click', function() {
        const formIndex = parseInt(totalFormsInput.value);
        
        // Clone empty form
        const newFormHtml = emptyForm.innerHTML.replace(/__prefix__/g, formIndex);
        
        // Create new form div
        const newFormDiv = document.createElement('div');
        newFormDiv.className = 'additional-ip-form border rounded p-3 mb-3';
        newFormDiv.setAttribute('data-form-index', formIndex);
        newFormDiv.innerHTML = newFormHtml;
        
        // Append to container
        formsContainer.appendChild(newFormDiv);
        
        // Update total forms count
        totalFormsInput.value = formIndex + 1;
        
        // Setup IP type toggle for new form
        setupAdditionalIPTypeToggle(newFormDiv);
        
        // Setup remove button
        setupRemoveButton(newFormDiv);
    });
    
    // Remove additional IP
    function setupRemoveButton(formDiv) {
        const removeButton = formDiv.querySelector('.remove-additional-ip');
        removeButton.addEventListener('click', function() {
            const deleteCheckbox = formDiv.querySelector('input[name$="-DELETE"]');
            
            if (deleteCheckbox) {
                // Existing form: mark for deletion
                deleteCheckbox.checked = true;
                formDiv.style.display = 'none';
            } else {
                // New form: remove from DOM
                formDiv.remove();
                
                // Update total forms count
                totalFormsInput.value = parseInt(totalFormsInput.value) - 1;
                
                // Re-index remaining forms
                reindexForms();
            }
        });
    }
    
    // Setup remove buttons for existing forms
    document.querySelectorAll('.remove-additional-ip').forEach(button => {
        setupRemoveButton(button.closest('.additional-ip-form'));
    });
    
    // Re-index forms after removal
    function reindexForms() {
        const forms = formsContainer.querySelectorAll('.additional-ip-form:not([style*="display: none"])');
        forms.forEach((formDiv, index) => {
            formDiv.setAttribute('data-form-index', index);
            
            // Update field names and IDs
            formDiv.querySelectorAll('input, select, textarea').forEach(field => {
                if (field.name) {
                    field.name = field.name.replace(/asset_ip_addresses-\d+-/, `asset_ip_addresses-${index}-`);
                }
                if (field.id) {
                    field.id = field.id.replace(/id_asset_ip_addresses-\d+-/, `id_asset_ip_addresses-${index}-`);
                }
            });
            
            // Update label for attributes
            formDiv.querySelectorAll('label').forEach(label => {
                if (label.htmlFor) {
                    label.htmlFor = label.htmlFor.replace(/id_asset_ip_addresses-\d+-/, `id_asset_ip_addresses-${index}-`);
                }
            });
        });
    }
});
</script>
```

**JavaScript Responsibilities:**
1. **Toggle IP Type**: Show/hide managed vs manual IP fields based on radio selection
2. **Add Form**: Clone empty form template, replace `__prefix__` with form index, append to container
3. **Remove Form**: Mark existing forms for deletion or remove new forms from DOM
4. **Re-index Forms**: Update form field names/IDs after removal to maintain sequential indexes
5. **Update Management Form**: Keep `TOTAL_FORMS` count synchronized

**Progressive Enhancement Approach:**
- Form works without JavaScript (user can submit multiple times)
- JavaScript enhances UX with dynamic add/remove
- Server-side validation remains authoritative

### 6. Display Components


#### 6.1 Asset Detail View

**File**: `assets/templates/assets/asset_detail.html`

```html
<!-- Primary IP Display -->
<div class="detail-row">
    <strong>IP Address:</strong>
    <span>
        {% if asset.get_primary_ip %}
            {{ asset.get_primary_ip.get_ip_display }}
        {% else %}
            <em class="text-muted">No IP assigned</em>
        {% endif %}
    </span>
</div>

<!-- Additional IPs Display -->
{% with additional_ips=asset.asset_ip_addresses.filter|is_primary=False %}
    {% if additional_ips %}
        <div class="detail-row">
            <strong>Additional IP Addresses:</strong>
            <ul class="list-unstyled mb-0">
                {% for ip_assoc in additional_ips %}
                    <li>
                        <span class="badge bg-secondary">{{ ip_assoc.ip_label }}</span>
                        {{ ip_assoc.get_ip_display }}
                    </li>
                {% endfor %}
            </ul>
        </div>
    {% endif %}
{% endwith %}
```

**Display Format:**
- Primary IP: Simple text display
- Additional IPs: List with badge labels
- No IP: Italicized "No IP assigned" text

#### 6.2 Asset List View

**File**: `assets/templates/assets/asset_list.html`

```html
<table class="table table-striped">
    <thead>
        <tr>
            <th>Asset Tag</th>
            <th>System Type</th>
            <th>IP Address</th>  <!-- Simplified column name -->
            <th>Assigned To</th>
            <th>Status</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for asset in assets %}
            <tr>
                <td>{{ asset.asset_tag }}</td>
                <td>{{ asset.system_type }}</td>
                <td>
                    {% if asset.get_primary_ip %}
                        {{ asset.get_primary_ip.get_ip_display }}
                    {% else %}
                        <span class="text-muted">—</span>
                    {% endif %}
                </td>
                <td>{{ asset.assigned_to|default:"—" }}</td>
                <td>
                    <span class="badge bg-{{ asset.get_status_color }}">
                        {{ asset.get_status_display }}
                    </span>
                </td>
                <td>
                    <a href="{% url 'asset-detail' asset.pk %}" class="btn btn-sm btn-info">View</a>
                </td>
            </tr>
        {% endfor %}
    </tbody>
</table>
```

**List View Changes:**
- Column renamed from "Primary IP (LAN)" to "IP Address"
- Only displays primary IP (additional IPs visible in detail view)
- Empty cells show "—" for consistency

## Data Models

### AssetIPAddress Model (Updated)

```python
class AssetIPAddress(models.Model):
    """Junction model linking Assets to IP addresses with optional labels."""
    
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, 
                              related_name='asset_ip_addresses')
    ip_address = models.ForeignKey('IPAddress', on_delete=models.PROTECT,
                                   null=True, blank=True)
    manual_ip = models.GenericIPAddressField(protocol='IPv4', 
                                            null=True, blank=True)
    is_primary = models.BooleanField(default=False, db_index=True)
    ip_label = models.CharField(max_length=100, blank=True, null=True)  # NEW
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(ip_address__isnull=False, manual_ip__isnull=True) |
                    models.Q(ip_address__isnull=True, manual_ip__isnull=False)
                ),
                name='asset_ip_exactly_one_ip_type'
            ),
        ]
```

**Field Descriptions:**
- `ip_label`: Optional 100-char description for additional IPs
- Required for `is_primary=False`, must be null for `is_primary=True`
- Allows labeling like "WiFi", "Mobile IP", "VPN", "Backup"

### Asset Model (No Changes)

The `Asset` model remains unchanged. Existing helper methods continue to work:
- `get_primary_ip()`: Returns primary `AssetIPAddress` or None
- `get_secondary_ips()`: Returns queryset of non-primary `AssetIPAddress` records
- `get_all_ips()`: Returns all `AssetIPAddress` records
- `get_display_primary_ip()`: Returns primary IP string or "No IP assigned"

### IPAddress Model (No Changes)

The `IPAddress` model remains unchanged - IP pool management continues working as-is.

## Error Handling


### Validation Errors

**Form-Level Validation:**

```python
# Duplicate IP on same asset
ValidationError("This IP is already assigned to this asset")

# Missing IP when type selected
ValidationError("Please select an IP address")  # for managed
ValidationError("Please enter an IP address")    # for manual

# Invalid IP format
ValidationError("Enter a valid IPv4 address")

# Missing label for additional IP
ValidationError("Label is required for additional IP addresses")

# Whitespace-only label
ValidationError("Label cannot contain only whitespace")

# Both IP types provided
ValidationError("Please provide either IP Address or Manual IP, not both")

# Neither IP type provided
ValidationError("Either managed or manual IP must be provided")
```

**Formset-Level Validation:**

```python
# Too many additional IPs
ValidationError("Please ensure there are no more than 10 forms")

# Formset management data tampered
ValidationError("ManagementForm data is missing or has been tampered with")
```

**Model-Level Validation:**

```python
# Database constraint violation
IntegrityError("asset_ip_exactly_one_ip_type constraint failed")
```

### User-Facing Error Display

**Form Errors:**
- Display inline below each field in red text
- Use Bootstrap's `.text-danger` class
- Show field-specific error messages

**Formset Errors:**
- Display non-field errors at the top of the formset section
- Use Bootstrap's `.alert-danger` class
- Preserve all form data on validation failure

**Success Messages:**
- Use Django messages framework
- Display success banner after save
- Redirect to asset detail view

### Error Recovery

**Validation Failure Recovery:**
1. Preserve all form data (primary IP + all additional IPs)
2. Maintain formset state including partially filled forms
3. Highlight erroneous fields with red borders
4. Show clear error messages for each issue
5. Allow user to correct and resubmit

**JavaScript Error Handling:**
- Graceful degradation if JavaScript disabled
- Console logging for debugging in development
- User-friendly alerts for critical errors

## Testing Strategy

### Unit Tests

**Model Tests** (`assets/tests/test_models.py`):

```python
def test_asset_ip_address_with_label():
    """Test creating AssetIPAddress with ip_label."""
    asset = create_test_asset()
    ip_assoc = AssetIPAddress.objects.create(
        asset=asset,
        manual_ip='192.168.1.100',
        is_primary=False,
        ip_label='WiFi'
    )
    assert ip_assoc.ip_label == 'WiFi'

def test_primary_ip_cannot_have_label():
    """Test that primary IPs cannot have labels."""
    asset = create_test_asset()
    with pytest.raises(ValidationError):
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.100',
            is_primary=True,
            ip_label='WiFi'
        )
        ip_assoc.full_clean()

def test_additional_ip_requires_label():
    """Test that additional IPs require labels."""
    asset = create_test_asset()
    with pytest.raises(ValidationError):
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.100',
            is_primary=False,
            ip_label=None
        )
        ip_assoc.full_clean()

def test_whitespace_label_invalid():
    """Test that whitespace-only labels are rejected."""
    asset = create_test_asset()
    with pytest.raises(ValidationError):
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.100',
            is_primary=False,
            ip_label='   '
        )
        ip_assoc.full_clean()
```

**Form Tests** (`assets/tests/test_forms.py`):

```python
def test_additional_ip_form_valid_data():
    """Test AdditionalIPForm with valid data."""
    asset = create_test_asset()
    form_data = {
        'ip_type': 'manual',
        'ip_label': 'WiFi',
        'manual_ip': '192.168.1.100'
    }
    form = AdditionalIPForm(data=form_data)
    assert form.is_valid()

def test_additional_ip_form_missing_label():
    """Test AdditionalIPForm requires label."""
    form_data = {
        'ip_type': 'manual',
        'manual_ip': '192.168.1.100'
    }
    form = AdditionalIPForm(data=form_data)
    assert not form.is_valid()
    assert 'ip_label' in form.errors

def test_formset_with_multiple_additional_ips():
    """Test formset handles multiple additional IPs."""
    asset = create_test_asset()
    formset_data = {
        'asset_ip_addresses-TOTAL_FORMS': '2',
        'asset_ip_addresses-INITIAL_FORMS': '0',
        'asset_ip_addresses-0-ip_type': 'manual',
        'asset_ip_addresses-0-ip_label': 'WiFi',
        'asset_ip_addresses-0-manual_ip': '192.168.1.100',
        'asset_ip_addresses-1-ip_type': 'manual',
        'asset_ip_addresses-1-ip_label': 'Mobile',
        'asset_ip_addresses-1-manual_ip': '192.168.1.101',
    }
    formset = AdditionalIPFormSet(data=formset_data, instance=asset)
    assert formset.is_valid()
```

### Integration Tests

**View Tests** (`assets/tests/test_views.py`):

```python
def test_create_asset_with_additional_ips(client, authenticated_user):
    """Test creating asset with primary and additional IPs."""
    response = client.post(reverse('asset-create'), {
        'asset_tag': 'TEST001',
        'system_type': 'Desktop',
        'primary_ip_type': 'manual',
        'manual_ip': '192.168.1.50',
        'asset_ip_addresses-TOTAL_FORMS': '2',
        'asset_ip_addresses-INITIAL_FORMS': '0',
        'asset_ip_addresses-0-ip_type': 'manual',
        'asset_ip_addresses-0-ip_label': 'WiFi',
        'asset_ip_addresses-0-manual_ip': '192.168.1.100',
        'asset_ip_addresses-1-ip_type': 'manual',
        'asset_ip_addresses-1-ip_label': 'Mobile',
        'asset_ip_addresses-1-manual_ip': '192.168.1.101',
    })
    
    assert response.status_code == 302
    asset = Asset.objects.get(asset_tag='TEST001')
    assert asset.asset_ip_addresses.count() == 3  # 1 primary + 2 additional
    assert asset.get_primary_ip().manual_ip == '192.168.1.50'

def test_update_asset_remove_additional_ip(client, authenticated_user):
    """Test removing an additional IP from existing asset."""
    asset = create_asset_with_ips()
    additional_ip = asset.asset_ip_addresses.filter(is_primary=False).first()
    
    response = client.post(reverse('asset-update', args=[asset.pk]), {
        # ... form data ...
        f'asset_ip_addresses-0-id': additional_ip.pk,
        f'asset_ip_addresses-0-DELETE': 'on',
    })
    
    assert response.status_code == 302
    assert not AssetIPAddress.objects.filter(pk=additional_ip.pk).exists()
```

### Manual Testing Checklist


**Form Functionality:**
- [ ] Primary IP radio toggles show/hide correct fields
- [ ] Additional IP type radios toggle managed/manual fields
- [ ] "Add Additional IP" button adds new form
- [ ] "Remove" button removes/marks for deletion correctly
- [ ] Form submission with 0 additional IPs works
- [ ] Form submission with multiple additional IPs works
- [ ] Form preserves data on validation errors
- [ ] Managed IP dropdowns show only available IPs

**Validation:**
- [ ] Cannot submit additional IP without label
- [ ] Cannot submit additional IP with whitespace-only label
- [ ] Cannot submit additional IP without selecting/entering IP
- [ ] Cannot submit duplicate IP on same asset
- [ ] Cannot exceed 10 additional IPs
- [ ] Primary IP cannot have label (enforced at model level)

**Display:**
- [ ] Asset list shows primary IP only
- [ ] Asset detail shows primary IP prominently
- [ ] Asset detail shows additional IPs with labels
- [ ] Asset detail shows "No IP assigned" when appropriate
- [ ] Additional IPs displayed with badge labels

**IP Pool Management:**
- [ ] Creating asset with managed IP marks it assigned
- [ ] Updating asset to different managed IP releases old IP
- [ ] Deleting additional managed IP releases it
- [ ] Deleting asset releases all managed IPs
- [ ] Manual IPs don't affect IP pool

**Migration:**
- [ ] Migration adds ip_label field successfully
- [ ] Data migration sets "Secondary IP" for existing secondary IPs
- [ ] Existing primary IPs have null ip_label
- [ ] No data loss during migration
- [ ] Rollback migration works

### Property-Based Testing Applicability

**Assessment**: Property-based testing is **NOT appropriate** for this feature.

**Rationale:**
- This feature is primarily CRUD operations with Django forms and formsets
- Behavior is deterministic based on form input
- Heavy reliance on Django ORM and database state
- UI interactions cannot be effectively property-tested
- Example-based tests and integration tests provide better coverage

**Alternative Testing Approach:**
- Unit tests for model validation rules
- Form tests for validation logic
- Integration tests for view workflows
- Manual testing for UI/JavaScript behavior

**Testing will focus on:**
- Example-based unit tests for specific validation scenarios
- Integration tests for complete create/update workflows
- Edge case testing (empty forms, max forms, deletions)
- Migration testing with sample data

## Backward Compatibility

### Data Compatibility

**Existing Assets:**
- All existing `AssetIPAddress` records remain valid
- `ip_label` field is nullable - no data loss
- Data migration provides sensible defaults
- Primary IPs continue working unchanged
- Secondary IPs become "additional IPs" with default label

**Existing Queries:**
- `Asset.get_primary_ip()` works unchanged
- `Asset.get_secondary_ips()` works unchanged (now returns IPs with labels)
- All existing ORM queries remain valid
- No breaking changes to model API

### UI Compatibility

**Breaking Changes:**
- Form labels changed (users will see "IP Address" instead of "Primary IP (LAN)")
- Secondary IP section replaced with "Additional IP Addresses" section
- Users must now provide labels for additional IPs

**Migration Path:**
- No user action required for existing data
- New workflows apparent from UI labels
- In-app help text guides users

### API Compatibility (if applicable)

If the application exposes APIs:
- Add `ip_label` to serializers (nullable field)
- Maintain backward compatibility for API consumers
- Document new field in API documentation
- Version API if breaking changes required

## Performance Considerations

### Database Impact

**Query Performance:**
- Existing indexes on `AssetIPAddress` remain optimal
- No additional indexes required for `ip_label`
- Filtering by `is_primary` remains efficient
- Asset detail view: 1 additional query for additional IPs (already exists)

**Write Performance:**
- Formset saves N additional IPs in single transaction
- No performance degradation vs current implementation
- IP pool updates remain O(1) per IP

### UI Performance

**JavaScript Performance:**
- Form cloning is lightweight (< 1KB per form)
- DOM manipulation is minimal
- Re-indexing affects only visible forms (max 10)
- No noticeable delay on modern browsers

**Page Load:**
- No additional HTTP requests
- Formset renders server-side (standard Django)
- JavaScript is vanilla (no heavy libraries)
- Empty form template adds ~2KB to page size

### Scalability

**Limits:**
- Max 10 additional IPs per asset (enforced at formset level)
- Reasonable for typical use cases
- Can be adjusted via `max_num` parameter if needed

**Large Datasets:**
- Paginated asset lists unaffected
- Detail view queries remain efficient
- No N+1 query issues

## Security Considerations

### Input Validation

**Server-Side Validation:**
- All form data validated on server
- Django ORM constraints prevent invalid data
- IP address format validated by `GenericIPAddressField`
- Label length limited to 100 characters
- XSS protection via Django template auto-escaping

**Client-Side Validation:**
- JavaScript validation is enhancement only
- Server validation is authoritative
- Form can be submitted without JavaScript

### Authorization

**Access Control:**
- Existing Django authentication required
- Only authenticated users can create/edit assets
- Permission checks remain unchanged
- No elevation of privilege concerns

### Data Integrity

**Transaction Safety:**
- All saves wrapped in database transactions
- Rollback on validation failure
- Atomic operations for primary + additional IPs
- Foreign key constraints prevent orphaned records

**IP Pool Consistency:**
- IP assignments remain consistent
- No race conditions in IP allocation
- Deletion cascades handled by Django ORM

### CSRF Protection

- Django CSRF middleware protects all POST requests
- Formset includes CSRF token automatically
- No additional CSRF concerns

## Deployment Strategy

### Migration Steps

1. **Pre-Deployment:**
   - Review migration files
   - Test migrations on staging database
   - Backup production database
   - Verify rollback procedure

2. **Deployment:**
   - Deploy code to production
   - Run migrations: `python manage.py migrate`
   - Verify migration success
   - Monitor logs for errors

3. **Post-Deployment:**
   - Verify existing assets display correctly
   - Test creating new asset with multiple IPs
   - Test updating existing asset
   - Monitor error logs

### Rollback Plan

**If Issues Occur:**
1. Revert code deployment
2. Run reverse migration: `python manage.py migrate assets XXXX_previous_migration`
3. Verify data integrity
4. Investigate and fix issues in development

**Data Safety:**
- Rollback migration clears `ip_label` field
- No data loss - field is nullable
- Can re-run forward migration after fixes

### Zero-Downtime Considerations

**Deployment Approach:**
- Migration is additive (adds field)
- No breaking changes to existing functionality
- Can deploy during business hours
- No service interruption required

**Staged Rollout (Optional):**
- Deploy migration first, verify
- Deploy code changes second
- Allows testing migration impact separately

