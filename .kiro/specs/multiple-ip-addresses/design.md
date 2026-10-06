# Design Document: Multiple IP Addresses per Asset

## Overview

The multiple IP addresses feature extends the existing Asset model to support assigning multiple IP addresses to a single asset. Currently, each asset can have only one IP address (either a managed IP from the IPAddress pool or a manually entered IP). This enhancement enables assets to have one primary IP address and zero or more secondary IP addresses, supporting scenarios where users switch between different network connections (e.g., LAN and WiFi).

The design introduces a junction model (AssetIPAddress) to create a many-to-many relationship between Assets and IP addresses while maintaining backward compatibility with the existing single-IP structure. The solution supports both managed IPs (tracked in IP_Pool) and manual IPs (not tracked) for both primary and secondary addresses.

Key design principles:
- **Backward compatibility**: Preserve existing Asset.ip_address and Asset.manual_ip fields during transition
- **Data integrity**: Maintain IP conflict prevention for managed IPs
- **Flexible IP management**: Support mixing managed and manual IPs as secondary addresses
- **Clear primary/secondary distinction**: Always identify one IP as primary
- **Seamless migration**: Automatically migrate existing single IPs to new structure

## Architecture

### System Components

The feature consists of five main layers:

1. **Data Layer**: New AssetIPAddress junction model linking Assets with multiple IPs
2. **Service Layer**: AssetIPService for business logic managing IP assignments
3. **Form Layer**: Enhanced forms supporting secondary IP management
4. **View Layer**: Updated views for IP addition/removal operations
5. **Migration Layer**: Data migration strategy from single-IP to multiple-IP schema

### Integration Points

- **Asset Model**: Extended with methods for managing multiple IPs via AssetIPAddress
- **IPAddress Model**: Continues to track is_assigned status for managed IPs
- **AssetForm**: Enhanced to support adding/removing secondary IPs
- **ReassignmentForm**: Updated to handle multiple IPs during freed system reassignment
- **IP Management Service**: Extended to handle AssetIPAddress assignments

### Data Flow

1. **Add Secondary IP**:
   - User selects "Add Secondary IP" → Form displays available IPs → User selects IP → Service validates availability → Service creates AssetIPAddress record → IP marked as assigned

2. **Remove Secondary IP**:
   - User selects "Remove IP" on secondary IP → Confirmation prompt → Service deletes AssetIPAddress record → Managed IP marked as unassigned

3. **Change Primary IP**:
   - User selects new primary IP from secondary IPs → Service validates secondary exists → Service updates is_primary flags → Old primary becomes secondary

4. **Data Migration**:
   - Migration script runs → Existing Asset.ip_address values migrated to AssetIPAddress with is_primary=True → Existing Asset.manual_ip values migrated to AssetIPAddress with is_primary=True


## Components and Interfaces

### Models

#### AssetIPAddress Junction Model

```python
class AssetIPAddress(models.Model):
    """Junction model for many-to-many relationship between Assets and IP addresses."""
    
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='asset_ip_addresses',
        db_index=True
    )
    ip_address = models.ForeignKey(
        IPAddress,
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
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        indexes = [
            models.Index(fields=['asset', 'is_primary']),
            models.Index(fields=['ip_address']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(ip_address__isnull=False, manual_ip__isnull=True) |
                    models.Q(ip_address__isnull=True, manual_ip__isnull=False)
                ),
                name='asset_ip_exactly_one_ip_type'
            ),
        ]
    
    def __str__(self):
        ip = self.ip_address.address if self.ip_address else self.manual_ip
        primary_label = " (Primary)" if self.is_primary else ""
        return f"{self.asset.asset_tag} - {ip}{primary_label}"
    
    def clean(self):
        """Validate AssetIPAddress business rules."""
        # Exactly one of ip_address or manual_ip must be set
        if not self.ip_address and not self.manual_ip:
            raise ValidationError("Either ip_address or manual_ip must be provided.")
        
        if self.ip_address and self.manual_ip:
            raise ValidationError("Cannot have both ip_address and manual_ip.")
        
        # Check for duplicate IP on same asset
        if self.asset_id:
            existing = AssetIPAddress.objects.filter(asset=self.asset).exclude(pk=self.pk)
            
            if self.ip_address:
                if existing.filter(ip_address=self.ip_address).exists():
                    raise ValidationError("This managed IP is already assigned to this asset.")
            
            if self.manual_ip:
                if existing.filter(manual_ip=self.manual_ip).exists():
                    raise ValidationError("This manual IP is already assigned to this asset.")
    
    def get_ip_display(self):
        """Return the IP address to display (managed or manual)."""
        if self.ip_address:
            return self.ip_address.address
        return self.manual_ip
```

