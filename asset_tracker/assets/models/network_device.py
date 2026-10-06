"""NetworkDevice model for tracking non-system network devices."""
from django.db import models
from django.core.exceptions import ValidationError


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
        ('Managed Switch', 'Managed Switch'),
        ('Access Control', 'Access Control'),
        ('Other', 'Other'),
    ]
    
    device_type = models.CharField(max_length=50, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=255)
    ip_address = models.OneToOneField(
        'IPAddress',
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
