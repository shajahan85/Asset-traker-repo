"""
Unit tests for HistoryService.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from assets.models import Asset, AssetHistory, IPAddress, IPRange, OperatingSystem, Team
from assets.services.history_service import HistoryService


class TestHistoryServiceRecordingMethods(TestCase):
    """Test cases for HistoryService history recording methods."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create IP range and addresses
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        self.ip1 = IPAddress.objects.create(
            address="192.168.10.1",
            ip_range=self.ip_range,
            is_assigned=False
        )
        self.ip2 = IPAddress.objects.create(
            address="192.168.10.2",
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        # Create OS and Team
        self.os = OperatingSystem.objects.create(name="Windows 10")
        self.team = Team.objects.create(name="IT Department")
    
    def test_record_creation_creates_history_entry(self):
        """Test that record_creation creates a history entry with correct event type."""
        # Create an asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe',
            team=self.team
        )
        
        # Record creation
        HistoryService.record_creation(asset, self.user)
        
        # Check history entry was created
        history_entries = AssetHistory.objects.filter(asset=asset)
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        self.assertEqual(entry.event_type, 'created')
        self.assertEqual(entry.user, 'testuser')
        self.assertIsNotNone(entry.timestamp)
    
    def test_record_creation_captures_initial_values(self):
        """Test that record_creation captures initial field values."""
        # Create an asset with various fields
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe',
            team=self.team,
            manufacturer='Dell',
            particulars='Test particulars'
        )
        
        # Record creation
        HistoryService.record_creation(asset, self.user)
        
        # Check changes captured
        entry = AssetHistory.objects.get(asset=asset)
        changes = entry.changes
        
        self.assertIn('asset_tag', changes)
        self.assertEqual(changes['asset_tag']['old'], None)
        self.assertEqual(changes['asset_tag']['new'], 'BIDC001')
        
        self.assertIn('system_type', changes)
        self.assertEqual(changes['system_type']['new'], 'Desktop')
        
        self.assertIn('assigned_to', changes)
        self.assertEqual(changes['assigned_to']['new'], 'John Doe')
        
        self.assertIn('manufacturer', changes)
        self.assertEqual(changes['manufacturer']['new'], 'Dell')
    
    def test_record_creation_skips_empty_fields(self):
        """Test that record_creation skips empty/null fields."""
        # Create an asset with minimal fields
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active'
        )
        
        # Record creation
        HistoryService.record_creation(asset, self.user)
        
        # Check changes don't include empty fields
        entry = AssetHistory.objects.get(asset=asset)
        changes = entry.changes
        
        # These should be present
        self.assertIn('asset_tag', changes)
        self.assertIn('system_type', changes)
        self.assertIn('status', changes)
        
        # assigned_to should not be in changes if it's empty
        if 'assigned_to' in changes:
            # If it is present, it should be because it has a value
            self.assertNotEqual(changes['assigned_to']['new'], '')
            self.assertIsNotNone(changes['assigned_to']['new'])
    
    def test_record_update_creates_history_entry(self):
        """Test that record_update creates a history entry with correct event type."""
        # Create an asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe'
        )
        
        # Capture old values
        old_values = {
            'assigned_to': 'John Doe',
            'system_type': 'Desktop'
        }
        
        # Update asset
        asset.assigned_to = 'Jane Smith'
        asset.save()
        
        # Record update
        HistoryService.record_update(asset, old_values, self.user)
        
        # Check history entry was created
        history_entries = AssetHistory.objects.filter(asset=asset)
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        self.assertEqual(entry.event_type, 'updated')
        self.assertEqual(entry.user, 'testuser')
    
    def test_record_update_captures_changed_fields(self):
        """Test that record_update captures only changed fields."""
        # Create an asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe',
            manufacturer='Dell'
        )
        
        # Capture old values
        old_values = {}
        for field in HistoryService.TRACKED_FIELDS:
            old_values[field] = HistoryService._get_field_value(asset, field)
        
        # Update asset
        asset.assigned_to = 'Jane Smith'
        asset.manufacturer = 'HP'
        asset.save()
        
        # Record update
        HistoryService.record_update(asset, old_values, self.user)
        
        # Check changes captured
        entry = AssetHistory.objects.get(asset=asset)
        changes = entry.changes
        
        # Only changed fields should be present
        self.assertIn('assigned_to', changes)
        self.assertEqual(changes['assigned_to']['old'], 'John Doe')
        self.assertEqual(changes['assigned_to']['new'], 'Jane Smith')
        
        self.assertIn('manufacturer', changes)
        self.assertEqual(changes['manufacturer']['old'], 'Dell')
        self.assertEqual(changes['manufacturer']['new'], 'HP')
        
        # Unchanged fields should not be present
        self.assertNotIn('system_type', changes)
        self.assertNotIn('asset_tag', changes)
    
    def test_record_update_no_changes_creates_no_entry(self):
        """Test that record_update creates no entry when no fields changed."""
        # Create an asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe'
        )
        
        # Capture old values
        old_values = {}
        for field in HistoryService.TRACKED_FIELDS:
            old_values[field] = HistoryService._get_field_value(asset, field)
        
        # Don't change anything
        asset.save()
        
        # Record update
        HistoryService.record_update(asset, old_values, self.user)
        
        # No history entry should be created
        history_entries = AssetHistory.objects.filter(asset=asset)
        self.assertEqual(history_entries.count(), 0)
    
    def test_record_status_change_freed(self):
        """Test that record_status_change records freed transition."""
        # Create an active asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='freed',
            assigned_to=None,
            team=None
        )
        
        # Record status change
        HistoryService.record_status_change(asset, 'freed', self.user)
        
        # Check history entry
        entry = AssetHistory.objects.get(asset=asset)
        self.assertEqual(entry.event_type, 'freed')
        self.assertEqual(entry.user, 'testuser')
        
        changes = entry.changes
        self.assertIn('status', changes)
        self.assertEqual(changes['status']['old'], 'active')
        self.assertEqual(changes['status']['new'], 'freed')
    
    def test_record_status_change_scrapped(self):
        """Test that record_status_change records scrapped transition."""
        # Create a freed asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='scrapped'
        )
        
        # Record status change with notes
        HistoryService.record_status_change(asset, 'scrapped', self.user, notes='Hardware failure')
        
        # Check history entry
        entry = AssetHistory.objects.get(asset=asset)
        self.assertEqual(entry.event_type, 'scrapped')
        self.assertEqual(entry.user, 'testuser')
        self.assertEqual(entry.notes, 'Hardware failure')
        
        changes = entry.changes
        self.assertIn('status', changes)
        self.assertEqual(changes['status']['old'], 'freed')
        self.assertEqual(changes['status']['new'], 'scrapped')
    
    def test_record_status_change_reassigned(self):
        """Test that record_status_change records reassigned transition."""
        # Create a freed asset
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active'
        )
        
        # Record status change
        HistoryService.record_status_change(asset, 'reassigned', self.user)
        
        # Check history entry
        entry = AssetHistory.objects.get(asset=asset)
        self.assertEqual(entry.event_type, 'reassigned')
        self.assertEqual(entry.user, 'testuser')
        
        changes = entry.changes
        self.assertIn('status', changes)
        self.assertEqual(changes['status']['old'], 'freed')
        self.assertEqual(changes['status']['new'], 'active')
    
    def test_record_health_status_update_to_defective(self):
        """Test that record_health_status_update records health status change to defective."""
        # Create a freed asset with healthy status
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='freed',
            health_status='defective',
            issues_description='Screen not working'
        )
        
        # Record health status update
        HistoryService.record_health_status_update(asset, 'healthy', self.user, None)
        
        # Check history entry
        entry = AssetHistory.objects.get(asset=asset)
        self.assertEqual(entry.event_type, 'health_status_updated')
        self.assertEqual(entry.user, 'testuser')
        
        changes = entry.changes
        self.assertIn('health_status', changes)
        self.assertEqual(changes['health_status']['old'], 'healthy')
        self.assertEqual(changes['health_status']['new'], 'defective')
        
        # Should also record issues_description
        self.assertIn('issues_description', changes)
        self.assertEqual(changes['issues_description']['old'], None)
        self.assertEqual(changes['issues_description']['new'], 'Screen not working')
    
    def test_record_health_status_update_to_healthy(self):
        """Test that record_health_status_update records health status change to healthy."""
        # Create a freed asset with defective status
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='freed',
            health_status='healthy',
            issues_description='Screen not working'
        )
        
        # Record health status update
        HistoryService.record_health_status_update(asset, 'defective', self.user, 'Screen not working')
        
        # Check history entry
        entry = AssetHistory.objects.get(asset=asset)
        self.assertEqual(entry.event_type, 'health_status_updated')
        self.assertEqual(entry.user, 'testuser')
        
        changes = entry.changes
        self.assertIn('health_status', changes)
        self.assertEqual(changes['health_status']['old'], 'defective')
        self.assertEqual(changes['health_status']['new'], 'healthy')
        
        # Should also record clearing of issues_description
        self.assertIn('issues_description', changes)
        self.assertEqual(changes['issues_description']['old'], 'Screen not working')
        self.assertEqual(changes['issues_description']['new'], None)
    
    def test_get_field_value_handles_foreign_keys(self):
        """Test that _get_field_value correctly handles foreign key fields."""
        # Create an asset with foreign keys
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            team=self.team,
            status='active'
        )
        
        # Test operating_system
        os_value = HistoryService._get_field_value(asset, 'operating_system')
        self.assertEqual(os_value, 'Windows 10')
        
        # Test team
        team_value = HistoryService._get_field_value(asset, 'team')
        self.assertEqual(team_value, 'IT Department')
    
    def test_get_field_value_handles_ip_address(self):
        """Test that _get_field_value correctly extracts IP address."""
        # Create an asset with IP address
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            ip_address=self.ip1,
            status='active'
        )
        
        # Test ip_address
        ip_value = HistoryService._get_field_value(asset, 'ip_address')
        self.assertEqual(ip_value, '192.168.10.1')
    
    def test_get_field_value_handles_null_values(self):
        """Test that _get_field_value correctly handles null values."""
        # Create an asset with no team
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active'
        )
        
        # Test null team
        team_value = HistoryService._get_field_value(asset, 'team')
        self.assertIsNone(team_value)
        
        # Test null ip_address
        ip_value = HistoryService._get_field_value(asset, 'ip_address')
        self.assertIsNone(ip_value)
    
    def test_record_creation_with_ip_address(self):
        """Test that record_creation correctly records IP address."""
        # Create an asset with IP
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            ip_address=self.ip1,
            status='active'
        )
        
        # Record creation
        HistoryService.record_creation(asset, self.user)
        
        # Check IP address in changes
        entry = AssetHistory.objects.get(asset=asset)
        changes = entry.changes
        
        self.assertIn('ip_address', changes)
        self.assertEqual(changes['ip_address']['old'], None)
        self.assertEqual(changes['ip_address']['new'], '192.168.10.1')
    
    def test_record_update_with_ip_address_change(self):
        """Test that record_update correctly records IP address changes."""
        # Create an asset with IP
        asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            ip_address=self.ip1,
            status='active'
        )
        
        # Capture old values
        old_values = {}
        for field in HistoryService.TRACKED_FIELDS:
            old_values[field] = HistoryService._get_field_value(asset, field)
        
        # Change IP
        asset.ip_address = self.ip2
        asset.save()
        
        # Record update
        HistoryService.record_update(asset, old_values, self.user)
        
        # Check IP address change in history
        entry = AssetHistory.objects.get(asset=asset)
        changes = entry.changes
        
        self.assertIn('ip_address', changes)
        self.assertEqual(changes['ip_address']['old'], '192.168.10.1')
        self.assertEqual(changes['ip_address']['new'], '192.168.10.2')



