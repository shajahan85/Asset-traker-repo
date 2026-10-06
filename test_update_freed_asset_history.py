 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 """
Test script to verify update_freed_asset creates history entries.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset, OperatingSystem, AssetHistory
from assets.services.asset_service import AssetService
from django.utils import timezone

# Create a test user
user, _ = User.objects.get_or_create(username='testuser', defaults={'password': 'testpass'})

# Create an OS
os_obj, _ = OperatingSystem.objects.get_or_create(name='Windows 10')

# Create a freed asset
asset = Asset.objects.create(
    asset_tag='TEST-FREED-001',
    system_type='Desktop',
    operating_system=os_obj,
    status='freed',
    health_status='healthy',
    freed_date=timezone.now()
)

print(f"Created freed asset: {asset.asset_tag}")
print(f"Initial health status: {asset.health_status}")
print(f"History entries before update: {AssetHistory.objects.filter(asset=asset).count()}")

# Update the freed asset
data = {
    'health_status': 'defective',
    'issues_description': 'Screen not working properly'
}

updated_asset = AssetService.update_freed_asset(asset, data, user)

print(f"\nAfter update:")
print(f"New health status: {updated_asset.health_status}")
print(f"Issues description: {updated_asset.issues_description}")
print(f"History entries after update: {AssetHistory.objects.filter(asset=asset).count()}")

# Check the history entry
history_entries = AssetHistory.objects.filter(asset=asset).order_by('-timestamp')
if history_entries.exists():
    entry = history_entries.first()
    print(f"\nHistory Entry Details:")
    print(f"Event type: {entry.event_type}")
    print(f"User: {entry.user}")
    print(f"Timestamp: {entry.timestamp}")
    print(f"Changes: {entry.changes}")
    
    if entry.event_type == 'health_status_updated':
        print("\n✓ SUCCESS: History entry with 'health_status_updated' event was created")
        if 'health_status' in entry.changes:
            print(f"✓ Health status change recorded: {entry.changes['health_status']['old']} -> {entry.changes['health_status']['new']}")
        if 'issues_description' in entry.changes:
            print(f"✓ Issues description recorded: {entry.changes['issues_description']}")
    else:
        print(f"\n✗ FAIL: Expected 'health_status_updated' but got '{entry.event_type}'")
else:
    print("\n✗ FAIL: No history entry was created")

# Cleanup
asset.delete()
print("\n\nTest asset cleaned up.")
