"""TestingDevice model for tracking testing devices with IP assignments."""
from django.db import models
from django.core.exceptions import ValidationError


class TestingDevice(models.Model):
    """Model for tracking testing devices (mobile phones and tablets) with IP assignments."""
    
    device_name = models.CharField(max_length=255, help_text="Device name (e.g., 'iPhone 12 Pro', 'Samsung Galaxy Tab')")
    assigned_user = models.CharField(max_length=150, blank=True, null=True, help_text="User currently using this device")
    ip_address = models.OneToOneField(
        'IPAddress',
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