class TestHistoryServiceAssetServiceIntegration(TestCase):
    """Test cases for HistoryService integration with AssetService methods."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create IP range and addresses
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        self.ip1 = IPAddress.objects.create(
            address="192.168.10.1",
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        # Create OS
        self.os = OperatingSystem.objects.create(name="Windows 10")
    
    def test_create_freed_asset_records_history(self):
        """Test that create_freed_asset records creation history with freed status."""
        from assets.services.asset_service import AssetService
        
        # Create freed asset
        data = {
            'asset_tag': 'BIDC_FREED001',
            'system_type': 'Desktop',
            'operating_system': self.os,
            'health_status': 'healthy',
            'manufacturer': 'Dell',
            'particulars': 'Test freed asset'
        }
        
        asset = AssetService.create_freed_asset(data, self.user)
        
        # Check that history entry was created
        history_entries = AssetHistory.objects.filter(asset=asset)
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        self.assertEqual(entry.event_type, 'created')
        self.assertEqual(entry.user, 'testuser')
        self.assertIsNotNone(entry.timestamp)
        
        # Check that status is captured as 'freed'
        changes = entry.changes
        self.assertIn('status', changes)
        self.assertEqual(changes['status']['new'], 'freed')
        
        # Check other fields
        self.assertIn('asset_tag', changes)
        self.assertEqual(changes['asset_tag']['new'], 'BIDC_FREED001')
        
        self.assertIn('system_type', changes)
        self.assertEqual(changes['system_type']['new'], 'Desktop')
        
        self.assertIn('health_status', changes)
        self.assertEqual(changes['health_status']['new'], 'healthy')
    
    def test_create_scrapped_asset_records_history(self):
        """Test that create_scrapped_asset records creation history with scrapped status."""
        from assets.services.asset_service import AssetService
        
        # Create scrapped asset
        data = {
            'asset_tag': 'BIDC_SCRAPPED001',
            'system_type': 'Laptop',
            'operating_system': self.os,
            'manufacturer': 'HP',
            'particulars': 'Test scrapped asset',
            'scrapping_reason': 'Hardware failure'
        }
        
        asset = AssetService.create_scrapped_asset(data, self.user)
        
        # Check that history entry was created
        history_entries = AssetHistory.objects.filter(asset=asset)
        self.assertEqual(history_entries.count(), 1)
        
        entry = history_entries.first()
        self.assertEqual(entry.event_type, 'created')
        self.assertEqual(entry.user, 'testuser')
        self.assertIsNotNone(entry.timestamp)
        
        # Check that status is captured as 'scrapped'
        changes = entry.changes
        self.assertIn('status', changes)
        self.assertEqual(changes['status']['new'], 'scrapped')
        
        # Check other fields
        self.assertIn('asset_tag', changes)
        self.assertEqual(changes['asset_tag']['new'], 'BIDC_SCRAPPED001')
        
        self.assertIn('system_type', changes)
        self.assertEqual(changes['system_type']['new'], 'Laptop')
        
        self.assertIn('scrapping_reason', changes)
        self.assertEqual(changes['scrapping_reason']['new'], 'Hardware failure')


class TestHistoryServiceCSVExport(TestCase):
    """Test cases for HistoryService CSV export functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create user
        self.user = User.objects.create_user(username='testuser', password='password')
        
        # Create IP range and addresses
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        self.ip1 = IPAddress.objects.create(
            address="192.168.10.1",
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        # Create OS and Team
        self.os = OperatingSystem.objects.create(name="Windows 10")
        self.team = Team.objects.create(name="IT Department")
        
        # Create an asset with history
        self.asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe',
            team=self.team,
            manufacturer='Dell'
        )
    
    def test_format_value_for_export_none(self):
        """Test that _format_value_for_export handles None values."""
        result = HistoryService._format_value_for_export(None)
        self.assertEqual(result, 'Not set')
    
    def test_format_value_for_export_empty_string(self):
        """Test that _format_value_for_export handles empty strings."""
        result = HistoryService._format_value_for_export('')
        self.assertEqual(result, 'Not set')
    
    def test_format_value_for_export_normal_value(self):
        """Test that _format_value_for_export handles normal values."""
        result = HistoryService._format_value_for_export('Test Value')
        self.assertEqual(result, 'Test Value')
    
    def test_format_value_for_export_number(self):
        """Test that _format_value_for_export handles numbers."""
        result = HistoryService._format_value_for_export(123)
        self.assertEqual(result, '123')
    
    def test_export_history_to_csv_returns_http_response(self):
        """Test that export_history_to_csv returns an HttpResponse."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Check response type and content type
        from django.http import HttpResponse
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
    
    def test_export_history_to_csv_filename_format(self):
        """Test that export_history_to_csv generates correct filename."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Check filename format
        content_disposition = response['Content-Disposition']
        self.assertIn('attachment', content_disposition)
        self.assertIn('asset_history_BIDC001_', content_disposition)
        self.assertIn('.csv', content_disposition)
    
    def test_export_history_to_csv_header_row(self):
        """Test that export_history_to_csv includes correct header row."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        lines = content.split('\r\n')
        
        # Check header row
        header = lines[0]
        self.assertEqual(header, 'Timestamp,Event Type,User,Field,Previous Value,New Value,Notes')
    
    def test_export_history_to_csv_includes_all_changes(self):
        """Test that export_history_to_csv includes all field changes."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        lines = content.split('\r\n')
        
        # Should have header + multiple data rows (one per field change) + empty line at end
        self.assertGreater(len(lines), 2)
        
        # Check that some expected fields are in the CSV
        csv_content = '\r\n'.join(lines)
        self.assertIn('Asset Tag', csv_content)
        self.assertIn('System Type', csv_content)
        self.assertIn('Assigned To', csv_content)
    
    def test_export_history_to_csv_formats_timestamp(self):
        """Test that export_history_to_csv formats timestamps correctly."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        lines = content.split('\r\n')
        
        # Check timestamp format in first data row
        if len(lines) > 1:
            first_data_row = lines[1]
            # Timestamp should be in format YYYY-MM-DD HH:MM:SS
            import re
            timestamp_pattern = r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'
            self.assertRegex(first_data_row, timestamp_pattern)
    
    def test_export_history_to_csv_includes_event_type(self):
        """Test that export_history_to_csv includes event type display name."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should include "Created" (display name for 'created' event type)
        self.assertIn('Created', content)
    
    def test_export_history_to_csv_includes_username(self):
        """Test that export_history_to_csv includes username."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should include username
        self.assertIn('testuser', content)
    
    def test_export_history_to_csv_with_filters(self):
        """Test that export_history_to_csv applies filters correctly."""
        # Create multiple history entries with different event types
        HistoryService.record_creation(self.asset, self.user)
        
        # Update the asset
        old_values = {}
        for field in HistoryService.TRACKED_FIELDS:
            old_values[field] = HistoryService._get_field_value(self.asset, field)
        
        self.asset.assigned_to = 'Jane Smith'
        self.asset.save()
        HistoryService.record_update(self.asset, old_values, self.user)
        
        # Export with filter for only 'created' events
        filters = {'event_type': 'created'}
        response = HistoryService.export_history_to_csv(self.asset, filters)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should include "Created" but not "Updated"
        self.assertIn('Created', content)
        self.assertNotIn('Updated', content)
    
    def test_export_history_to_csv_with_notes(self):
        """Test that export_history_to_csv includes notes when present."""
        # Create a status change with notes
        self.asset.status = 'scrapped'
        self.asset.save()
        HistoryService.record_status_change(self.asset, 'scrapped', self.user, notes='Hardware failure')
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should include the notes
        self.assertIn('Hardware failure', content)
    
    def test_export_history_to_csv_empty_history(self):
        """Test that export_history_to_csv handles assets with no history."""
        # Create a new asset without recording history
        new_asset = Asset.objects.create(
            asset_tag='BIDC999',
            system_type='Laptop',
            operating_system=self.os,
            status='active'
        )
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(new_asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        lines = content.split('\r\n')
        
        # Should only have header row + empty line
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0], 'Timestamp,Event Type,User,Field,Previous Value,New Value,Notes')
    
    def test_export_history_to_csv_entry_without_changes(self):
        """Test that export_history_to_csv handles entries without field changes."""
        # Manually create a history entry without changes
        AssetHistory.objects.create(
            asset=self.asset,
            event_type='created',
            user='testuser',
            changes={},
            notes='Test entry without changes'
        )
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        lines = content.split('\r\n')
        
        # Should have header + 1 data row + empty line
        self.assertEqual(len(lines), 3)
        
        # Check that the row has empty field columns but includes notes
        data_row = lines[1]
        self.assertIn('Test entry without changes', data_row)
    
    def test_export_history_to_csv_uses_field_labels(self):
        """Test that export_history_to_csv uses human-readable field labels."""
        # Create a history entry
        HistoryService.record_creation(self.asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(self.asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should use field labels from FIELD_LABELS dict
        self.assertIn('Asset Tag', content)  # Not 'asset_tag'
        self.assertIn('System Type', content)  # Not 'system_type'
        self.assertIn('Operating System', content)  # Not 'operating_system'
    
    def test_export_history_to_csv_formats_none_as_not_set(self):
        """Test that export_history_to_csv formats None values as 'Not set'."""
        # Create an asset with some null fields
        minimal_asset = Asset.objects.create(
            asset_tag='BIDC998',
            system_type='Desktop',
            operating_system=self.os,
            status='active'
        )
        
        # Record creation
        HistoryService.record_creation(minimal_asset, self.user)
        
        # Export to CSV
        response = HistoryService.export_history_to_csv(minimal_asset)
        
        # Decode content
        content = response.content.decode('utf-8')
        
        # Should have "Not set" for fields that were None/empty
        self.assertIn('Not set', content)
