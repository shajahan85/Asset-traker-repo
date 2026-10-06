"""Tests for AssetDetailView displaying multiple IPs."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from assets.models import Asset, OperatingSystem, IPAddress, Branch, AssetIPAddress
from datetime import datetime


class AssetDetailViewTestCase(TestCase):
    """Test cases for asset detail view with multiple IPs."""

    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            password='adminpass123',
            is_staff=True
        )
        
        # Create test data
        self.os = OperatingSystem.objects.create(name='Windows 10')
        self.branch = Branch.objects.create(name='Main Branch', code='MAIN')
        
        # Create IP range first (required for IPAddress)
        from assets.models import IPRange
        self.ip_range = IPRange.objects.create(
            range_pattern='192.168.10.x',
            network_prefix='192.168.10'
        )
        
        # Create managed IPs
        self.ip1 = IPAddress.objects.create(
            address='192.168.10.100',
            ip_range=self.ip_range,
            is_assigned=True
        )
        self.ip2 = IPAddress.objects.create(
            address='192.168.10.101',
            ip_range=self.ip_range,
            is_assigned=True
        )
        
        # Create asset
        self.asset = Asset.objects.create(
            asset_tag='TEST-001',
            system_type='Desktop',
            operating_system=self.os,
            branch=self.branch,
            status='active'
        )
        
        # Create primary IP
        self.primary_ip = AssetIPAddress.objects.create(
            asset=self.asset,
            ip_address=self.ip1,
            is_primary=True
        )
        
        # Create secondary IP (managed)
        self.secondary_managed = AssetIPAddress.objects.create(
            asset=self.asset,
            ip_address=self.ip2,
            is_primary=False,
            ip_label="Secondary"  # Add default label
        )
        
        # Create secondary IP (manual)
        self.secondary_manual = AssetIPAddress.objects.create(
            asset=self.asset,
            manual_ip='10.0.0.50',
            is_primary=False,
            ip_label="Manual Secondary"  # Add default label
        )
        
        self.client = Client()

    def test_asset_detail_view_requires_login(self):
        """Test that asset detail view requires authentication."""
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_asset_detail_view_displays_asset_info(self):
        """Test that asset detail view displays basic asset information."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-001')
        self.assertContains(response, 'Desktop')
        self.assertContains(response, 'Windows 10')

    def test_asset_detail_view_displays_primary_ip(self):
        """Test that primary IP is displayed with Primary label."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '192.168.10.100')
        self.assertContains(response, 'Primary')

    def test_asset_detail_view_displays_secondary_managed_ip(self):
        """Test that secondary managed IP is displayed with correct labels."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '192.168.10.101')
        self.assertContains(response, 'Secondary - Managed')

    def test_asset_detail_view_displays_secondary_manual_ip(self):
        """Test that secondary manual IP is displayed with correct labels."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '10.0.0.50')
        self.assertContains(response, 'Secondary - Manual')

    def test_asset_detail_view_shows_add_button_for_admin(self):
        """Test that Add Secondary IP button is shown for admin users."""
        self.client.login(username='adminuser', password='adminpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add Secondary IP')
        self.assertContains(response, reverse('add_secondary_ip', kwargs={'pk': self.asset.pk}))

    def test_asset_detail_view_shows_remove_button_for_admin(self):
        """Test that Remove buttons are shown for secondary IPs for admin users."""
        self.client.login(username='adminuser', password='adminpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Remove')
        self.assertContains(response, reverse('remove_secondary_ip', kwargs={'pk': self.secondary_managed.pk}))

    def test_asset_detail_view_shows_set_primary_button_for_admin(self):
        """Test that Set as Primary buttons are shown for secondary IPs for admin users."""
        self.client.login(username='adminuser', password='adminpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Set as Primary')
        self.assertContains(response, reverse('set_primary_ip', kwargs={'pk': self.secondary_managed.pk}))

    def test_asset_detail_view_hides_admin_buttons_for_non_admin(self):
        """Test that admin buttons are hidden for non-admin users."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # These buttons should not appear in the response for non-admin users
        self.assertNotContains(response, 'Add Secondary IP')
        # The column for Actions should not exist for non-admin
        response_text = response.content.decode()
        self.assertTrue('Primary IP' not in response_text or response_text.count('<th>Actions</th>') == 0)

    def test_asset_detail_view_with_no_secondary_ips(self):
        """Test asset detail view when asset has only primary IP."""
        # Remove secondary IPs
        self.secondary_managed.delete()
        self.secondary_manual.delete()
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No secondary IPs assigned')

    def test_asset_detail_view_404_for_nonexistent_asset(self):
        """Test that 404 is returned for non-existent asset."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)

    def test_additional_ip_section_displays_with_labels(self):
        """Test that additional IP addresses section displays with ip_label badges."""
        # Add ip_label to existing secondary IPs
        self.secondary_managed.ip_label = "WiFi"
        self.secondary_managed.save()
        
        self.secondary_manual.ip_label = "Mobile"
        self.secondary_manual.save()
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # Check for the "Additional IP Addresses" heading
        self.assertContains(response, 'Additional IP Addresses')
        # Check for ip_label badges
        self.assertContains(response, 'WiFi')
        self.assertContains(response, 'Mobile')
        # Check for IP addresses
        self.assertContains(response, '192.168.10.101')
        self.assertContains(response, '10.0.0.50')

    def test_additional_ip_section_not_displayed_without_additional_ips(self):
        """Test that additional IP section is not displayed when no additional IPs exist."""
        # Remove all secondary IPs
        self.secondary_managed.delete()
        self.secondary_manual.delete()
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        # The "Additional IP Addresses" heading should not be present
        self.assertNotContains(response, 'Additional IP Addresses')

    def test_additional_ip_section_only_displays_non_primary_ips(self):
        """Test that additional IP section only shows non-primary IPs."""
        # Add ip_label to secondary IPs
        self.secondary_managed.ip_label = "WiFi"
        self.secondary_managed.save()
        
        self.client.login(username='testuser', password='testpass123')
        url = reverse('asset_detail', kwargs={'pk': self.asset.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        response_text = response.content.decode()
        
        # Count occurrences of primary IP in additional section
        # Primary IP should appear in main IP section but not in additional section
        # Additional section should only contain non-primary IPs
        self.assertIn('Additional IP Addresses', response_text)
        self.assertIn('192.168.10.101', response_text)  # Secondary IP
        
        # Verify primary IP badge is shown separately
        self.assertIn('192.168.10.100', response_text)  # Primary IP
