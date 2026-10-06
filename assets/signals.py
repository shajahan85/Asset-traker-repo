"""Signal handlers for assets app."""
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone


@receiver(post_delete, sender='assets.AssetIPAddress')
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
