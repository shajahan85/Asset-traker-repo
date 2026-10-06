"""
Unit tests for models.
"""
import pytest
import time
from datetime import datetime, timedelta
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from assets.models import Asset, IPAddress, IPRange, OperatingSystem, AssetIPAddress


class TestAssetModel(TestCase):
    """Test cases for Asset model field constraints."""

    def setUp(self):
        """Set up test data."""
        self.os = OperatingSystem.objects.create(name="Windows 10")
        self.ip_range = IPRange.objects.create(
            range_pattern="10.0.0.x",
            network_prefix="10.0.0"
        )

    def test_manufacturer_max_length_within_limit(self):
        """Test manufacturer field accepts values within max_length=100."""
        asset = Asset.objects.create(
            asset_tag="BIDC100",
            system_type="Desktop",
            operating_system=self.os,
            manufacturer="Dell Technologies"
        )
        asset.full_clean()
        self.assertEqual(asset.manufacturer, "Dell Technologies")

    def test_manufacturer_max_length_at_boundary(self):
        """Test manufacturer field accepts exactly 100 characters."""
        value = "A" * 100
        asset = Asset.objects.create(
            asset_tag="BIDC101",
            system_type="Desktop",
            operating_system=self.os,
            manufacturer=value
        )
        asset.full_clean()
        self.assertEqual(asset.manufacturer, value)

    def test_manufacturer_max_length_exceeds_limit(self):
        """Test manufacturer field rejects values exceeding max_length=100."""
        value = "A" * 101
        asset = Asset(
            asset_tag="BIDC102",
            system_type="Desktop",
            operating_system=self.os,
            manufacturer=value
        )
        with self.assertRaises(ValidationError):
            asset.full_clean()

    def test_scrapping_reason_accepts_multiline_text(self):
        """Test scrapping_reason TextField accepts multi-line text."""
        multiline_reason = "Hardware failure.\nMotherboard burned out.\nNot economical to repair."
        asset = Asset.objects.create(
            asset_tag="BIDC103",
            system_type="Laptop",
            operating_system=self.os,
            scrapping_reason=multiline_reason
        )
        asset.refresh_from_db()
        self.assertEqual(asset.scrapping_reason, multiline_reason)

    def test_scrapping_reason_accepts_long_text(self):
        """Test scrapping_reason TextField accepts long text content."""
        long_reason = "Detailed reason. " * 200
        asset = Asset.objects.create(
            asset_tag="BIDC104",
            system_type="Desktop",
            operating_system=self.os,
            scrapping_reason=long_reason
        )
        asset.refresh_from_db()
        self.assertEqual(asset.scrapping_reason, long_reason)


