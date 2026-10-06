"""IP Address and IPRange models."""
from django.db import models
from django.core.validators import validate_ipv4_address


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

    # Manual occupation fields
    manually_occupied = models.BooleanField(
        default=False,
        help_text="Whether this IP was manually marked as occupied"
    )
    occupied_by = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="Username of admin who marked this IP as occupied"
    )
    occupied_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this IP was manually marked as occupied"
    )
    occupied_particulars = models.TextField(
        blank=True,
        null=True,
        help_text="Details about why this IP is marked as occupied (e.g., employee name, company)"
    )

    class Meta:
        ordering = ['address']
        verbose_name_plural = 'IP Addresses'

    def __str__(self):
        return self.address
    
    def is_guest_assigned(self):
        """Check if this IP is currently assigned to a guest."""
        return bool(self.guest_name)
