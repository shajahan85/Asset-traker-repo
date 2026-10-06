#!/usr/bin/env python
"""Quick test script for AssetHistory model."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetHistory

# Get first asset
asset = Asset.objects.first()

if not asset:
    print("No assets found in database. Cannot test.")
    exit(1)

print(f"Testing AssetHistory model with asset: {asset.asset_tag}")

# Create a test history entry
history = AssetHistory.objects.create(
    asset=asset,
    event_type='created',
    user='test_user',
    changes={'asset_tag': {'old': None, 'new': asset.asset_tag}},
    notes='Test entry'
)

print(f"✓ Created history entry: {history}")
print(f"✓ History ID: {history.id}")
print(f"✓ Timestamp: {history.timestamp}")
print(f"✓ Event type: {history.get_event_type_display()}")
print(f"✓ Related name works: {asset.history_entries.count()} entry(ies)")
print(f"✓ Changes: {history.changes}")

# Test __str__ method
print(f"✓ __str__ method: {str(history)}")

# Clean up
history.delete()
print("✓ Test history entry deleted")
print("\n✅ All tests passed! AssetHistory model is working correctly.")
