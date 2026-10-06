"""HyperVVM model for tracking Hyper-V virtual machines."""
from django.db import models
from django.core.exceptions import ValidationError


class HyperVVM(models.Model):
    """Model for tracking Hyper-V virtual machines."""
    
    POWER_STATUS_CHOICES = [
        ('on', 'On'),
        ('off', 'Off'),
    ]
    
    name = models.CharField(max_length=200, unique=True, db_index=True)
    host_machine = models.ForeignKey(
        'Asset',
        on_delete=models.PROTECT,
        related_name='hosted_vms',
        help_text="Physical machine hosting this VM"
    )
    ip_address = models.ForeignKey(
        'IPAddress',
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
