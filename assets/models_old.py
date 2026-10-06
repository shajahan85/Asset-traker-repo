from django.db import models
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class TeamManager(models.Manager):
    """Custom manager for efficient team hierarchy queries."""
    
    def get_hierarchy(self, branch=None):
        """
        Get all teams with parent relationships prefetched.
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.select_related('parent', 'branch').prefetch_related('sub_teams')
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_parent_teams(self, branch=None):
        """
        Get only parent teams (teams without a parent).
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.filter(parent__isnull=True)
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_sub_teams(self, branch=None):
        """
        Get only sub-teams (teams with a parent).
        
        Args:
            branch: Optional Branch instance to filter by
        """
        qs = self.filter(parent__isnull=False)
        if branch:
            qs = qs.filter(branch=branch)
        return qs
    
    def get_teams_by_branch(self, branch):
        """
        Get all teams for a specific branch.
        
        Args:
            branch: Branch instance
            
        Returns:
            QuerySet of teams for the branch, ordered hierarchically
        """
        return self.filter(branch=branch).select_related('parent', 'branch').order_by('parent__name', 'name')
    
    def get_hierarchical_choices(self, branch=None):
        """
        Get teams formatted for dropdown display with hierarchy.
        
        Args:
            branch: Optional Branch instance to filter by
            
        Returns:
            list of tuples: (id, display_name)
        """
        choices = []
        parent_teams = self.get_parent_teams(branch=branch).order_by('name')
        
        for parent in parent_teams:
            choices.append((parent.id, parent.name))
            sub_teams = parent.sub_teams.filter(branch=parent.branch).order_by('name') if branch else parent.sub_teams.all().order_by('name')
            for sub in sub_teams:
                choices.append((sub.id, f"  └─ {sub.name}"))
        
        return choices


class OperatingSystem(models.Model):
    """Model for storing available operating systems."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(models.Model):
    """Model for storing company branches/locations."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code for the branch (e.g., KCH, PUN, BLR, DEL)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name