**Design Decisions**:
- **ForeignKey to Asset with CASCADE**: Deleting an asset automatically removes all IP associations
- **ForeignKey to IPAddress with PROTECT**: Prevents accidental IPAddress deletion if assigned
- **Nullable ip_address and manual_ip**: One must be set, enforced by CheckConstraint and clean()
- **is_primary flag**: Identifies which IP is the primary address
- **CheckConstraint**: Database-level enforcement that exactly one of ip_address or manual_ip is set
- **Ordering**: Primary IPs first, then by creation date for secondaries


#### Asset Model Extensions

```python
class Asset(models.Model):
    # ... existing fields ...
    
    # Keep existing fields for backward compatibility during migration
    # ip_address = models.ForeignKey(IPAddress, ...) # DEPRECATED
    # manual_ip = models.GenericIPAddressField(...) # DEPRECATED
    
    def get_primary_ip(self):
        """
        Get the primary IP address for this asset.
        
        Returns:
            AssetIPAddress: Primary IP association, or None
        """
        return self.asset_ip_addresses.filter(is_primary=True).first()
    
    def get_secondary_ips(self):
        """
        Get all secondary IP addresses for this asset.
        
        Returns:
            QuerySet of AssetIPAddress: All secondary IP associations
        """
        return self.asset_ip_addresses.filter(is_primary=False)
    
    def get_all_ips(self):
        """
        Get all IP addresses (primary and secondary) for this asset.
        
        Returns:
            QuerySet of AssetIPAddress: All IP associations ordered by is_primary desc
        """
        return self.asset_ip_addresses.all()
    
    def get_display_primary_ip(self):
        """
        Get the primary IP address as a string for display.
        
        Returns:
            str: IP address string, or "No IP assigned"
        """
        primary = self.get_primary_ip()
        if primary:
            return primary.get_ip_display()
        return "No IP assigned"
    
    def has_managed_primary_ip(self):
        """
        Check if the asset has a managed primary IP.
        
        Returns:
            bool: True if primary IP is managed (from IP pool)
        """
        primary = self.get_primary_ip()
        return primary and primary.ip_address is not None
```

**Design Decisions**:
- **Backward compatibility methods**: get_display_primary_ip() replaces direct access to ip_address/manual_ip
- **QuerySet return types**: Enable chaining and efficient database queries
- **Separation of concerns**: Distinct methods for primary vs secondary vs all IPs


### Services

#### AssetIPService

