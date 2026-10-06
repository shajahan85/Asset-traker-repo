# Data migration to populate ip_label for existing secondary IPs

from django.db import migrations


def populate_ip_labels(apps, schema_editor):
    """
    Set default ip_label for existing secondary IPs.
    
    This migration populates the ip_label field with "Secondary IP" for all
    existing AssetIPAddress records where:
    - is_primary=False (secondary IPs)
    - ip_label is null (not already set)
    
    Primary IPs (is_primary=True) retain null ip_label as intended.
    """
    AssetIPAddress = apps.get_model('assets', 'AssetIPAddress')
    
    # Set label "Secondary IP" for all existing secondary (non-primary) IPs
    # that don't already have a label
    updated_count = AssetIPAddress.objects.filter(
        is_primary=False,
        ip_label__isnull=True
    ).update(ip_label="Secondary IP")
    
    # Print migration summary for visibility
    if updated_count > 0:
        print(f"  Populated ip_label for {updated_count} secondary IP address(es)")


def reverse_populate_ip_labels(apps, schema_editor):
    """
    Reverse operation - clear ip_label for secondary IPs.
    
    This allows rolling back the migration if needed by clearing the
    ip_label field for all secondary IPs.
    """
    AssetIPAddress = apps.get_model('assets', 'AssetIPAddress')
    
    # Clear ip_label for all secondary IPs
    cleared_count = AssetIPAddress.objects.filter(
        is_primary=False
    ).update(ip_label=None)
    
    if cleared_count > 0:
        print(f"  Cleared ip_label for {cleared_count} secondary IP address(es)")


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0021_add_ip_label_to_assetipaddress'),
    ]

    operations = [
        migrations.RunPython(
            populate_ip_labels,
            reverse_code=reverse_populate_ip_labels
        ),
    ]
