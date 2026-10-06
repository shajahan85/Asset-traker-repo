"""
Django forms for asset management.
"""
from django import forms
from django.db import models
from django.forms import inlineformset_factory
from assets.models import Asset, OperatingSystem, Team, IPAddress, NetworkDevice, AssetIPAddress


def get_filtered_free_ips(include_current_ip_id=None, limit=30):
    """
    Get free IPs filtered to specific ranges for easier selection.
    Returns first 30 IPs without sorting for maximum performance.
    
    Args:
        include_current_ip_id: Optional IP ID to include even if assigned (for editing)
        limit: Maximum number of IPs to return (default: 30 for fast loading)
    
    Returns:
        QuerySet of IPAddress objects filtered to common ranges
    """
    # Define the allowed IP ranges
    allowed_ranges = ['192.168.10.', '192.168.11.', '192.168.50.', '192.168.70.']
    
    # Build query to filter by ranges
    range_query = models.Q()
    for range_prefix in allowed_ranges:
        range_query |= models.Q(address__startswith=range_prefix)
    
    # Get free IPs in the specified ranges
    if include_current_ip_id:
        # Include current IP and free IPs in specified ranges
        ips = IPAddress.objects.filter(
            (models.Q(is_assigned=False) & range_query) | 
            models.Q(pk=include_current_ip_id)
        )
    else:
        # Only free IPs in specified ranges
        ips = IPAddress.objects.filter(
            is_assigned=False
        ).filter(range_query)
    
    # Return limited queryset WITHOUT sorting - fastest possible
    # Order by ID which is already indexed
    return ips.only('id', 'address').order_by('id')[:limit]


class HierarchicalTeamChoiceField(forms.ModelChoiceField):
    """Custom form field for displaying teams hierarchically."""
    
    def __init__(self, *args, **kwargs):
        kwargs['queryset'] = Team.objects.get_hierarchy()
        super().__init__(*args, **kwargs)
    
    def label_from_instance(self, obj):
        """Return label with hierarchy indentation."""
        if obj.parent:
            return f"  └─ {obj.name}"
        return obj.name