```python
class AssetIPService:
    """Service for managing asset IP address assignments."""
    
    @staticmethod
    def add_secondary_ip(asset, ip_address=None, manual_ip=None, user=None):
        """
        Add a secondary IP address to an asset.
        
        Args:
            asset: Asset instance
            ip_address: IPAddress instance (managed IP), mutually exclusive with manual_ip
            manual_ip: String IP address (manual IP), mutually exclusive with ip_address
            user: User performing the operation (for audit trail)
        
        Returns:
            AssetIPAddress: Created IP association
        
        Raises:
            ValidationError: If IP is invalid, already assigned, or both types provided
        """
        with transaction.atomic():
            # Validate exactly one IP type provided
            if not ip_address and not manual_ip:
                raise ValidationError("Either ip_address or manual_ip must be provided.")
            
            if ip_address and manual_ip:
                raise ValidationError("Cannot provide both ip_address and manual_ip.")
            
            # Check for managed IP conflicts
            if ip_address:
                if ip_address.is_assigned:
                    raise ValidationError(f"IP {ip_address.address} is already assigned.")
                
                # Check if this IP is already assigned to this asset
                if AssetIPAddress.objects.filter(asset=asset, ip_address=ip_address).exists():
                    raise ValidationError(f"IP {ip_address.address} is already assigned to this asset.")
            
            # Check for manual IP duplicates on same asset
            if manual_ip:
                if AssetIPAddress.objects.filter(asset=asset, manual_ip=manual_ip).exists():
                    raise ValidationError(f"Manual IP {manual_ip} is already assigned to this asset.")
            
            # Create secondary IP association
            asset_ip = AssetIPAddress.objects.create(
                asset=asset,
                ip_address=ip_address,
                manual_ip=manual_ip,
                is_primary=False
            )
            
            # Mark managed IP as assigned
            if ip_address:
                ip_address.is_assigned = True
                ip_address.assigned_to_asset = asset
                ip_address.save()
            
            return asset_ip
    
    @staticmethod
    def remove_secondary_ip(asset_ip, user=None):
        """
        Remove a secondary IP address from an asset.
        
        Args:
            asset_ip: AssetIPAddress instance to remove
            user: User performing the operation (for audit trail)
        
        Raises:
            ValidationError: If attempting to remove primary IP without reassignment
        """
        with transaction.atomic():
            # Prevent removing primary IP
            if asset_ip.is_primary:
                raise ValidationError("Cannot remove primary IP. Designate a secondary IP as primary first.")
            
            managed_ip = asset_ip.ip_address
            
            # Delete the association
            asset_ip.delete()
            
            # Mark managed IP as unassigned
            if managed_ip:
                managed_ip.is_assigned = False
                managed_ip.assigned_to_asset = None
                managed_ip.freed_date = timezone.now()
                managed_ip.save()
```


    @staticmethod
    def set_primary_ip(asset, new_primary_asset_ip, user=None):
        """
        Change which IP address is the primary IP for an asset.
        
        Args:
            asset: Asset instance
            new_primary_asset_ip: AssetIPAddress instance to make primary
            user: User performing the operation (for audit trail)
        
        Raises:
            ValidationError: If new_primary_asset_ip doesn't belong to asset
        """
        with transaction.atomic():
            # Validate the new primary belongs to this asset
            if new_primary_asset_ip.asset_id != asset.id:
                raise ValidationError("The selected IP does not belong to this asset.")
            
            # Get current primary
            old_primary = asset.get_primary_ip()
            
            # Update flags
            if old_primary:
                old_primary.is_primary = False
                old_primary.save()
            
            new_primary_asset_ip.is_primary = True
            new_primary_asset_ip.save()
    
    @staticmethod
    def migrate_legacy_ip_to_asset_ip(asset):
        """
        Migrate asset's legacy ip_address or manual_ip to AssetIPAddress model.
        
        Args:
            asset: Asset instance with legacy IP fields
        
        Returns:
            AssetIPAddress: Created primary IP association, or None if no legacy IP
        """
        with transaction.atomic():
            # Skip if already migrated
            if asset.asset_ip_addresses.filter(is_primary=True).exists():
                return None
            
            # Migrate managed IP
            if asset.ip_address:
                asset_ip = AssetIPAddress.objects.create(
                    asset=asset,
                    ip_address=asset.ip_address,
                    manual_ip=None,
                    is_primary=True
                )
                return asset_ip
            
            # Migrate manual IP
            if asset.manual_ip:
                asset_ip = AssetIPAddress.objects.create(
                    asset=asset,
                    ip_address=None,
                    manual_ip=asset.manual_ip,
                    is_primary=True
                )
                return asset_ip
            
            return None
    
    @staticmethod
    def ensure_primary_ip_exists(asset):
        """
        Ensure asset has exactly one primary IP. If multiple or none exist, fix it.
        
        Args:
            asset: Asset instance
        
        Returns:
            AssetIPAddress: The primary IP association
        
        Raises:
            ValidationError: If asset has no IPs at all
        """
        with transaction.atomic():
            primary_ips = asset.asset_ip_addresses.filter(is_primary=True)
            primary_count = primary_ips.count()
            
            if primary_count == 1:
                return primary_ips.first()
            
            if primary_count == 0:
                # No primary - designate first IP as primary
                first_ip = asset.asset_ip_addresses.first()
                if not first_ip:
                    raise ValidationError("Asset must have at least one IP address.")
                first_ip.is_primary = True
                first_ip.save()
                return first_ip
            
            # Multiple primaries - keep first, demote others
            keep_primary = primary_ips.first()
            for ip_assoc in primary_ips.exclude(pk=keep_primary.pk):
                ip_assoc.is_primary = False
                ip_assoc.save()
            
            return keep_primary
```


### Forms

#### SecondaryIPForm

```python
class SecondaryIPForm(forms.Form):
    """Form for adding secondary IP addresses to assets."""
    
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP (from IP pool)'),
        ('manual', 'Manual IP (enter manually)'),
    ]
    
    ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='IP Type',
        initial='managed'
    )
    
    ip_address = forms.ModelChoiceField(
        queryset=IPAddress.objects.none(),
        required=False,
        empty_label="Select IP Address",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_managed_ip'}),
        label='Managed IP Address'
    )
    
    manual_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_manual_ip_input',
            'placeholder': 'e.g., 192.168.1.100',
            'style': 'display:none;'
        }),
        label='Manual IP Address'
    )
    
    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        
        # Populate managed IP dropdown with filtered free IPs
        available_ips = get_filtered_free_ips()
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [
            (ip.pk, str(ip.address)) for ip in available_ips
        ]
    
    def clean(self):
        """Validate that exactly one IP type is provided."""
        cleaned_data = super().clean()
        ip_type = cleaned_data.get('ip_type')
        ip_address = cleaned_data.get('ip_address')
        manual_ip = cleaned_data.get('manual_ip')
        
        if ip_type == 'managed':
            if not ip_address:
                raise forms.ValidationError("Please select a managed IP address.")
            cleaned_data['manual_ip'] = None
        elif ip_type == 'manual':
            if not manual_ip:
                raise forms.ValidationError("Please enter a manual IP address.")
            cleaned_data['ip_address'] = None
        
        return cleaned_data
