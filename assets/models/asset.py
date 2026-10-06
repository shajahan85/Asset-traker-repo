"""Asset model for tracking IT assets throughout their lifecycle."""
from django.db import models
from django.core.exceptions import ValidationError


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
    operating_system = models.ForeignKey('OperatingSystem', on_delete=models.PROTECT, related_name='assets')
    ip_address = models.ForeignKey('IPAddress', on_delete=models.SET_NULL, null=True, blank=True, related_name='asset')
    manual_ip = models.GenericIPAddressField(protocol='IPv4', null=True, blank=True, help_text="Manually entered IP address (not tracked in IP management)")
    particulars = models.TextField(blank=True, null=True, help_text="Detailed information about the asset")
    assigned_to = models.CharField(max_length=100, blank=True, null=True)
    employee_code = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text="Employee code of the person to whom the asset is assigned")
    team = models.ForeignKey('Team', on_delete=models.SET_NULL, null=True, blank=True, related_name='assets')
    branch = models.ForeignKey('Branch', on_delete=models.PROTECT, related_name='assets', null=True, blank=True)
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
    
    # New methods for multiple IP address support
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
    
    def is_server_controller(self):
        """
        Check if this asset is a Server Controller (192.168.50.x IP range).
        
        Server Controllers are dynamically identified by their IP address.
        This checks primary IP, additional IPs, and manual IP.
        
        Returns:
            bool: True if IP is in 192.168.50.x range
        """
        # Check primary IP
        primary = self.get_primary_ip()
        if primary and primary.ip_address:
            ip_str = primary.ip_address.address
            if ip_str and ip_str.startswith('192.168.50.'):
                return True
        
        # Check manual IP
        if self.manual_ip and self.manual_ip.startswith('192.168.50.'):
            return True
        
        # Check secondary IPs
        for asset_ip in self.get_secondary_ips():
            if asset_ip.ip_address:
                ip_str = asset_ip.ip_address.address
                if ip_str and ip_str.startswith('192.168.50.'):
                    return True
        
        return False
    
    def get_ip_address_string(self):
        """
        Get the primary IP address as a simple string.
        
        Returns:
            str: IP address string, or empty string if no IP
        """
        primary = self.get_primary_ip()
        if primary and primary.ip_address:
            return primary.ip_address.address
        if self.manual_ip:
            return self.manual_ip
        return ''
