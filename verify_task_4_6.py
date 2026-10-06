"""
Quick verification test for Task 4.6: History recording in update_freed_asset method

This test verifies that the update_freed_asset method correctly:
1. Captures old health_status value before update
2. Calls HistoryService.record_health_status_update() after save
3. Passes asset, old_health_status, and user
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from django.db import transaction
from assets.models import Asset, OperatingSystem, AssetHistory
from assets.services.asset_service import AssetService


def verify_task_4_6():
    """Verify Task 4.6 implementation."""
    print("\n" + "="*70)
    print("Task 4.6 Verification: update_freed_asset History Recording")
    print("="*70)
    
    # Create test user
    user, _ = User.objects.get_or_create(
        username='task_4_6_verifier',
        defaults={'email': 'verifier@test.com'}
    )
    if not user.has_usable_password():
        user.set_password('testpass123')
        user.save()
    print(f"✓ Test user: {user.username}")
    
    # Create test OS
    os_obj, _ = OperatingSystem.objects.get_or_create(name='Test OS 4.6')
    print(f"✓ Test OS: {os_obj.name}")
    
    # Create freed asset
    freed_asset = Asset.objects.create(
        asset_tag='VERIFY-4-6',
        system_type='Desktop',
        operating_system=os_obj,
        status='freed',
        health_status='healthy',
    )
    print(f"✓ Created freed asset: {freed_asset.asset_tag}")
    print(f"  Initial health_status: {freed_asset.health_status}")
    
    # Get initial history count
    initial_count = AssetHistory.objects.filter(asset=freed_asset).count()
    print(f"  Initial history entries: {initial_count}")
    
    # Test 1: Update from healthy to defective
    print("\n--- Test 1: Healthy → Defective ---")
    update_data = {
        'health_status': 'defective',
        'issues_description': 'Hard drive failure'
    }
    
    AssetService.update_freed_asset(freed_asset, update_data, user)
    freed_asset.refresh_from_db()
    
    print(f"✓ Updated health_status: {freed_asset.health_status}")
    print(f"✓ Issues: {freed_asset.issues_description}")
    
    # Verify history was recorded
    history_entries = AssetHistory.objects.filter(
        asset=freed_asset,
        event_type='health_status_updated'
    ).order_by('-timestamp')
    
    assert history_entries.count() == 1, "Should have 1 history entry"
    entry = history_entries.first()
    
    assert entry.event_type == 'health_status_updated', "Event type should be health_status_updated"
    assert entry.user == user.username, f"User should be {user.username}"
    assert 'health_status' in entry.changes, "Changes should include health_status"
    assert entry.changes['health_status']['old'] == 'healthy', "Old value should be 'healthy'"
    assert entry.changes['health_status']['new'] == 'defective', "New value should be 'defective'"
    
    print(f"✓ History entry created correctly")
    print(f"  Event type: {entry.event_type}")
    print(f"  User: {entry.user}")
    print(f"  Change: {entry.changes['health_status']['old']} → {entry.changes['health_status']['new']}")
    
    # Test 2: Update from defective to healthy
    print("\n--- Test 2: Defective → Healthy ---")
    update_data = {
        'health_status': 'healthy',
        'issues_description': None
    }
    
    AssetService.update_freed_asset(freed_asset, update_data, user)
    freed_asset.refresh_from_db()
    
    print(f"✓ Updated health_status: {freed_asset.health_status}")
    
    # Verify second history entry
    history_entries = AssetHistory.objects.filter(
        asset=freed_asset,
        event_type='health_status_updated'
    ).order_by('-timestamp')
    
    assert history_entries.count() == 2, "Should have 2 history entries"
    entry = history_entries.first()
    
    assert entry.changes['health_status']['old'] == 'defective', "Old value should be 'defective'"
    assert entry.changes['health_status']['new'] == 'healthy', "New value should be 'healthy'"
    
    print(f"✓ Second history entry created correctly")
    print(f"  Change: {entry.changes['health_status']['old']} → {entry.changes['health_status']['new']}")
    
    # Cleanup
    freed_asset.delete()
    user.delete()
    os_obj.delete()
    
    print("\n" + "="*70)
    print("✅ Task 4.6 VERIFIED: All checks passed!")
    print("="*70)
    print("\nImplementation correctly:")
    print("  • Captures old health_status value before update")
    print("  • Calls HistoryService.record_health_status_update() after save")
    print("  • Passes asset, old_health_status, and user")
    print("  • Records changes in AssetHistory with correct event_type")
    print()


if __name__ == '__main__':
    try:
        verify_task_4_6()
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        import traceback
        traceback.print_exc()