```


#### AssetForm Updates

```python
class AssetForm(forms.ModelForm):
    """Updated form for creating and updating assets with primary IP only."""
    
    # Keep existing fields for primary IP selection
    # ip_address field continues to work as before for primary IP
    
    # Add IP type selector for primary IP
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP (from IP pool)'),
        ('manual', 'Manual IP (enter manually)'),
    ]
    
    primary_ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Primary IP Type',
        initial='managed',
        required=False
    )
    
    class Meta:
        model = Asset
        fields = [
            'asset_tag',
            'system_type',
            'hardware_serial_number',
            'manufacturer',
            'operating_system',
            'ip_address',  # For managed primary IP
            'manual_ip',   # For manual primary IP
            'particulars',
            'assigned_to',
            'team',
            'branch',
            'warranty_expiration'
        ]
        # ... existing widget configuration ...
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Existing initialization logic...
        # ... (branch filtering, team cascading, etc.) ...
        
        # For editing: Detect which IP type is set and pre-select radio button
        if self.instance and self.instance.pk:
            primary = self.instance.get_primary_ip()
            if primary:
                if primary.ip_address:
                    self.fields['primary_ip_type'].initial = 'managed'
                    self.fields['ip_address'].initial = primary.ip_address
                elif primary.manual_ip:
                    self.fields['primary_ip_type'].initial = 'manual'
                    self.fields['manual_ip'].initial = primary.manual_ip
    
    def save(self, commit=True):
        """Save asset and create primary IP association."""
        asset = super().save(commit=commit)
        
        if commit:
            with transaction.atomic():
                # Get or create primary IP association
                primary_ip_type = self.cleaned_data.get('primary_ip_type')
                
                if primary_ip_type == 'managed':
                    ip_address = self.cleaned_data.get('ip_address')
                    if ip_address:
                        # Remove old primary if exists
                        old_primary = asset.get_primary_ip()
                        if old_primary:
                            AssetIPService.remove_secondary_ip(old_primary)
                        
                        # Create new primary
                        AssetIPAddress.objects.create(
                            asset=asset,
                            ip_address=ip_address,
                            manual_ip=None,
                            is_primary=True
                        )
                        
                        # Mark IP as assigned
                        ip_address.is_assigned = True
                        ip_address.assigned_to_asset = asset
                        ip_address.save()
                
                elif primary_ip_type == 'manual':
                    manual_ip = self.cleaned_data.get('manual_ip')
                    if manual_ip:
                        # Remove old primary if exists
                        old_primary = asset.get_primary_ip()
                        if old_primary:
                            if old_primary.ip_address:
                                # Release managed IP
                                old_primary.ip_address.is_assigned = False
                                old_primary.ip_address.assigned_to_asset = None
                                old_primary.ip_address.save()
                            old_primary.delete()
                        
                        # Create new primary
                        AssetIPAddress.objects.create(
                            asset=asset,
                            ip_address=None,
                            manual_ip=manual_ip,
                            is_primary=True
                        )
        
        return asset
```


#### ReassignmentForm Updates

```python
class ReassignmentForm(forms.Form):
    """Updated form for reassigning freed systems with multiple IP support."""
    
    # ... existing fields (assigned_to, team selectors, etc.) ...
    
    # Update IP fields to support primary IP type selection
    primary_ip_type = forms.ChoiceField(
        choices=[
            ('managed', 'Managed IP (from IP pool)'),
            ('manual', 'Manual IP (enter manually)'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Primary IP Type',
        initial='manual',
        required=True
    )
    
    ip_address = forms.ModelChoiceField(
        queryset=IPAddress.objects.none(),
        required=False,
        empty_label="Select IP Address",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_managed_ip'}),
        label='Managed IP Address'
    )
    
    manual_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_manual_ip_input',
            'placeholder': 'e.g., 192.168.1.100'
        }),
        label='Manual IP Address'
    )
    
    # ... other existing fields ...
    
    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        
        # Populate managed IP dropdown
        available_ips = get_filtered_free_ips()
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [
            (ip.pk, str(ip.address)) for ip in available_ips
        ]
        
        # Pre-populate with current primary IP if exists
        if asset:
            primary = asset.get_primary_ip()
            if primary:
                if primary.ip_address:
                    self.fields['primary_ip_type'].initial = 'managed'
                    # Include current IP in queryset for updates
                    self.fields['ip_address'].queryset = IPAddress.objects.filter(
                        models.Q(is_assigned=False) | models.Q(pk=primary.ip_address.pk)
                    )
                    self.fields['ip_address'].initial = primary.ip_address
                elif primary.manual_ip:
                    self.fields['primary_ip_type'].initial = 'manual'
                    self.fields['manual_ip'].initial = primary.manual_ip
            
            # ... existing team and other field initialization ...
    
    def clean(self):
        """Validate primary IP selection based on type."""
        cleaned_data = super().clean()
        primary_ip_type = cleaned_data.get('primary_ip_type')
        ip_address = cleaned_data.get('ip_address')
        manual_ip = cleaned_data.get('manual_ip')
        
        if primary_ip_type == 'managed':
            if not ip_address:
                raise forms.ValidationError("Please select a managed IP address for the primary IP.")
            cleaned_data['manual_ip'] = None
        elif primary_ip_type == 'manual':
            if not manual_ip:
                raise forms.ValidationError("Please enter a manual IP address for the primary IP.")
            cleaned_data['ip_address'] = None
        
        # ... existing team validation ...
        
        return cleaned_data
