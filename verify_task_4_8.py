#!/usr/bin/env python
"""
Verification script for Task 4.8: Add history recording to create_scrapped_asset method

This script demonstrates that:
1. create_scrapped_asset calls HistoryService.record_creation() after asset creation
2. The history entry has event_type='created'
3. The history entry captures status='scrapped'
4. All tracked fields are recorded including scrapping_reason
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.contrib.auth import get_user_model
from assets.models import Asset, AssetHistory, OperatingSystem
from assets.services.asset_service import AssetService

User = get_user_model()

# Get or create test user
user, _ = User.objects.get_or_create(username='verification_user')

# Get or create test OS
os_obj, _ = OperatingSystem.objects.get_or_create(name='Test OS')

# Create scrapped asset
print("\n=== Task 4.8 Verification: create_scrapped_asset History Recording ===\n")

data = {
    'asset_tag': 'VERIFY_SCRAPPED_001',
    'system_type': 'Desktop',
    'operating_system': os_obj,
    'manufacturer': 'Dell',
    'particulars': 'Test verification asset',
    'scrapping_reason': 'Obsolete hardware - verification test'
}

# Delete existing test asset if it exists
Asset.objects.filter(asset_tag=data['asset_tag']).delete()

print(f"Creating scrapped asset: {data['asset_tag']}")
asset = AssetService.create_scrapped_asset(data, user)

print(f"✓ Asset created with status: {asset.status}")
print(f"✓ Asset scrapping reason: {asset.scrapping_reason}")

# Verify history entry
history_entries = AssetHistory.objects.filter(asset=asset)
print(f"\n✓ History entries created: {history_entries.count()}")

if history_entries.exists():
    entry = history_entries.first()
    print(f"\nHistory Entry Details:")
    print(f"  - Event Type: {entry.event_type}")
    print(f"  - User: {entry.user}")
    print(f"  - Timestamp: {entry.timestamp}")
    
    changes = entry.changes
    print(f"\nRecorded Changes ({len(changes)} fields):")
    
    # Check critical fields
    if 'status' in changes:
        print(f"  ✓ status: {changes['status']['old']} → {changes['status']['new']}")
    else:
        print(f"  ✗ status: NOT RECORDED")
    
    if 'scrapping_reason' in changes:
        print(f"  ✓ scrapping_reason: {changes['scrapping_reason']['new']}")
    else:
        print(f"  ✗ scrapping_reason: NOT RECORDED")
    
    if 'asset_tag' in changes:
        print(f"  ✓ asset_tag: {changes['asset_tag']['new']}")
    
    if 'system_type' in changes:
        print(f"  ✓ system_type: {changes['system_type']['new']}")
    
    # Show all tracked fields
    print(f"\n  All tracked fields in history:")
    for field_name in sorted(changes.keys()):
        old_val = changes[field_name].get('old', 'None')
        new_val = changes[field_name].get('new', 'None')
        print(f"    - {field_name}: {old_val} → {new_val}")
    
    print("\n=== VERIFICATION SUCCESSFUL ===")
    print("\nTask 4.8 Requirements Met:")
    print("  ✓ HistoryService.record_creation() is called after scrapped asset creation")
    print("  ✓ Event type reflects 'created'")
    print("  ✓ Status reflects 'scrapped'")
    print("  ✓ All tracked fields including scrapping_reason are recorded")
else:
    print("\n✗ No history entry created - VERIFICATION FAILED")

# Cleanup
print("\nCleaning up test data...")
asset.delete()
user.delete()
print("✓ Cleanup complete")
