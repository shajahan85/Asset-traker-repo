"""
Unit tests for Task 4.6: update_freed_asset history recording.

Tests verify that the update_freed_asset method correctly records health status changes
in the AssetHistory table through HistoryService.record_health_status_update().
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from assets.models import Asset, AssetHistory, OperatingSystem
from assets.services.asset_service import AssetService


class TestUpdateFreedAssetHistoryRecording(TestCase):
    """Test cases for update_freed_asset history recording functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(
            username='testuser',
            password='password'
        )
        
        # Create OS
        self.os = OperatingSystem.objects.create(name="Windows 10")
        
        # Create freed asset
        self.freed_asset = Asset.objects.create(
            asset_tag='FREED001',
            system_type='Desktop',
            operating_system=self.os,
            status='freed',
            health_status='healthy',
            issues_description=None
        )
    
    def test_update_freed_asset_records_history_healthy_to_defective(self):
        """
        Test that update_freed_asset records history when changing from healthy to defective.
        
        Validates:
        - History entry is created with event_type='health_status_updated'
        - Old and new health_status values are captured
        - Issues_description is recorded when changing to defective
        - User attribution is correct
        """
        # Update freed asset from healthy to defective
        update_data = {
            'health_status': 'defective',
            'issues_description': 'Hard drive failure'
        }
        
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Verify history entry was created
        history_entries = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        )
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        
        # Verify event type
        self.assertEqual(entry.event_type, 'health_status_updated')
        
        # Verify user attribution
        self.assertEqual(entry.user, 'testuser')
        
        # Verify timestamp is set
        self.assertIsNotNone(entry.timestamp)
        
        # Verify changes recorded
        changes = entry.changes
        self.assertIn('health_status', changes)
        self.assertEqual(changes['health_status']['old'], 'healthy')
        self.assertEqual(changes['health_status']['new'], 'defective')
        
        # Verify issues_description is recorded
        self.assertIn('issues_description', changes)
        self.assertEqual(changes['issues_description']['old'], None)
        self.assertEqual(changes['issues_description']['new'], 'Hard drive failure')
    
    def test_update_freed_asset_records_history_defective_to_healthy(self):
        """
        Test that update_freed_asset records history when changing from defective to healthy.
        
        Validates:
        - History entry is created with event_type='health_status_updated'
        - Old and new health_status values are captured
        - Issues_description clearing is recorded
        - User attribution is correct
        """
        # First set asset to defective
        self.freed_asset.health_status = 'defective'
        self.freed_asset.issues_description = 'Screen not working'
        self.freed_asset.save()
        
        # Clear existing history entries from setup
        AssetHistory.objects.filter(asset=self.freed_asset).delete()
        
        # Update freed asset from defective to healthy
        update_data = {
            'health_status': 'healthy',
            'issues_description': None
        }
        
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Verify history entry was created
        history_entries = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        )
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        
        # Verify event type
        self.assertEqual(entry.event_type, 'health_status_updated')
        
        # Verify user attribution
        self.assertEqual(entry.user, 'testuser')
        
        # Verify changes recorded
        changes = entry.changes
        self.assertIn('health_status', changes)
        self.assertEqual(changes['health_status']['old'], 'defective')
        self.assertEqual(changes['health_status']['new'], 'healthy')
        
        # Verify issues_description clearing is recorded
        self.assertIn('issues_description', changes)
        self.assertEqual(changes['issues_description']['old'], 'Screen not working')
        self.assertEqual(changes['issues_description']['new'], None)
    
    def test_update_freed_asset_captures_old_value_before_update(self):
        """
        Test that update_freed_asset captures old health_status value before update.
        
        This test ensures that the old value is captured before any modifications
        are made to the asset object.
        """
        # Initial state
        self.assertEqual(self.freed_asset.health_status, 'healthy')
        
        # Update to defective
        update_data = {
            'health_status': 'defective',
            'issues_description': 'Keyboard malfunction'
        }
        
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Verify the asset was updated
        self.freed_asset.refresh_from_db()
        self.assertEqual(self.freed_asset.health_status, 'defective')
        
        # Verify history captured the correct old value
        entry = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        ).first()
        
        self.assertEqual(entry.changes['health_status']['old'], 'healthy')
        self.assertEqual(entry.changes['health_status']['new'], 'defective')
    
    def test_update_freed_asset_calls_history_service_after_save(self):
        """
        Test that update_freed_asset calls HistoryService.record_health_status_update after save.
        
        This test ensures that the history is only recorded after the asset is successfully
        saved to the database (within the transaction).
        """
        # Update health status
        update_data = {
            'health_status': 'defective',
            'issues_description': 'Monitor issue'
        }
        
        # Count history entries before
        initial_count = AssetHistory.objects.filter(asset=self.freed_asset).count()
        
        # Perform update
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Verify asset was saved
        self.freed_asset.refresh_from_db()
        self.assertEqual(self.freed_asset.health_status, 'defective')
        self.assertEqual(self.freed_asset.issues_description, 'Monitor issue')
        
        # Verify history was recorded after save
        final_count = AssetHistory.objects.filter(asset=self.freed_asset).count()
        self.assertEqual(final_count, initial_count + 1)
    
    def test_update_freed_asset_passes_correct_parameters_to_history_service(self):
        """
        Test that update_freed_asset passes asset, old_health_status, and user to HistoryService.
        
        This test verifies that all required parameters are correctly passed to the
        HistoryService.record_health_status_update() method.
        """
        # Update health status
        update_data = {
            'health_status': 'defective',
            'issues_description': 'RAM failure'
        }
        
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Retrieve history entry
        entry = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        ).first()
        
        # Verify asset parameter
        self.assertEqual(entry.asset, self.freed_asset)
        
        # Verify old_health_status parameter (captured in changes)
        self.assertEqual(entry.changes['health_status']['old'], 'healthy')
        
        # Verify user parameter
        self.assertEqual(entry.user, self.user.username)
    
    def test_update_freed_asset_multiple_updates_create_multiple_history_entries(self):
        """
        Test that multiple updates create multiple history entries.
        
        This ensures that each update operation creates its own history entry,
        providing a complete audit trail.
        """
        # First update: healthy -> defective
        update_data_1 = {
            'health_status': 'defective',
            'issues_description': 'Initial issue'
        }
        AssetService.update_freed_asset(self.freed_asset, update_data_1, self.user)
        
        # Second update: defective -> healthy
        self.freed_asset.refresh_from_db()
        update_data_2 = {
            'health_status': 'healthy',
            'issues_description': None
        }
        AssetService.update_freed_asset(self.freed_asset, update_data_2, self.user)
        
        # Verify two history entries exist
        history_entries = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        ).order_by('timestamp')
        
        self.assertEqual(history_entries.count(), 2)
        
        # Verify first entry
        first_entry = history_entries[0]
        self.assertEqual(first_entry.changes['health_status']['old'], 'healthy')
        self.assertEqual(first_entry.changes['health_status']['new'], 'defective')
        
        # Verify second entry
        second_entry = history_entries[1]
        self.assertEqual(second_entry.changes['health_status']['old'], 'defective')
        self.assertEqual(second_entry.changes['health_status']['new'], 'healthy')
    
    def test_update_freed_asset_with_particulars_also_records_history(self):
        """
        Test that updating particulars along with health_status is handled correctly.
        
        The history should focus on health_status changes as per the task requirements.
        """
        # Update health status and particulars
        update_data = {
            'health_status': 'defective',
            'issues_description': 'Power supply failure',
            'particulars': 'Updated particulars'
        }
        
        AssetService.update_freed_asset(self.freed_asset, update_data, self.user)
        
        # Verify history entry was created
        entry = AssetHistory.objects.filter(
            asset=self.freed_asset,
            event_type='health_status_updated'
        ).first()
        
        # Verify health_status change is recorded
        self.assertIn('health_status', entry.changes)
        self.assertEqual(entry.changes['health_status']['old'], 'healthy')
        self.assertEqual(entry.changes['health_status']['new'], 'defective')
        
        # Verify asset particulars was updated
        self.freed_asset.refresh_from_db()
        self.assertEqual(self.freed_asset.particulars, 'Updated particulars')