```


### Views

#### AddSecondaryIPView

```python
class AddSecondaryIPView(AdminRequiredMixin, View):
    """View for adding secondary IP addresses to assets."""
    
    def get(self, request, pk):
        """Display form to add secondary IP."""
        asset = get_object_or_404(Asset, pk=pk)
        form = SecondaryIPForm(asset=asset)
        
        context = {
            'asset': asset,
            'form': form,
            'primary_ip': asset.get_primary_ip(),
            'secondary_ips': asset.get_secondary_ips(),
        }
        return render(request, 'assets/add_secondary_ip.html', context)
    
    def post(self, request, pk):
        """Process secondary IP addition."""
        asset = get_object_or_404(Asset, pk=pk)
        form = SecondaryIPForm(request.POST, asset=asset)
        
        if form.is_valid():
            try:
                ip_type = form.cleaned_data['ip_type']
                
                if ip_type == 'managed':
                    ip_address = form.cleaned_data['ip_address']
                    AssetIPService.add_secondary_ip(
                        asset=asset,
                        ip_address=ip_address,
                        user=request.user
                    )
                    messages.success(request, f'Secondary IP {ip_address.address} added successfully.')
                else:
                    manual_ip = form.cleaned_data['manual_ip']
                    AssetIPService.add_secondary_ip(
                        asset=asset,
                        manual_ip=manual_ip,
                        user=request.user
                    )
                    messages.success(request, f'Secondary IP {manual_ip} added successfully.')
                
                return redirect('asset_detail', pk=asset.pk)
            
            except ValidationError as e:
                messages.error(request, str(e))
                return self.get(request, pk)
        
        # Form invalid
        context = {
            'asset': asset,
            'form': form,
            'primary_ip': asset.get_primary_ip(),
            'secondary_ips': asset.get_secondary_ips(),
        }
        return render(request, 'assets/add_secondary_ip.html', context)


class RemoveSecondaryIPView(AdminRequiredMixin, View):
    """View for removing secondary IP addresses from assets."""
    
    def post(self, request, pk):
        """Process secondary IP removal."""
        asset_ip = get_object_or_404(AssetIPAddress, pk=pk)
        asset = asset_ip.asset
        
        try:
            ip_display = asset_ip.get_ip_display()
            AssetIPService.remove_secondary_ip(asset_ip, user=request.user)
            messages.success(request, f'Secondary IP {ip_display} removed successfully.')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('asset_detail', pk=asset.pk)


class SetPrimaryIPView(AdminRequiredMixin, View):
    """View for changing which IP is the primary IP."""
    
    def post(self, request, pk):
        """Process primary IP change."""
        asset_ip = get_object_or_404(AssetIPAddress, pk=pk)
        asset = asset_ip.asset
        
        try:
            AssetIPService.set_primary_ip(asset, asset_ip, user=request.user)
            ip_display = asset_ip.get_ip_display()
            messages.success(request, f'IP {ip_display} is now the primary IP.')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('asset_detail', pk=asset.pk)