class TestIPAddressModel(TestCase):
    """Test cases for IPAddress model freed_date field."""

    def setUp(self):
        """Set up test data."""
        self.ip_range = IPRange.objects.create(
            range_pattern="10.0.1.x",
            network_prefix="10.0.1"
        )

    def test_freed_date_accepts_datetime(self):
        """Test freed_date field accepts datetime values."""
        now = timezone.now()
        ip = IPAddress.objects.create(
            address="10.0.1.1",
            ip_range=self.ip_range,
            freed_date=now
        )
        ip.refresh_from_db()
        self.assertIsNotNone(ip.freed_date)
        self.assertEqual(ip.freed_date.year, now.year)
        self.assertEqual(ip.freed_date.month, now.month)
        self.assertEqual(ip.freed_date.day, now.day)

    def test_freed_date_defaults_to_none(self):
        """Test freed_date is None by default."""
        ip = IPAddress.objects.create(
            address="10.0.1.2",
            ip_range=self.ip_range
        )
        self.assertIsNone(ip.freed_date)

    def test_freed_date_accepts_specific_datetime(self):
        """Test freed_date stores a specific datetime accurately."""
        specific_time = timezone.make_aware(datetime(2024, 6, 15, 14, 30, 0))
        ip = IPAddress.objects.create(
            address="10.0.1.3",
            ip_range=self.ip_range,
            freed_date=specific_time
        )
        ip.refresh_from_db()
        self.assertEqual(ip.freed_date, specific_time)

    def test_guest_name_defaults_to_none(self):
        """Test guest_name is None by default."""
        ip = IPAddress.objects.create(
            address="10.0.1.4",
            ip_range=self.ip_range
        )
        self.assertIsNone(ip.guest_name)

    def test_guest_assigned_date_defaults_to_none(self):
        """Test guest_assigned_date is None by default."""
        ip = IPAddress.objects.create(
            address="10.0.1.5",
            ip_range=self.ip_range
        )
        self.assertIsNone(ip.guest_assigned_date)

    def test_guest_assigned_by_defaults_to_none(self):
        """Test guest_assigned_by is None by default."""
        ip = IPAddress.objects.create(
            address="10.0.1.6",
            ip_range=self.ip_range
        )
        self.assertIsNone(ip.guest_assigned_by)

    def test_guest_name_accepts_string(self):
        """Test guest_name field accepts string values."""
        ip = IPAddress.objects.create(
            address="10.0.1.7",
            ip_range=self.ip_range,
            guest_name="John Doe"
        )
        ip.refresh_from_db()
        self.assertEqual(ip.guest_name, "John Doe")

    def test_guest_assigned_date_accepts_datetime(self):
        """Test guest_assigned_date field accepts datetime values."""
        now = timezone.now()
        ip = IPAddress.objects.create(
            address="10.0.1.8",
            ip_range=self.ip_range,
            guest_assigned_date=now
        )
        ip.refresh_from_db()
        self.assertIsNotNone(ip.guest_assigned_date)
        self.assertEqual(ip.guest_assigned_date.year, now.year)

    def test_guest_assigned_by_accepts_string(self):
        """Test guest_assigned_by field accepts string values."""
        ip = IPAddress.objects.create(
            address="10.0.1.9",
            ip_range=self.ip_range,
            guest_assigned_by="admin_user"
        )
        ip.refresh_from_db()
        self.assertEqual(ip.guest_assigned_by, "admin_user")

    def test_is_guest_assigned_returns_false_when_no_guest(self):
        """Test is_guest_assigned() returns False when guest_name is None."""
        ip = IPAddress.objects.create(
            address="10.0.1.10",
            ip_range=self.ip_range
        )
        self.assertFalse(ip.is_guest_assigned())

    def test_is_guest_assigned_returns_false_when_guest_name_empty(self):
        """Test is_guest_assigned() returns False when guest_name is empty string."""
        ip = IPAddress.objects.create(
            address="10.0.1.11",
            ip_range=self.ip_range,
            guest_name=""
        )
        self.assertFalse(ip.is_guest_assigned())

    def test_is_guest_assigned_returns_true_when_guest_assigned(self):
        """Test is_guest_assigned() returns True when guest_name is set."""
        ip = IPAddress.objects.create(
            address="10.0.1.12",
            ip_range=self.ip_range,
            guest_name="Jane Smith"
        )
        self.assertTrue(ip.is_guest_assigned())

    def test_guest_fields_can_be_updated(self):
        """Test all guest fields can be set and updated."""
        now = timezone.now()
        ip = IPAddress.objects.create(
            address="10.0.1.13",
            ip_range=self.ip_range
        )
        
        # Assign to guest
        ip.guest_name = "Bob Johnson"
        ip.guest_assigned_date = now
        ip.guest_assigned_by = "admin1"
        ip.save()
        ip.refresh_from_db()
        
        self.assertEqual(ip.guest_name, "Bob Johnson")
        self.assertIsNotNone(ip.guest_assigned_date)
        self.assertEqual(ip.guest_assigned_by, "admin1")
        self.assertTrue(ip.is_guest_assigned())
        
        # Clear guest assignment
        ip.guest_name = None
        ip.guest_assigned_date = None
        ip.guest_assigned_by = None
        ip.save()
        ip.refresh_from_db()
        
        self.assertIsNone(ip.guest_name)
        self.assertIsNone(ip.guest_assigned_date)
        self.assertIsNone(ip.guest_assigned_by)
        self.assertFalse(ip.is_guest_assigned())


