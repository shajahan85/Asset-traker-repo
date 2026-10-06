"""Service for managing asset IP address assignments."""
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


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
        from assets.models import AssetIPAddress
        
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
        from assets.models import AssetIPAddress
        
        with transaction.atomic():
            # Skip if already migrated
            if AssetIPAddress.objects.filter(asset=asset, is_primary=True).exists():
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