class Team(models.Model):
    """Model for storing organizational teams with hierarchical support."""
    name = models.CharField(max_length=100)
    branch = models.ForeignKey(
        'Branch',
        on_delete=models.PROTECT,
        related_name='teams',
        db_index=True,
        help_text="Branch this team belongs to"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sub_teams',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TeamManager()

    class Meta:
        ordering = ['branch__name', 'name']
        indexes = [
            models.Index(fields=['branch', 'parent', 'name']),
            models.Index(fields=['parent', 'name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['branch', 'name'],
                name='unique_team_name_per_branch'
            )
        ]

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name

    def clean(self):
        """Validate team hierarchy constraints."""
        # Prevent self-reference
        if self.parent == self:
            raise ValidationError("A team cannot be its own parent.")

        # Prevent circular references
        if self.parent and self._creates_circular_reference():
            raise ValidationError("This parent assignment would create a circular reference.")

        # Prevent depth > 2 (only parent and sub-team levels)
        if self.parent and self.parent.parent:
            raise ValidationError("Teams can only be nested 2 levels deep (parent and sub-team).")

        # Prevent converting parent with children to sub-team
        if self.parent and self.sub_teams.exists():
            raise ValidationError("Cannot assign a parent to a team that has sub-teams.")
        
        # Validate branch consistency with parent
        if self.parent and self.branch_id != self.parent.branch_id:
            raise ValidationError(
                "Sub-team must belong to the same branch as its parent team."
            )
        
        # Prevent changing branch if team has sub-teams
        if self.pk and self.sub_teams.exists():
            old_instance = Team.objects.get(pk=self.pk)
            if old_instance.branch_id != self.branch_id:
                raise ValidationError(
                    "Cannot change branch - this parent team has sub-teams in the current branch."
                )

    def _creates_circular_reference(self):
        """Check if assigning this parent would create a circular reference."""
        current = self.parent
        while current:
            if current == self:
                return True
            current = current.parent
        return False

    @property
    def is_parent(self):
        """Check if this team has sub-teams."""
        return self.sub_teams.exists()

    @property
    def hierarchy_level(self):
        """Return hierarchy level: 0 for parent, 1 for sub-team."""
        return 1 if self.parent else 0

    def get_all_sub_teams(self):
        """Get all sub-teams for this team."""
        return self.sub_teams.all()

    def get_hierarchy_display(self):
        """Get display string with hierarchy context."""
        if self.parent:
            return f"  └─ {self.name}"
        return self.name
    
    def get_asset_count(self, include_sub_teams=True):
        """
        Get count of assets assigned to this team.
        
        Args:
            include_sub_teams: If True and this is a parent team, include assets from sub-teams
        
        Returns:
            int: Total count of assets
        """
        from django.db.models import Q
        
        if include_sub_teams and self.is_parent:
            # Include assets from this team and all sub-teams
            # Query from Asset model to include both direct assignments and sub-team assignments
            return Asset.objects.filter(
                Q(team=self) | Q(team__parent=self)
            ).count()
        else:
            # Only count assets directly assigned to this team
            return self.assets.count()
    
    def get_asset_statistics(self, include_sub_teams=True):
        """
        Get detailed statistics for assets assigned to this team.
        
        Args:
            include_sub_teams: If True and this is a parent team, include assets from sub-teams
        
        Returns:
            dict: Statistics including total count, by status, by system type
        """
        from django.db.models import Q, Count
        
        if include_sub_teams and self.is_parent:
            # Include assets from this team and all sub-teams
            # Query from Asset model to include both direct assignments and sub-team assignments
            assets = Asset.objects.filter(
                Q(team=self) | Q(team__parent=self)
            )
        else:
            # Only assets directly assigned to this team
            assets = self.assets.all()
        
        return {
            'total': assets.count(),
            'by_status': dict(assets.values('status').annotate(count=Count('status')).values_list('status', 'count')),
            'by_system_type': dict(assets.values('system_type').annotate(count=Count('system_type')).values_list('system_type', 'count')),
        }




class IPRange(models.Model):
    """Model for defining IP address ranges."""
    range_pattern = models.CharField(max_length=20, unique=True, help_text="e.g., 192.168.10.x")
    network_prefix = models.CharField(max_length=15, help_text="e.g., 192.168.10")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['range_pattern']

    def __str__(self):
        return self.range_pattern


class IPAddress(models.Model):
    """Model for tracking IP addresses and their assignment status."""
    address = models.GenericIPAddressField(protocol='IPv4', unique=True, validators=[validate_ipv4_address])
    ip_range = models.ForeignKey(IPRange, on_delete=models.CASCADE, related_name='ip_addresses')
    is_assigned = models.BooleanField(default=False, db_index=True)
    assigned_to_asset = models.ForeignKey('Asset', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_ips')
    freed_date = models.DateTimeField(null=True, blank=True, help_text="Date when IP was released from an asset")
    
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

    class Meta:
        ordering = ['address']
        verbose_name_plural = 'IP Addresses'

    def __str__(self):
        return self.address
    
    def is_guest_assigned(self):
        """Check if this IP is currently assigned to a guest."""
        return bool(self.guest_name)


class Asset(models.Model):
    """Model for tracking IT assets throughout their lifecycle."""
    
    SYSTEM_TYPE_CHOICES = [
        ('Desktop', 'Desktop'),
        ('Laptop', 'Laptop'),
        ('All-in-One PC', 'All-in-One PC'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('freed', 'Freed'),
        ('scrapped', 'Scrapped'),
    ]
    
    HEALTH_STATUS_CHOICES = [
        ('healthy', 'Healthy'),
        ('defective', 'Defective'),
    ]
    
    serial_number = models.AutoField(primary_key=True)
    asset_tag = models.CharField(max_length=50, unique=True, db_index=True, help_text="Unique asset identifier")
    system_type = models.CharField(max_length=20, choices=SYSTEM_TYPE_CHOICES)
    hardware_serial_number = models.CharField(max_length=100, blank=True, null=True, help_text="Hardware serial number (required for Laptop and All-in-One PC)")
    operating_system = models.ForeignKey(OperatingSystem, on_delete=models.PROTECT, related_name='assets')
    ip_address = models.ForeignKey(IPAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='asset')
    manual_ip = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="Manually entered IP address (not tracked in IP management)")
    particulars = models.TextField(blank=True, null=True, help_text="Detailed information about the asset")
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, related_name='assets', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', db_index=True)
    warranty_expiration = models.DateField(null=True, blank=True, db_index=True)
    freed_date = models.DateTimeField(null=True, blank=True)
    scrapped_date = models.DateTimeField(null=True, blank=True)
    manufacturer = models.CharField(max_length=100, blank=True, null=True, help_text="Manufacturer or brand of the asset")
    scrapping_reason = models.TextField(blank=True, null=True, help_text="Explanation for why the asset was scrapped")
    health_status = models.CharField(
        max_length=20,
        choices=HEALTH_STATUS_CHOICES,
        null=True,
        blank=True,
        help_text="Health status for freed systems"
    )
    issues_description = models.TextField(
        blank=True,
        null=True,
        help_text="Description of issues for defective freed systems"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['serial_number']

    def __str__(self):
        return f"{self.asset_tag} ({self.system_type})"
    
    def clean(self):
        """Validate asset data including branch-team consistency."""
        super().clean()
        
        # Validate team belongs to same branch as asset
        if self.team and self.branch:
            if self.team.branch_id != self.branch_id:
                raise ValidationError({
                    'team': 'Team must belong to the same branch as the asset.'
                })
        
        # Require branch if team is assigned
        if self.team and not self.branch:
            raise ValidationError({
                'branch': 'Asset must have a branch when a team is assigned.'
            })


class Attachment(models.Model):
    """Model for storing file attachments for assets."""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='asset_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.asset.asset_tag}"


class NetworkDevice(models.Model):
    """Model for tracking non-system network devices (cameras, printers, etc.)."""
    
    DEVICE_TYPE_CHOICES = [
        ('Camera', 'Camera'),
        ('Printer', 'Printer'),
        ('Punching Machine', 'Punching Machine'),
        ('Mobile', 'Mobile'),
        ('NVR', 'NVR'),
        ('DVR', 'DVR'),
        ('NAS Device', 'NAS Device'),
        ('Other', 'Other'),
    ]
    
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=255)
    ip_address = models.OneToOneField(
        IPAddress,
        on_delete=models.PROTECT,
        related_name='network_device',
        null=True,
        blank=True
    )
    manual_ip = models.GenericIPAddressField(
        protocol='IPv4',
        null=True,
        blank=True,
        help_text='Manual IP address (use if IP is not in the managed IP list)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['device_name']
        indexes = [
            models.Index(fields=['device_type']),
            models.Index(fields=['device_name']),
        ]
    
    def __str__(self):
        return f"{self.device_name} ({self.device_type})"
    
    def get_ip_address(self):
        """Return the IP address (managed or manual)."""
        if self.ip_address:
            return self.ip_address.address
        return self.manual_ip
    
    def clean(self):
        """Validate that at least one IP address is provided."""
        if not self.ip_address and not self.manual_ip:
            raise ValidationError('Either IP Address or Manual IP must be provided.')
        if self.ip_address and self.manual_ip:
            raise ValidationError('Please provide either IP Address or Manual IP, not both.')


class HyperVVM(models.Model):
    """Model for tracking Hyper-V virtual machines."""
    
    POWER_STATUS_CHOICES = [
        ('on', 'On'),
        ('off', 'Off'),
    ]
    
    name = models.CharField(max_length=200, unique=True, db_index=True)
    host_machine = models.ForeignKey(
        Asset,
        on_delete=models.PROTECT,
        related_name='hosted_vms',
        help_text="Physical machine hosting this VM"
    )
    ip_address = models.ForeignKey(
        IPAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vm'
    )
    manual_ip = models.GenericIPAddressField(
        protocol='IPv4',
        null=True,
        blank=True,
        help_text="Manually entered IP (not tracked in IP management)"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    power_status = models.CharField(
        max_length=10,
        choices=POWER_STATUS_CHOICES,
        default='on',
        help_text='Power status of the VM'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Hyper-V VM'
        verbose_name_plural = 'Hyper-V VMs'
        indexes = [
            models.Index(fields=['host_machine', 'is_active']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.name} (on {self.host_machine.asset_tag})"
    
    def clean(self):
        """Validate VM data."""
        from django.core.exceptions import ValidationError
        
        # Validate IP uniqueness if provided
        if self.ip_address:
            existing = HyperVVM.objects.filter(
                ip_address=self.ip_address
            ).exclude(pk=self.pk)
            if existing.exists():
                raise ValidationError({
                    'ip_address': 'This IP address is already assigned to another VM.'
                })
    
    def get_display_ip(self):
        """Return the IP address to display (tracked or manual)."""
        if self.ip_address:
            return self.ip_address.address
        return self.manual_ip or 'No IP assigned'
    
    def get_host_ip(self):
        """Return the host machine's IP address."""
        if self.host_machine.ip_address:
            return self.host_machine.ip_address.address
        return self.host_machine.manual_ip or 'No IP'


class AssetHistory(models.Model):
    """Model for tracking all changes to assets."""
    
    EVENT_TYPE_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('freed', 'Freed'),
        ('scrapped', 'Scrapped'),
        ('reassigned', 'Reassigned'),
        ('health_status_updated', 'Health Status Updated'),
    ]
    
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='history_entries',
        db_index=True,
        help_text="Asset this history entry belongs to"
    )
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of event that occurred"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this change occurred"
    )
    user = models.CharField(
        max_length=150,
        db_index=True,
        help_text="Username of user who made the change"
    )
    changes = models.JSONField(
        default=dict,
        help_text="Dictionary of field changes: {field_name: {'old': value, 'new': value}}"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional context (e.g., scrapping reason)"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Asset History'
        verbose_name_plural = 'Asset Histories'
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_tag} - {self.event_type} at {self.timestamp}"
    
    def get_formatted_changes(self):
        """Return human-readable formatted changes."""
        from assets.services.history_service import HistoryService
        return HistoryService.format_changes_for_display(self.changes, self.asset)


# Signal handlers for cache invalidation
@receiver(post_save, sender=Team)
def invalidate_team_hierarchy_cache_on_save(sender, instance, **kwargs):
    """Invalidate team hierarchy cache when a team is saved."""
    cache.delete('team_hierarchy')
    cache.delete(f'team_{instance.id}_hierarchy')
    if instance.parent:
        cache.delete(f'team_{instance.parent.id}_sub_teams')


@receiver(post_delete, sender=Team)
def invalidate_team_hierarchy_cache_on_delete(sender, instance, **kwargs):
    """Invalidate team hierarchy cache when a team is deleted."""
    cache.delete('team_hierarchy')
    cache.delete(f'team_{instance.id}_hierarchy')
    # Check if parent exists before accessing it (it might be deleted via CASCADE)
    try:
        if instance.parent_id:  # Use parent_id to avoid database query
            cache.delete(f'team_{instance.parent_id}_sub_teams')
    except:
        pass  # Parent might already be deleted


class TestingDevice(models.Model):
    """Model for tracking testing devices (mobile phones and tablets) with IP assignments."""
    
    device_name = models.CharField(max_length=255, help_text="Device name (e.g., 'iPhone 12 Pro', 'Samsung Galaxy Tab')")
    assigned_user = models.CharField(max_length=150, blank=True, null=True, help_text="User currently using this device")
    ip_address = models.OneToOneField(
        IPAddress,
        on_delete=models.PROTECT,
        related_name='testing_device',
        null=True,
        blank=True,
        help_text="Managed IP address from IP management system"
    )
    manual_ip = models.GenericIPAddressField(
        protocol='IPv4',
        null=True,
        blank=True,
        help_text='Manual IP address (use if IP is not in the managed IP list)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['device_name']
        indexes = [
            models.Index(fields=['device_name']),
            models.Index(fields=['assigned_user']),
        ]
    
    def __str__(self):
        return f"{self.device_name} - {self.assigned_user or 'Unassigned'}"
    
    def get_ip_address(self):
        """Return the IP address (managed or manual)."""
        if self.ip_address:
            return self.ip_address.address
        return self.manual_ip
    
    def clean(self):
        """Validate that either managed or manual IP is provided, but not both."""
        if self.ip_address and self.manual_ip:
            raise ValidationError('Please provide either IP Address or Manual IP, not both.')
