"""AssetIPAddress junction model for many-to-many relationship between Assets and IP addresses."""
from django.db import models
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError


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
    ip_label = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Description label for this IP address (e.g., 'WiFi', 'Mobile', 'VPN')"
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
        
        # Validate ip_label for non-primary IPs (Requirement 1.4.4)
        if not self.is_primary and not self.ip_label:
            raise ValidationError({
                'ip_label': 'Label is required for additional IP addresses.'
            })
        
        # Validate ip_label doesn't contain only whitespace (Requirement 1.4.5)
        if self.ip_label and not self.ip_label.strip():
            raise ValidationError({
                'ip_label': 'Label cannot contain only whitespace.'
            })
        
        # Primary IPs should not have labels (Requirement 1.4.6)
        if self.is_primary and self.ip_label:
            raise ValidationError({
                'ip_label': 'Primary IP should not have a label.'
            })
        
        # Check for duplicate IP on same asset (skip for primary IPs as they're managed separately)
        if self.asset_id and not self.is_primary:
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