class AssetForm(forms.ModelForm):
    """Form for creating and updating assets."""
    
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP (from IP pool)'),
        ('manual', 'Manual IP (enter manually)'),
    ]
    
    primary_ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='IP Address',
        initial='managed',
        required=False
    )
    
    parent_team = forms.ModelChoiceField(
        queryset=Team.objects.get_parent_teams(),
        required=False,
        empty_label="Select Team",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_parent_team',
            'onchange': 'handleParentTeamChange(this.value)'
        }),
        label='Team'
    )
    
    sub_team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=False,
        empty_label="Select Sub-Team",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_sub_team',
            'style': 'display:none;'
        }),
        label='Sub-Team'
    )
    
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )
    
    # Email notification control
    send_notification = forms.BooleanField(
        required=False,
        initial=True,
        label='Send Email Notification',
        help_text='Uncheck to prevent email notification for this save',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_send_notification'
        })
    )
    
    
    class Meta:
        model = Asset
        fields = [
            'asset_tag',
            'system_type',
            'hardware_serial_number',
            'manufacturer',
            'operating_system',
            'ip_address',
            'manual_ip',
            'particulars',
            'assigned_to',
            'employee_code',
            'team',
            'branch',
            'warranty_expiration'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique asset tag'
            }),
            'system_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'hardware_serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'id_hardware_serial_number',
                'placeholder': 'Enter hardware serial number'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dell, HP, Lenovo'
            }),
            'operating_system': forms.Select(attrs={'class': 'form-control'}),
            'ip_address': forms.Select(attrs={'class': 'form-control'}),
            'manual_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 192.168.1.100'
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter detailed information about the asset'
            }),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter person name'
            }),
            'employee_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter employee code'
            }),
            'branch': forms.Select(attrs={'class': 'form-control'}),
            'warranty_expiration': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            })
        }
        labels = {
            'asset_tag': 'Asset Tag',
            'system_type': 'System Type',
            'hardware_serial_number': 'Hardware Serial Number',
            'manufacturer': 'Manufacturer',
            'operating_system': 'Operating System',
            'ip_address': 'IP Address (Managed)',
            'manual_ip': 'IP Address (Manual)',
            'particulars': 'Particulars',
            'assigned_to': 'Assigned To',
            'employee_code': 'Employee Code',
            'branch': 'Branch',
            'team': 'Team',
            'warranty_expiration': 'Warranty Expiration'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate branch dropdown
        from assets.models import Branch
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True)
        self.fields['branch'].empty_label = "Select Branch"
        self.fields['branch'].required = True
        
        # Add branch change handler to branch widget
        self.fields['branch'].widget.attrs.update({
            'onchange': 'handleBranchChange(this.value)'
        })
        
        # Populate operating system dropdown
        self.fields['operating_system'].queryset = OperatingSystem.objects.all()
        self.fields['operating_system'].empty_label = "Select Operating System"
        
        # Hardware serial number is not required by default (will be validated in clean())
        self.fields['hardware_serial_number'].required = False
        
        # Filter teams by branch
        current_branch = None
        
        # For editing existing assets
        if self.instance and self.instance.pk:
            current_branch = self.instance.branch
            
            # Detect and pre-select IP type for editing
            primary_ip = self.instance.get_primary_ip()
            if primary_ip:
                if primary_ip.ip_address:
                    self.fields['primary_ip_type'].initial = 'managed'
                    # Note: Initial value for ip_address field will be set later when populating dropdown
                elif primary_ip.manual_ip:
                    self.fields['primary_ip_type'].initial = 'manual'
                    self.fields['manual_ip'].initial = primary_ip.manual_ip
            
            # Set up team dropdowns based on current team
            if self.instance.team:
                current_team = self.instance.team
                if current_team.parent:
                    # Asset is assigned to a sub-team
                    self.fields['parent_team'].queryset = Team.objects.get_parent_teams(branch=current_branch)
                    self.fields['parent_team'].initial = current_team.parent
                    self.fields['sub_team'].queryset = current_team.parent.sub_teams.filter(branch=current_branch)
                    self.fields['sub_team'].initial = current_team
                    self.fields['sub_team'].widget.attrs['style'] = ''
                else:
                    # Asset is assigned to a parent team
                    self.fields['parent_team'].queryset = Team.objects.get_parent_teams(branch=current_branch)
                    self.fields['parent_team'].initial = current_team
                self.fields['team'].initial = current_team
        
        # For form submission with POST data
        if self.data:
            try:
                branch_id = self.data.get('branch')
                if branch_id:
                    from assets.models import Branch
                    current_branch = Branch.objects.get(pk=branch_id)
                    self.fields['parent_team'].queryset = Team.objects.get_parent_teams(branch=current_branch)
                    
                    parent_team_id = self.data.get('parent_team')
                    if parent_team_id:
                        parent_team = Team.objects.get(pk=parent_team_id)
                        # Ensure parent team belongs to selected branch
                        if parent_team.branch_id == current_branch.id:
                            self.fields['sub_team'].queryset = parent_team.sub_teams.filter(branch=current_branch)
            except (ValueError, Branch.DoesNotExist, Team.DoesNotExist):
                pass
        
        # Set empty queryset if no branch selected
        if not current_branch and not self.data.get('branch'):
            self.fields['parent_team'].queryset = Team.objects.none()
            self.fields['sub_team'].queryset = Team.objects.none()
        
        # Populate IP address dropdown with only available IPs from specific ranges
        # For updates, include the currently assigned IP from AssetIPAddress model
        current_managed_ip_id = None
        
        if self.instance and self.instance.pk:
            primary_ip = self.instance.get_primary_ip()
            if primary_ip and primary_ip.ip_address:
                current_managed_ip_id = primary_ip.ip_address.pk
                # Set initial value to the IP's primary key (not the object)
                self.fields['ip_address'].initial = primary_ip.ip_address.pk
        
        # Get available IPs for primary dropdown
        if current_managed_ip_id:
            available_ips = get_filtered_free_ips(include_current_ip_id=current_managed_ip_id)
        else:
            # Only show filtered free IPs for new assets
            available_ips = get_filtered_free_ips()
        
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [(ip.pk, str(ip.address)) for ip in available_ips]
        self.fields['ip_address'].required = False
        self.fields['manual_ip'].required = False
        
        # Set required fields
        self.fields['asset_tag'].required = True
        self.fields['system_type'].required = True
        self.fields['operating_system'].required = False  # Made optional to allow manual entry
        self.fields['assigned_to'].required = False
        self.fields['particulars'].required = False
        self.fields['warranty_expiration'].required = False
        self.fields['parent_team'].required = False
        self.fields['sub_team'].required = False
    
    def clean(self):
        """Custom validation to set the team field based on parent_team and sub_team."""
        cleaned_data = super().clean()
        parent_team = cleaned_data.get('parent_team')
        sub_team = cleaned_data.get('sub_team')
        system_type = cleaned_data.get('system_type')
        hardware_serial_number = cleaned_data.get('hardware_serial_number')
        
        # Validate hardware serial number for Laptop and All-in-One PC
        if system_type in ['Laptop', 'All-in-One PC']:
            if not hardware_serial_number or not hardware_serial_number.strip():
                self.add_error('hardware_serial_number', 'Hardware serial number is required for Laptop and All-in-One PC.')
        
        # Determine which team to assign
        if sub_team:
            cleaned_data['team'] = sub_team
        elif parent_team:
            cleaned_data['team'] = parent_team
        else:
            cleaned_data['team'] = None
        
        return cleaned_data
    
    def clean_asset_tag(self):
        """Validate asset tag uniqueness."""
        asset_tag = self.cleaned_data.get('asset_tag')
        
        # Check if asset tag already exists (excluding current instance for updates)
        existing = Asset.objects.filter(asset_tag=asset_tag)
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise forms.ValidationError("Asset tag already exists. Please use a unique asset tag.")
        
        return asset_tag
    
    def save(self, commit=True):
        """Save asset and create primary IP association."""
        from django.db import transaction
        from assets.models import AssetIPAddress
        
        asset = super().save(commit=commit)
        
        if commit:
            with transaction.atomic():
                # Get or update primary IP association
                primary_ip_type = self.cleaned_data.get('primary_ip_type')
                
                if primary_ip_type == 'managed':
                    ip_address = self.cleaned_data.get('ip_address')
                    if ip_address:
                        # Get old primary if exists
                        old_primary = asset.get_primary_ip()
                        
                        # Check if the primary IP is changing
                        if old_primary and old_primary.ip_address != ip_address:
                            # Release old managed IP if exists
                            if old_primary.ip_address:
                                old_primary.ip_address.is_assigned = False
                                old_primary.ip_address.assigned_to_asset = None
                                old_primary.ip_address.save()
                            # Remove old primary association
                            old_primary.delete()
                            old_primary = None
                        
                        # Create new primary if doesn't exist or was removed
                        if not old_primary:
                            AssetIPAddress.objects.create(
                                asset=asset,
                                ip_address=ip_address,
                                manual_ip=None,
                                is_primary=True
                            )
                        
                        # Mark new IP as assigned
                        ip_address.is_assigned = True
                        ip_address.assigned_to_asset = asset
                        ip_address.save()
                
                elif primary_ip_type == 'manual':
                    manual_ip = self.cleaned_data.get('manual_ip')
                    if manual_ip:
                        # Get old primary if exists
                        old_primary = asset.get_primary_ip()
                        
                        # Check if the primary IP is changing
                        if old_primary and old_primary.manual_ip != manual_ip:
                            # Release old managed IP if exists
                            if old_primary.ip_address:
                                old_primary.ip_address.is_assigned = False
                                old_primary.ip_address.assigned_to_asset = None
                                old_primary.ip_address.save()
                            # Remove old primary association
                            old_primary.delete()
                            old_primary = None
                        
                        # Create new primary if doesn't exist or was removed
                        if not old_primary:
                            AssetIPAddress.objects.create(
                                asset=asset,
                                ip_address=None,
                                manual_ip=manual_ip,
                                is_primary=True
                            )
        
        return asset