class TestAssetIPAddressTimestamps(TestCase):
    """Test cases for AssetIPAddress created_at timestamp field."""

    def setUp(self):
        """Set up test data."""
        self.os = OperatingSystem.objects.create(name="Windows 10")
        self.asset = Asset.objects.create(
            asset_tag="BIDC200",
            system_type="Desktop",
            operating_system=self.os
        )
        self.ip_range = IPRange.objects.create(
            range_pattern="10.0.2.x",
            network_prefix="10.0.2"
        )
        self.managed_ip = IPAddress.objects.create(
            address="10.0.2.50",
            ip_range=self.ip_range
        )

    def test_created_at_is_set_automatically_on_creation(self):
        """Test that created_at timestamp is automatically set when creating a new IP assignment.
        
        **Validates: Requirements 1.12.1, 1.12.2**
        """
        before_creation = timezone.now()
        
        # Create new IP assignment
        ip_assoc = AssetIPAddress.objects.create(
            asset=self.asset,
            ip_address=self.managed_ip,
            is_primary=True
        )
        
        after_creation = timezone.now()
        
        # Verify created_at is set
        self.assertIsNotNone(ip_assoc.created_at)
        
        # Verify created_at is within expected time range
        self.assertGreaterEqual(ip_assoc.created_at, before_creation)
        self.assertLessEqual(ip_assoc.created_at, after_creation)

    def test_created_at_uses_current_timestamp(self):
        """Test that new IP assignments get the current timestamp.
        
        **Validates: Requirement 1.12.2**
        """
        # Create first IP assignment
        ip_assoc1 = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.100",
            is_primary=True
        )
        
        # Wait a moment
        time.sleep(0.1)
        
        # Create another asset and assignment
        asset2 = Asset.objects.create(
            asset_tag="BIDC201",
            system_type="Laptop",
            operating_system=self.os
        )
        ip_assoc2 = AssetIPAddress.objects.create(
            asset=asset2,
            manual_ip="192.168.1.101",
            is_primary=True
        )
        
        # Verify the second assignment has a later timestamp
        self.assertLess(ip_assoc1.created_at, ip_assoc2.created_at)

    def test_created_at_preserved_during_updates(self):
        """Test that existing timestamps are preserved when updating AssetIPAddress records.
        
        **Validates: Requirement 1.12.1, 1.12.2**
        """
        # Create IP assignment
        ip_assoc = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.102",
            is_primary=False,
            ip_label="WiFi"
        )
        
        # Store original timestamp
        original_created_at = ip_assoc.created_at
        
        # Wait a moment
        time.sleep(0.1)
        
        # Update the record
        ip_assoc.ip_label = "Mobile"
        ip_assoc.save()
        
        # Refresh from database
        ip_assoc.refresh_from_db()
        
        # Verify created_at has NOT changed
        self.assertEqual(ip_assoc.created_at, original_created_at)

    def test_created_at_preserved_across_multiple_updates(self):
        """Test that created_at remains unchanged through multiple updates.
        
        **Validates: Requirement 1.12.1, 1.12.2**
        """
        # Create IP assignment
        ip_assoc = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.103",
            is_primary=False,
            ip_label="WiFi"
        )
        
        # Store original timestamp
        original_created_at = ip_assoc.created_at
        
        # Perform multiple updates
        for i in range(3):
            time.sleep(0.05)
            ip_assoc.ip_label = f"Label {i}"
            ip_assoc.save()
            ip_assoc.refresh_from_db()
            
            # Verify created_at is still the same
            self.assertEqual(ip_assoc.created_at, original_created_at)

    def test_created_at_field_uses_auto_now_add(self):
        """Test that the created_at field is configured with auto_now_add=True.
        
        **Validates: Requirement 1.12.1**
        """
        # Get the field definition
        field = AssetIPAddress._meta.get_field('created_at')
        
        # Verify it's a DateTimeField
        from django.db.models import DateTimeField
        self.assertIsInstance(field, DateTimeField)
        
        # Verify auto_now_add is True
        self.assertTrue(field.auto_now_add)
        
        # Verify auto_now is False (shouldn't update on save)
        self.assertFalse(field.auto_now)

    def test_created_at_cannot_be_manually_set_on_creation(self):
        """Test that attempting to manually set created_at on creation is ignored.
        
        **Validates: Requirement 1.12.2**
        """
        # Try to create with a specific created_at
        past_time = timezone.now() - timedelta(days=30)
        
        ip_assoc = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.104",
            is_primary=True,
            created_at=past_time  # This should be ignored
        )
        
        # Verify created_at is NOT the manually set value
        # It should be close to the current time
        self.assertNotEqual(ip_assoc.created_at, past_time)
        self.assertGreater(ip_assoc.created_at, past_time)

    def test_multiple_ips_on_same_asset_have_different_timestamps(self):
        """Test that multiple IP assignments to the same asset have distinct timestamps.
        
        **Validates: Requirement 1.12.2**
        """
        # Create primary IP
        primary_ip = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.105",
            is_primary=True
        )
        
        time.sleep(0.1)
        
        # Create additional IP
        additional_ip = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip="192.168.1.106",
            is_primary=False,
            ip_label="WiFi"
        )
        
        # Verify timestamps are different
        self.assertNotEqual(primary_ip.created_at, additional_ip.created_at)
        self.assertLess(primary_ip.created_at, additional_ip.created_at)