```


## Data Models

### AssetIPAddress Table Schema

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| asset_id | INTEGER | FOREIGN KEY (Asset), NOT NULL, ON DELETE CASCADE, INDEX | Asset this IP is assigned to |
| ip_address_id | INTEGER | FOREIGN KEY (IPAddress), NULL, ON DELETE PROTECT, INDEX | Managed IP from IP pool (nullable) |
| manual_ip | VARCHAR(45) | NULL | Manual IP address (nullable) |
| is_primary | BOOLEAN | NOT NULL, DEFAULT FALSE, INDEX | True if this is the primary IP |
| created_at | DATETIME | NOT NULL | Creation timestamp |

### Relationships

- **AssetIPAddress → Asset**: Many-to-One (many IPs can belong to one asset)
- **AssetIPAddress → IPAddress**: Many-to-One (many asset associations can reference one managed IP - but is_assigned prevents actual duplicates)
- **Asset ← AssetIPAddress**: One-to-Many (asset can have multiple IP associations)
- **IPAddress ← AssetIPAddress**: One-to-Many (IPAddress can have multiple asset associations, but only one active due to is_assigned check)

### Database Constraints

1. **Check Constraint**: `asset_ip_exactly_one_ip_type`
   - Ensures exactly one of `ip_address_id` or `manual_ip` is set
   - `(ip_address_id IS NOT NULL AND manual_ip IS NULL) OR (ip_address_id IS NULL AND manual_ip IS NOT NULL)`

2. **Foreign Key Constraints**:
   - `asset_id` → Asset.serial_number with CASCADE delete
   - `ip_address_id` → IPAddress.id with PROTECT delete

### Database Indexes

- Primary key index on `id`
- Composite index on `(asset_id, is_primary)` for efficiently finding primary IP
- Index on `ip_address_id` for efficient IP lookup
- Index on `is_primary` for filtering queries

### Migration Strategy

The migration from single IP to multiple IPs follows this approach:

1. **Phase 1**: Create AssetIPAddress model (additive change, no breaking changes)
2. **Phase 2**: Migrate existing data using data migration
3. **Phase 3**: Update views and forms to use AssetIPAddress
4. **Phase 4** (Future): Deprecate and remove Asset.ip_address and Asset.manual_ip fields

**Data Migration Script**:
```python
def migrate_legacy_ips(apps, schema_editor):
    """Migrate existing Asset.ip_address and Asset.manual_ip to AssetIPAddress."""
    Asset = apps.get_model('assets', 'Asset')
    AssetIPAddress = apps.get_model('assets', 'AssetIPAddress')
    
    for asset in Asset.objects.all():
        # Skip if already migrated
        if AssetIPAddress.objects.filter(asset=asset, is_primary=True).exists():
            continue
        
        # Migrate managed IP
        if asset.ip_address_id:
            AssetIPAddress.objects.create(
                asset=asset,
                ip_address_id=asset.ip_address_id,
                manual_ip=None,
                is_primary=True
            )
        # Migrate manual IP
        elif asset.manual_ip:
            AssetIPAddress.objects.create(
                asset=asset,
                ip_address_id=None,
                manual_ip=asset.manual_ip,
                is_primary=True
            )
```


## Error Handling

### Validation Errors

The system shall handle the following validation errors gracefully:

1. **IP Already Assigned Conflict**
   - When: Attempting to add a managed IP that is already assigned to another asset
   - Error: `ValidationError("IP {address} is already assigned.")`
   - User Feedback: Display error message on form
   - Recovery: User selects a different available IP

2. **Duplicate IP on Same Asset**
   - When: Attempting to add an IP that is already assigned to this asset (as primary or secondary)
   - Error: `ValidationError("This IP is already assigned to this asset.")`
   - User Feedback: Display error message on form
   - Recovery: User selects a different IP

3. **Both IP Types Provided**
   - When: User provides both managed IP and manual IP in the same operation
   - Error: `ValidationError("Cannot provide both ip_address and manual_ip.")`
   - User Feedback: Display error message on form
   - Recovery: User selects only one IP type

4. **No IP Type Provided**
   - When: User submits form without selecting managed IP or entering manual IP
   - Error: `ValidationError("Either ip_address or manual_ip must be provided.")`
   - User Feedback: Display error message on form
   - Recovery: User provides one IP type

5. **Invalid IP Format**
   - When: Manual IP does not conform to IPv4 format
   - Error: `ValidationError("Enter a valid IPv4 address.")`
   - User Feedback: Display error message on form field
   - Recovery: User enters valid IP address (XXX.XXX.XXX.XXX)

6. **Removing Primary IP Without Replacement**
   - When: Attempting to remove the primary IP when it's the only IP or without designating a new primary
   - Error: `ValidationError("Cannot remove primary IP. Designate a secondary IP as primary first.")`
   - User Feedback: Display error message
   - Recovery: User designates a secondary IP as primary, then removes the old primary

7. **Asset Has No IP Addresses**
   - When: Asset has no IP addresses when system expects at least one
   - Error: `ValidationError("Asset must have at least one IP address.")`
   - User Feedback: Display error message
   - Recovery: User adds an IP address before proceeding

8. **Invalid Primary IP Assignment**
   - When: Attempting to set an AssetIPAddress as primary when it belongs to a different asset
   - Error: `ValidationError("The selected IP does not belong to this asset.")`
   - User Feedback: Display error message
   - Recovery: System prevents operation; should not occur in normal usage


### Database Errors

1. **Integrity Constraint Violation (Check Constraint)**
   - When: Database-level enforcement fails (both ip_address and manual_ip are set or both are null)
   - Handling: Catch IntegrityError, convert to ValidationError
   - Rollback: Transaction automatically rolled back via `transaction.atomic()`
   - User Feedback: "Invalid IP configuration. Please contact support."

2. **Foreign Key Constraint Violation**
   - When: Attempting to delete IPAddress that has AssetIPAddress associations
   - Prevention: Use PROTECT on_delete on AssetIPAddress.ip_address ForeignKey
   - Error: `ProtectedError`
   - User Feedback: "Cannot delete IP address - it is assigned to one or more assets"

3. **Cascade Delete**
   - When: Asset is deleted
   - Behavior: All AssetIPAddress records are automatically deleted via CASCADE
   - Side Effect: Managed IPs must be marked as unassigned (handled in post_delete signal)

### Transaction Management

All create, update, and delete operations use Django's `transaction.atomic()` to ensure:
- All database changes succeed or all are rolled back
- IP assignment state (is_assigned flag) is consistent with AssetIPAddress existence
- No partial state changes on error
- Primary IP designation changes are atomic (old primary demoted and new primary promoted together)

### Signal Handlers

```python
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=AssetIPAddress)
def release_managed_ip_on_delete(sender, instance, **kwargs):
    """
    When an AssetIPAddress is deleted, mark the managed IP as unassigned.
    This handles both explicit deletion and cascade deletion from Asset.
    """
    if instance.ip_address:
        instance.ip_address.is_assigned = False
        instance.ip_address.assigned_to_asset = None
        instance.ip_address.freed_date = timezone.now()
        instance.ip_address.save()
