"""
Test script to verify history links are present in templates.
This tests tasks 9.1, 9.2, 9.3, and 9.4 of the asset-history-tracking spec.
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from assets.models import Asset, OperatingSystem, Team, IPAddress
from django.urls import reverse


class HistoryLinksTestCase(TestCase):
    """Test that history links appear in all required templates."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            is_staff=True
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create test data
        self.os = OperatingSystem.objects.create(name='Windows 10')
        self.team = Team.objects.create(name='IT')
        
        # Create an active asset
        self.active_asset = Asset.objects.create(
            asset_tag='BIDC-001',
            system_type='Desktop',
            operating_system=self.os,
            status='active',
            assigned_to='John Doe',
            team=self.team
        )
        
        # Create a freed asset
        self.freed_asset = Asset.objects.create(
            asset_tag='BIDC-002',
            system_type='Laptop',
            operating_system=self.os,
            status='freed',
            health_status='healthy'
        )
        
        # Create a scrapped asset
        self.scrapped_asset = Asset.objects.create(
            asset_tag='BIDC-003',
            system_type='All-in-One PC',
            operating_system=self.os,
            status='scrapped',
            scrapping_reason='Hardware failure'
        )
    
    def test_task_9_1_asset_detail_has_history_link(self):
        """Task 9.1: Verify asset_detail (form) page has View History button."""
        response = self.client.get(reverse('asset_update', args=[self.active_asset.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Check that the View History link is present
        self.assertContains(response, 'View History')
        self.assertContains(response, reverse('asset_history', args=[self.active_asset.pk]))
    
    def test_task_9_2_asset_list_has_history_links(self):
        """Task 9.2: Verify asset_list.html has history icon/link column."""
        response = self.client.get(reverse('asset_list'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the History column header is present
        self.assertContains(response, '<th>History</th>')
        
        # Check that the history link is present for the active asset
        self.assertContains(response, reverse('asset_history', args=[self.active_asset.pk]))
        self.assertContains(response, '📋')
    
    def test_task_9_3_freed_list_has_history_links(self):
        """Task 9.3: Verify freed_list.html has history icon/link column."""
        response = self.client.get(reverse('freed_systems'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the History column header is present
        self.assertContains(response, '<th>History</th>')
        
        # Check that the history link is present for the freed asset
        self.assertContains(response, reverse('asset_history', args=[self.freed_asset.pk]))
        self.assertContains(response, '📋')
    
    def test_task_9_4_scrapped_list_has_history_links(self):
        """Task 9.4: Verify scrapped_list.html has history icon/link column."""
        response = self.client.get(reverse('scrapped_items'))
        self.assertEqual(response.status_code, 200)
        
        # Check that the History column header is present
        self.assertContains(response, '<th>History</th>')
        
        # Check that the history link is present for the scrapped asset
        self.assertContains(response, reverse('asset_history', args=[self.scrapped_asset.pk]))
        self.assertContains(response, '📋')
    
    def test_all_history_links_point_to_same_url_pattern(self):
        """Verify all history links use the correct URL pattern."""
        # Get all relevant pages
        asset_detail = self.client.get(reverse('asset_update', args=[self.active_asset.pk]))
        asset_list = self.client.get(reverse('asset_list'))
        freed_list = self.client.get(reverse('freed_systems'))
        scrapped_list = self.client.get(reverse('scrapped_items'))
        
        # All should return 200
        self.assertEqual(asset_detail.status_code, 200)
        self.assertEqual(asset_list.status_code, 200)
        self.assertEqual(freed_list.status_code, 200)
        self.assertEqual(scrapped_list.status_code, 200)
        
        # All should contain asset_history URL pattern
        self.assertContains(asset_detail, 'asset_history')
        self.assertContains(asset_list, 'asset_history')
        self.assertContains(freed_list, 'asset_history')
        self.assertContains(scrapped_list, 'asset_history')


if __name__ == '__main__':
    import django
    import os
    import sys
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['__main__'])
    sys.exit(bool(failures))
