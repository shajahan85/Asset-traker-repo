"""
Integration tests for guest IP view access control.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class GuestIPViewAccessTests(TestCase):
    """Test access control for guest IP views."""
    
    def setUp(self):
        """Set up test client and users."""
        self.client = Client()
        
        # Create admin user (staff)
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            email='admin@test.com',
            is_staff=True
        )
        
        # Create regular user (non-staff)
        self.regular_user = User.objects.create_user(
            username='user',
            password='userpass123',
            email='user@test.com',
            is_staff=False
        )
    
    def test_guest_ip_assign_requires_authentication(self):
        """Test that guest IP assign view requires authentication."""
        url = reverse('guest_ip_assign')
        response = self.client.post(url)
        # Should redirect to login or return 302/403
        self.assertIn(response.status_code, [302, 403])
    
    def test_guest_ip_release_requires_authentication(self):
        """Test that guest IP release view requires authentication."""
        url = reverse('guest_ip_release')
        response = self.client.post(url)
        # Should redirect to login or return 302/403
        self.assertIn(response.status_code, [302, 403])
    
    def test_guest_ip_assign_requires_admin(self):
        """Test that guest IP assign view requires admin role."""
        self.client.login(username='user', password='userpass123')
        url = reverse('guest_ip_assign')
        response = self.client.post(url)
        # Should deny access (403 or redirect)
        self.assertIn(response.status_code, [302, 403])
    
    def test_guest_ip_release_requires_admin(self):
        """Test that guest IP release view requires admin role."""
        self.client.login(username='user', password='userpass123')
        url = reverse('guest_ip_release')
        response = self.client.post(url)
        # Should deny access (403 or redirect)
        self.assertIn(response.status_code, [302, 403])
    
    def test_guest_ip_assign_admin_access(self):
        """Test that admin can access guest IP assign view."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('guest_ip_assign')
        response = self.client.post(url)
        # Should not be denied (will fail validation but not auth)
        # Expect 400 due to missing data, not 403
        self.assertEqual(response.status_code, 400)
    
    def test_guest_ip_release_admin_access(self):
        """Test that admin can access guest IP release view."""
        self.client.login(username='admin', password='adminpass123')
        url = reverse('guest_ip_release')
        response = self.client.post(url)
        # Should not be denied (will fail validation but not auth)
        # Expect 400 due to missing data, not 403
        self.assertEqual(response.status_code, 400)