```


## Testing Strategy

### Testing Approach Assessment

This feature contains a mix of components with different testing needs:

**Suitable for Property-Based Testing**:
- Business logic in AssetIPService (IP assignment, validation, conflict detection)
- Form validation logic (SecondaryIPForm, AssetForm updates)
- Asset model methods (get_primary_ip, get_secondary_ips, etc.)
- IP conflict prevention logic

**NOT Suitable for Property-Based Testing**:
- Database schema creation (AssetIPAddress model)
- Data migration scripts (use integration tests with test fixtures)
- View rendering (use integration tests)
- Signal handlers (use integration tests)

**Testing Strategy**: Dual approach using both property-based tests for business logic and integration tests for database/migration/view components.

### Dual Testing Approach

- **Unit tests**: Verify specific examples, edge cases, and error conditions
- **Property tests**: Verify universal properties across randomized inputs for business logic
- **Integration tests**: Verify database operations, migrations, and end-to-end flows

### Property-Based Testing

Property-based tests will be implemented using **Hypothesis** (Python's property-based testing library). Each correctness property will be implemented as a property-based test with minimum 100 iterations.

**Test Configuration**:
```python
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.django import from_model

@settings(max_examples=100)
@given(
    asset=from_model(Asset),
    ip_type=st.sampled_from(['managed', 'manual']),
    # ... other strategies
)
def test_property_X(asset, ip_type, ...):
    """Feature: multiple-ip-addresses, Property X: [property text]"""
    # Test implementation