class FreeAssetForm(forms.Form):
    """Form for freeing assets with password confirmation."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        label='Password',
        required=True,
        help_text='Enter your admin password to confirm freeing this asset'
    )
    
    def clean_password(self):
        """Validate that password is provided."""
        password = self.cleaned_data.get('password')
        
        if not password:
            raise forms.ValidationError("Password is required to free an asset.")
        
        return password


class ReassignmentForm(forms.Form):
    """Form for reassigning freed systems back to active status."""
    
    assigned_to = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter person name'
        }),
        label='Assigned To'
    )
    
    parent_team = forms.ModelChoiceField(
        queryset=Team.objects.none(),  # Will be populated in __init__ based on asset branch
        required=False,
        empty_label="Select Team",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_parent_team',
            'onchange': 'handleParentTeamChange(this.value)'
        }),
        label='Team'
    )
    
    sub_team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        required=False,
        empty_label="Select Sub-Team",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_sub_team',
            'style': 'display:none;'
        }),
        label='Sub-Team'
    )
    
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=True,
        widget=forms.HiddenInput()
    )
    
    manual_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_manual_ip',
            'placeholder': 'e.g., 192.168.1.100'
        }),
        label='IP Address'
    )
    
    operating_system = forms.ModelChoiceField(
        queryset=OperatingSystem.objects.all(),
        required=False,
        empty_label="Select Operating System",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_operating_system'
        }),
        label='Operating System'
    )
    
    os_manual_entry = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_os_manual_entry',
            'placeholder': 'Or enter OS manually'
        }),
        label='Manual OS Entry'
    )
    
    system_type = forms.ChoiceField(
        choices=Asset.SYSTEM_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_system_type'
        }),
        label='System Type'
    )
    
    manufacturer = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Dell, HP, Lenovo'
        }),
        label='Manufacturer'
    )
    
    particulars = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter detailed information about the asset'
        }),
        label='Particulars'
    )
    
    warranty_expiration = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Warranty Expiration'
    )
    
    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        
        # Filter teams by asset's branch
        asset_branch = asset.branch if asset else None
        
        if asset_branch:
            # Populate parent_team dropdown with teams from asset's branch
            self.fields['parent_team'].queryset = Team.objects.get_parent_teams(branch=asset_branch)
        else:
            # No branch, set empty queryset
            self.fields['parent_team'].queryset = Team.objects.none()
        
        # Handle team cascading dropdown - for form submission with POST data
        if self.data:
            try:
                parent_team_id = self.data.get('parent_team')
                if parent_team_id and asset_branch:
                    parent_team = Team.objects.get(pk=parent_team_id)
                    # Ensure parent team belongs to asset's branch
                    if parent_team.branch_id == asset_branch.id:
                        self.fields['sub_team'].queryset = parent_team.sub_teams.filter(branch=asset_branch)
                    else:
                        self.fields['sub_team'].queryset = Team.objects.none()
            except (ValueError, Team.DoesNotExist):
                pass
        
        # Pre-populate fields with current asset values if asset provided
        if asset:
            self.fields['assigned_to'].initial = asset.assigned_to or ''
            self.fields['system_type'].initial = asset.system_type
            self.fields['manufacturer'].initial = asset.manufacturer or ''
            self.fields['particulars'].initial = asset.particulars or ''
            self.fields['warranty_expiration'].initial = asset.warranty_expiration
            
            if asset.operating_system:
                self.fields['operating_system'].initial = asset.operating_system
            
            # Pre-populate team fields with asset's current team
            if asset.team and asset_branch:
                if asset.team.parent:
                    # Asset is assigned to a sub-team
                    self.fields['parent_team'].initial = asset.team.parent
                    self.fields['sub_team'].queryset = asset.team.parent.sub_teams.filter(branch=asset_branch)
                    self.fields['sub_team'].initial = asset.team
                    self.fields['sub_team'].widget.attrs['style'] = ''
                else:
                    # Asset is assigned to a parent team
                    self.fields['parent_team'].initial = asset.team
                self.fields['team'].initial = asset.team
            
            if asset.ip_address:
                # Include current IP in queryset
                self.fields['ip_address'].queryset = IPAddress.objects.filter(
                    models.Q(is_assigned=False) | models.Q(pk=asset.ip_address.pk)
                )
                self.fields['ip_address'].initial = asset.ip_address
            elif asset.manual_ip:
                self.fields['manual_ip'].initial = asset.manual_ip
    
    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        parent_team = cleaned_data.get('parent_team')
        sub_team = cleaned_data.get('sub_team')
        manual_ip = cleaned_data.get('manual_ip')
        
        # Manual IP is now required (handled by field definition)
        # No need for additional IP validation since we only have one IP field
        
        # Determine which team to assign
        if sub_team:
            cleaned_data['team'] = sub_team
        elif parent_team:
            cleaned_data['team'] = parent_team
        else:
            raise forms.ValidationError("Please select a team.")
        
        return cleaned_data
    
    def clean_manual_ip(self):
        """Validate manual IP format."""
        manual_ip = self.cleaned_data.get('manual_ip')
        
        if manual_ip:
            # GenericIPAddressField already validates IPv4 format
            # Additional validation can be added here if needed
            pass
        
        return manual_ip


class AttachmentForm(forms.Form):
    """Form for uploading attachments with size and type validation."""
    
    file = forms.FileField(
        label='File',
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.jpg,.jpeg,.png,.gif,.bmp,.doc,.docx,.xls,.xlsx,.txt,.zip'
        }),
        help_text='Maximum file size: 10MB. Allowed types: PDF, images (JPG, PNG, GIF, BMP), documents (DOC, DOCX, XLS, XLSX, TXT, ZIP)'
    )
    
    # File validation constants (matching AttachmentService)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes
    ALLOWED_EXTENSIONS = {
        'pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp',
        'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip'
    }
    
    def clean_file(self):
        """Validate file size and type."""
        import os
        
        file = self.cleaned_data.get('file')
        
        if not file:
            raise forms.ValidationError("No file was uploaded.")
        
        # Validate file size
        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                f'File size exceeds the maximum limit of {self.MAX_FILE_SIZE / (1024 * 1024):.0f}MB'
            )
        
        # Validate file type
        file_extension = os.path.splitext(file.name)[1][1:].lower()  # Get extension without dot
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise forms.ValidationError(
                f'File type .{file_extension} is not allowed. Allowed types: {", ".join(sorted(self.ALLOWED_EXTENSIONS))}'
            )
        
        return file



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
        current_ip_id = None
        if self.instance and self.instance.pk and self.instance.ip_address:
            current_ip_id = self.instance.ip_address.pk
        
        if current_ip_id:
            available_ips = get_filtered_free_ips(include_current_ip_id=current_ip_id)
        else:
            available_ips = get_filtered_free_ips()
        
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [(ip.pk, str(ip.address)) for ip in available_ips]
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
        
        # For existing records, if neither field changed, accept current state
        if self.instance and self.instance.pk:
            # If the form has an existing record with data, and user selected wrong ip_type
            # but the actual data is valid, auto-correct ip_type
            if ip_type == 'managed' and not ip_address and manual_ip:
                # User's radio says managed but manual_ip is filled - treat as manual
                ip_type = 'manual'
                cleaned_data['ip_type'] = 'manual'
            elif ip_type == 'manual' and not manual_ip and ip_address:
                # User's radio says manual but ip_address is filled - treat as managed
                ip_type = 'managed'
                cleaned_data['ip_type'] = 'managed'
            elif not ip_address and not manual_ip:
                # Neither provided - use existing instance data
                if self.instance.ip_address:
                    cleaned_data['ip_address'] = self.instance.ip_address
                    cleaned_data['ip_type'] = 'managed'
                    ip_type = 'managed'
                    ip_address = self.instance.ip_address
                elif self.instance.manual_ip:
                    cleaned_data['manual_ip'] = self.instance.manual_ip
                    cleaned_data['ip_type'] = 'manual'
                    ip_type = 'manual'
                    manual_ip = self.instance.manual_ip
        
        # Exactly one IP must be provided based on ip_type
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


class NetworkDeviceForm(forms.ModelForm):
    """Form for creating and updating network devices."""
    
    class Meta:
        model = NetworkDevice
        fields = ['device_type', 'device_name', 'ip_address', 'manual_ip']
        widgets = {
            'device_type': forms.Select(attrs={'class': 'form-control'}),
            'device_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter device name or description'
            }),
            'ip_address': forms.Select(attrs={'class': 'form-control'}),
            'manual_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10.0.0.50'
            }),
        }
        labels = {
            'device_type': 'Device Type',
            'device_name': 'Device Name',
            'ip_address': 'IP Address (Managed)',
            'manual_ip': 'IP Address (Manual)',
        }
        help_texts = {
            'ip_address': 'Select from managed IP addresses',
            'manual_ip': 'Or enter an IP address manually',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Show only unassigned IPs from specific ranges for easier selection
        if self.instance and self.instance.pk and self.instance.ip_address:
            # For updates, include current IP and filtered free IPs
            available_ips = get_filtered_free_ips(
                include_current_ip_id=self.instance.ip_address.pk
            )
        else:
            # For new devices, only show filtered free IPs
            available_ips = get_filtered_free_ips()
        
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x) (Optional)')] + [(ip.pk, str(ip.address)) for ip in available_ips]
        self.fields['ip_address'].required = False
        self.fields['manual_ip'].required = False
    
    def clean(self):
        """Validate that at least one IP address is provided."""
        cleaned_data = super().clean()
        ip_address = cleaned_data.get('ip_address')
        manual_ip = cleaned_data.get('manual_ip')
        
        # At least one IP must be provided
        if not ip_address and not manual_ip:
            raise forms.ValidationError('Please provide either an IP Address from the dropdown or enter a Manual IP Address.')
        
        # Both IPs cannot be provided
        if ip_address and manual_ip:
            raise forms.ValidationError('Please provide either IP Address or Manual IP, not both.')
        
        return cleaned_data


class BaseAdditionalIPFormSet(forms.BaseInlineFormSet):
    """Custom formset with duplicate IP validation and IP pool management."""
    
    def clean(self):
        """Validate that no duplicate IPs exist on the same asset."""
        if any(self.errors):
            return
        
        ip_addresses = []
        
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):
                continue
            if not form.cleaned_data:
                continue
            
            ip_address_obj = form.cleaned_data.get('ip_address')
            manual_ip = form.cleaned_data.get('manual_ip')
            
            if ip_address_obj:
                ip_string = str(ip_address_obj.address)
            elif manual_ip:
                ip_string = str(manual_ip)
            else:
                continue
            
            if ip_string in ip_addresses:
                raise forms.ValidationError(
                    "This IP is already assigned to this asset"
                )
            
            ip_addresses.append(ip_string)
        
        if self.instance and self.instance.pk:
            primary_ip = self.instance.get_primary_ip()
            if primary_ip:
                primary_ip_string = None
                if primary_ip.ip_address:
                    primary_ip_string = str(primary_ip.ip_address.address)
                elif primary_ip.manual_ip:
                    primary_ip_string = str(primary_ip.manual_ip)
                
                if primary_ip_string and primary_ip_string in ip_addresses:
                    raise forms.ValidationError(
                        "This IP is already assigned to this asset"
                    )
    
    def save(self, commit=True):
        """Save formset and mark managed IPs as assigned in IP pool."""
        instances = super().save(commit=commit)
        
        if commit:
            # Mark managed IPs as assigned for all saved instances (new and updated)
            for instance in instances:
                if instance.ip_address:
                    instance.ip_address.is_assigned = True
                    instance.ip_address.assigned_to_asset = instance.asset
                    instance.ip_address.save()
        
        return instances


# Formset for additional IP addresses
AdditionalIPFormSet = inlineformset_factory(
    Asset,
    AssetIPAddress,
    form=AdditionalIPForm,
    formset=BaseAdditionalIPFormSet,  # Use custom formset class
    extra=0,  # No extra empty forms by default (JavaScript adds them dynamically)
    can_delete=True,  # Allow removing additional IPs
    min_num=0,  # Additional IPs are optional
    max_num=10,  # Reasonable limit to prevent abuse
    validate_min=False,
    validate_max=True
)



class AccessoryForm(forms.ModelForm):
    """Form for a single accessory."""
    
    class Meta:
        from assets.models import Accessory
        model = Accessory
        fields = ['accessory_name', 'accessory_details', 'quantity']
        widgets = {
            'accessory_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Mouse, Keyboard, Monitor'
            }),
            'accessory_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brand, model, serial number (optional)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
        }
        labels = {
            'accessory_name': 'Accessory Name',
            'accessory_details': 'Details',
            'quantity': 'Quantity',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['accessory_name'].required = True
        self.fields['accessory_details'].required = False
        self.fields['quantity'].required = True


# Formset for accessories
from assets.models import Asset, Accessory

AccessoryFormSet = forms.inlineformset_factory(
    Asset,
    Accessory,
    form=AccessoryForm,
    extra=1,  # Show 1 empty form by default
    can_delete=True,
    min_num=0,
    validate_min=False,
    max_num=20,  # Maximum 20 accessories
    validate_max=True
)
