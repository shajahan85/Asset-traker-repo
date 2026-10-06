"""
Tests for guest IP URL routes.
"""
from django.test import TestCase
from django.urls import reverse, resolve
from assets.views import GuestIPAssignView, GuestIPReleaseView


class GuestIPURLTests(TestCase):
    """Test guest IP URL configuration."""
    
    def test_guest_ip_assign_url_resolves(self):
        """Test that guest_ip_assign URL resolves to correct view."""
        url = reverse('guest_ip_assign')
        self.assertEqual(url, '/assets/guest-ip/assign/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, GuestIPAssignView)
    
    def test_guest_ip_release_url_resolves(self):
        """Test that guest_ip_release URL resolves to correct view."""
        url = reverse('guest_ip_release')
        self.assertEqual(url, '/assets/guest-ip/release/')
        resolver = resolve(url)
        self.assertEqual(resolver.func.view_class, GuestIPReleaseView)
    
    def test_guest_ip_assign_url_name(self):
        """Test that guest_ip_assign URL name exists and is correct."""
        url = reverse('guest_ip_assign')
        self.assertIsNotNone(url)
        self.assertIn('guest-ip/assign', url)
    
    def test_guest_ip_release_url_name(self):
        """Test that guest_ip_release URL name exists and is correct."""
        url = reverse('guest_ip_release')
        self.assertIsNotNone(url)
        self.assertIn('guest-ip/release', url)