```

**Property Test Tags**: Each property test must include a comment tag:
```python
"""Feature: multiple-ip-addresses, Property 1: Primary IP uniqueness"""
```


### Unit Testing

Unit tests will focus on:

1. **Specific Examples**:
   - Creating asset with one managed primary IP
   - Adding a second managed IP as secondary
   - Adding a manual IP as secondary
   - Removing a specific secondary IP

2. **Edge Cases**:
   - Asset with only primary IP (zero secondaries)
   - Asset with maximum practical secondaries (e.g., 10)
   - Manual IP at boundary values (0.0.0.0, 255.255.255.255)
   - IP address in edge of filtered ranges (192.168.10.1, 192.168.70.254)

3. **Error Conditions**:
   - Attempting to add already-assigned managed IP
   - Attempting to remove primary IP when secondaries exist
   - Providing both managed and manual IP in same operation
   - Invalid IPv4 format for manual IP

4. **Integration Points**:
   - Data migration from legacy single-IP model
   - Form rendering with IP lists
   - Signal handler releasing IPs on deletion

### Test Coverage Goals

- **Model tests**: 100% coverage of AssetIPAddress model and Asset model extensions
- **Service tests**: 100% coverage of AssetIPService methods
- **View tests**: Coverage of all CRUD operations for secondary IPs
- **Form tests**: Coverage of validation logic for SecondaryIPForm and form updates
- **Integration tests**: Coverage of data migration and end-to-end workflows


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Primary IP Uniqueness

*For any* asset at any point in time, the asset SHALL have exactly one IP address marked as primary, accessible via get_primary_ip().

**Validates: Requirements 1.4, 8.1**

### Property 2: Managed IP Assignment State

*For any* managed IP address assigned to an asset (as either primary or secondary), the IPAddress record SHALL have is_assigned set to True and assigned_to_asset pointing to that asset.

**Validates: Requirements 1.2, 1.3, 1.6, 2.6**

### Property 3: Managed IP Release State

*For any* managed IP address that is removed from an asset, the IPAddress record SHALL have is_assigned set to False, assigned_to_asset set to None, and freed_date populated with the removal timestamp.

**Validates: Requirements 1.7, 3.6**

### Property 4: Available IP Filtering

*For any* asset form displaying available IPs for selection, the dropdown SHALL contain only IPAddress records where is_assigned is False AND the address matches one of the patterns: 192.168.10.x, 192.168.11.x, 192.168.50.x, or 192.168.70.x.

**Validates: Requirements 2.2, 2.3, 2.4**

### Property 5: Secondary IP Association Persistence

*For any* valid secondary IP assignment (managed or manual), creating the association SHALL result in an AssetIPAddress record existing in the database with is_primary=False and the correct asset_id and IP values.

**Validates: Requirements 2.5**


### Property 6: Multiple Secondary IPs Support

*For any* asset and sequence of secondary IP additions (managed or manual), each successful addition SHALL result in a distinct AssetIPAddress record, and all records SHALL be retrievable via get_secondary_ips().

**Validates: Requirements 2.7**

### Property 7: Secondary IP Removal

*For any* secondary IP (is_primary=False) on any asset, invoking remove_secondary_ip() SHALL result in the AssetIPAddress record being deleted from the database.

**Validates: Requirements 3.5**

### Property 8: Primary IP Removal Protection

*For any* asset with one or more secondary IPs, attempting to remove the primary IP via remove_secondary_ip() SHALL raise a ValidationError and leave all IP associations unchanged.

**Validates: Requirements 3.7**

### Property 9: Manual IP IPv4 Validation

*For any* string value provided as a manual_ip, the system SHALL accept it if and only if it conforms to valid IPv4 format (XXX.XXX.XXX.XXX where each XXX is 0-255).

**Validates: Requirements 4.2, 4.3**

### Property 10: Manual IP Isolation from Managed Pool

*For any* manual IP address saved as a secondary IP on any asset, the is_assigned state of all managed IPAddress records SHALL remain unchanged.

**Validates: Requirements 4.4**

### Property 11: Mixed IP Type Support

*For any* asset, adding a combination of managed and manual IP addresses as secondary IPs SHALL succeed, and get_all_ips() SHALL return all associations regardless of type.

**Validates: Requirements 4.6**

### Property 12: Managed IP Conflict Prevention

*For any* managed IPAddress where is_assigned is True, attempting to assign that IP to a different asset (as primary or secondary) SHALL raise a ValidationError.

**Validates: Requirements 5.1, 5.2**


### Property 13: IP Reassignment After Release

*For any* managed IPAddress that is unassigned from asset A (resulting in is_assigned=False), subsequently assigning that same IP to asset B SHALL succeed and set is_assigned=True with assigned_to_asset pointing to asset B.

**Validates: Requirements 5.3**

### Property 14: Manual IP No Conflict Checking

*For any* manual IP string value, assigning it as a secondary IP SHALL NOT check the managed IPAddress pool for conflicts, and SHALL succeed even if a managed IP with the same address exists and is assigned.

**Validates: Requirements 5.4**

### Property 15: Manual IP Duplicate Permission

*For any* manual IP string value, assigning it to multiple different assets simultaneously SHALL succeed, resulting in multiple AssetIPAddress records with the same manual_ip value but different asset_id values.

**Validates: Requirements 5.5**

### Property 16: Freed Asset IP Preservation

*For any* asset with multiple IP addresses that is transitioned to freed status, all AssetIPAddress associations SHALL remain in the database with their asset_id and IP values unchanged.

**Validates: Requirements 6.1**

### Property 17: Reassignment Secondary Addition

*For any* freed asset being reassigned, adding a new secondary IP during the reassignment process SHALL succeed and create a new AssetIPAddress record.

**Validates: Requirements 6.3**

### Property 18: Reassignment Secondary Removal

*For any* freed asset being reassigned that has secondary IPs, removing a secondary IP during the reassignment process SHALL succeed and delete the AssetIPAddress record.

**Validates: Requirements 6.4**

### Property 19: Reassignment Primary Change

*For any* freed asset being reassigned with multiple IPs, changing which IP is primary SHALL update the is_primary flags such that exactly one AssetIPAddress has is_primary=True.

**Validates: Requirements 6.5**


### Property 20: Scrapping Releases Managed IPs

*For any* asset transitioned to scrapped status, all managed IPAddress records associated with that asset (where ip_address is not None) SHALL have is_assigned set to False and assigned_to_asset set to None.

**Validates: Requirements 6.6**

### Property 21: Asset Primary IP Requirement

*For any* asset in the system at any point in time, get_primary_ip() SHALL return a non-None AssetIPAddress instance.

**Validates: Requirements 8.1**

### Property 22: No Duplicate IPs Per Asset

*For any* asset and any IP address (managed or manual), at most one AssetIPAddress record SHALL exist linking that asset to that IP address.

**Validates: Requirements 8.2, 8.4**

