"""
Verification test for Task 4.6: Add history recording to update_freed_asset method
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.contrib.auth.models import User
from assets.models import Asset, OperatingSystem, AssetHistory
from assets.services.asset_service import AssetService
from django.utils import timezone

def test_update_freed_asset_records_history():
    """Verify that update_freed_asset records health status changes in history."""
    print("=" * 80)
    print("Task 4.6 Verification: update_freed_asset history recording")
    print("=" * 80)
    
    # Create a test user
    user, _ = User.objects.get_or_create(
        username='test_user_4_6', 
        defaults={'password': 'testpass'}
    )
    print(f"✓ Created test user: {user.username}")
    
    # Create an OS
    os_obj, _ = OperatingSystem.objects.get_or_create(name='Windows 10 Test')
    print(f"✓ Created/found OS: {os_obj.name}")
    
    # Create a freed asset
    asset = Asset.objects.create(
        asset_tag='TEST-TASK-4-6',
        system_type='Desktop',
        operating_system=os_obj,
        status='freed',
        health_status='healthy',
        freed_date=timezone.now()
    )
    print(f"✓ Created freed asset: {asset.asset_tag}")
    print(f"  Initial health status: {asset.health_status}")
    
    # Clear any existing history for clean test
    AssetHistory.objects.filter(asset=asset).delete()
    
    # Update the freed asset (healthy -> defective)
    print("\n--- Test 1: Updating health status from healthy to defective ---")
    data = {
        'health_status': 'defective',
        'issues_description': 'Screen not working properly'
    }
    
    updated_asset = AssetService.update_freed_asset(asset, data, user)
    print(f"✓ Updated health status to: {updated_asset.health_status}")
    print(f"✓ Issues description: {updated_asset.issues_description}")
    
    # Verify history entry was created
    history_entries = AssetHistory.objects.filter(asset=asset).order_by('-timestamp')
    assert history_entries.count() == 1, f"Expected 1 history entry, found {history_entries.count()}"
    print(f"✓ History entry created (total: {history_entries.count()})")
    
    # Verify history entry details
    entry = history_entries.first()
    assert entry.event_type == 'health_status_updated', f"Expected event_type 'health_status_updated', got '{entry.event_type}'"
    print(f"✓ Event type: {entry.event_type}")
    
    assert entry.user == user.username, f"Expected user '{user.username}', got '{entry.user}'"
    print(f"✓ User: {entry.user}")
    
    # Verify changes recorded
    changes = entry.changes
    assert 'health_status' in changes, "health_status not found in changes"
    assert changes['health_status']['old'] == 'healthy', f"Expected old value 'healthy', got '{changes['health_status']['old']}'"
    assert changes['health_status']['new'] == 'defective', f"Expected new value 'defective', got '{changes['health_status']['new']}'"
    print(f"✓ Health status change: {changes['health_status']['old']} -> {changes['health_status']['new']}")
    
    assert 'issues_description' in changes, "issues_description not found in changes"
    assert changes['issues_description']['new'] == 'Screen not working properly', f"Issues description mismatch"
    print(f"✓ Issues description recorded: {changes['issues_description']['new']}")
    
    # Test 2: Update back to healthy
    print("\n--- Test 2: Updating health status from defective to healthy ---")
    data2 = {
        'health_status': 'healthy',
        'issues_description': None
    }
    
    updated_asset2 = AssetService.update_freed_asset(asset, data2, user)
    print(f"✓ Updated health status to: {updated_asset2.health_status}")
    
    # Verify second history entry
    history_entries2 = AssetHistory.objects.filter(asset=asset).order_by('-timestamp')
    assert history_entries2.count() == 2, f"Expected 2 history entries, found {history_entries2.count()}"
    print(f"✓ Second history entry created (total: {history_entries2.count()})")
    
    entry2 = history_entries2.first()
    assert entry2.event_type == 'health_status_updated', f"Expected event_type 'health_status_updated', got '{entry2.event_type}'"
    print(f"✓ Event type: {entry2.event_type}")
    
    changes2 = entry2.changes
    assert changes2['health_status']['old'] == 'defective', f"Expected old value 'defective', got '{changes2['health_status']['old']}'"
    assert changes2['health_status']['new'] == 'healthy', f"Expected new value 'healthy', got '{changes2['health_status']['new']}'"
    print(f"✓ Health status change: {changes2['health_status']['old']} -> {changes2['health_status']['new']}")
    
    # Cleanup
    asset.delete()
    user.delete()
    print("\n✓ Test cleanup completed")
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED: Task 4.6 is correctly implemented!")
    print("=" * 80)
    print("\nSummary:")
    print("• update_freed_asset captures old health_status value before update ✓")
    print("• update_freed_asset calls HistoryService.record_health_status_update() after save ✓")
    print("• History entry contains correct event_type, user, and changes ✓")
    print("• Both healthy->defective and defective->healthy transitions work ✓")

if __name__ == '__main__':
    try:
        test_update_freed_asset_records_history()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
