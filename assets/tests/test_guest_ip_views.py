"""
Unit tests for guest IP assignment and release views.
"""
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from assets.models import IPAddress, IPRange
from django.utils import timezone


class TestGuestIPAssignView(TestCase):
    """Test cases for GuestIPAssignView."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user (non-admin)
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_staff=False
        )
        
        # Create IP range and free IP address
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        self.free_ip = IPAddress.objects.create(
            address="192.168.10.100",
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        # Create already assigned IP
        self.assigned_ip = IPAddress.objects.create(
            address="192.168.10.101",
            ip_range=self.ip_range,
            is_assigned=True
        )
        
        self.client = Client()
    
    def test_assign_guest_ip_requires_admin(self):
        """Test that guest IP assignment requires admin authentication."""
        # Try without login - should redirect to login or be forbidden
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': 'John Doe'
        })
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
        
        # Try with regular user - should be forbidden
        self.client.login(username='regular', password='testpass123')
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': 'John Doe'
        })
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
        
        self.client.logout()
    
    def test_assign_guest_ip_success(self):
        """Test successful guest IP assignment."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': 'John Doe'
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['guest_name'], 'John Doe')
        self.assertEqual(data['ip_address'], '192.168.10.100')
        
        # Verify database changes
        self.free_ip.refresh_from_db()
        self.assertTrue(self.free_ip.is_assigned)
        self.assertEqual(self.free_ip.guest_name, 'John Doe')
        self.assertEqual(self.free_ip.guest_assigned_by, 'admin')
        self.assertIsNotNone(self.free_ip.guest_assigned_date)
    
    def test_assign_guest_ip_missing_ip_address(self):
        """Test that missing IP address returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'guest_name': 'John Doe'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('required', data['error'].lower())
    
    def test_assign_guest_ip_missing_guest_name(self):
        """Test that missing guest name returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('required', data['error'].lower())
    
    def test_assign_guest_ip_empty_guest_name(self):
        """Test that empty guest name returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': '   '  # Only whitespace
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
    
    def test_assign_guest_ip_invalid_ip_address(self):
        """Test that invalid IP address returns 404."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': '192.168.99.999',  # Non-existent IP
            'guest_name': 'John Doe'
        })
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    def test_assign_guest_ip_already_assigned(self):
        """Test that assigning already assigned IP returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.assigned_ip.address,
            'guest_name': 'John Doe'
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('already assigned', data['error'].lower())
    
    def test_assign_guest_ip_strips_whitespace(self):
        """Test that guest name whitespace is stripped."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': '  John Doe  '
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Verify whitespace was stripped
        self.free_ip.refresh_from_db()
        self.assertEqual(self.free_ip.guest_name, 'John Doe')


class TestGuestIPReleaseView(TestCase):
    """Test cases for GuestIPReleaseView."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user (non-admin)
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_staff=False
        )
        
        # Create IP range
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        
        # Create guest-assigned IP
        self.guest_ip = IPAddress.objects.create(
            address="192.168.10.100",
            ip_range=self.ip_range,
            is_assigned=True,
            guest_name='John Doe',
            guest_assigned_by='admin',
            guest_assigned_date=timezone.now()
        )
        
        # Create non-guest assigned IP
        self.regular_ip = IPAddress.objects.create(
            address="192.168.10.101",
            ip_range=self.ip_range,
            is_assigned=True
        )
        
        self.client = Client()
    
    def test_release_guest_ip_requires_admin(self):
        """Test that guest IP release requires admin authentication."""
        # Try without login - should redirect to login or be forbidden
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': self.guest_ip.id
        })
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
        
        # Try with regular user - should be forbidden
        self.client.login(username='regular', password='testpass123')
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': self.guest_ip.id
        })
        self.assertIn(response.status_code, [302, 403])  # Redirect or forbidden
        
        self.client.logout()
    
    def test_release_guest_ip_success(self):
        """Test successful guest IP release."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': self.guest_ip.id
        })
        
        self.assertEqual(response.status_code, 200)
        
        # Parse JSON response
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['ip_address'], '192.168.10.100')
        
        # Verify database changes
        self.guest_ip.refresh_from_db()
        self.assertFalse(self.guest_ip.is_assigned)
        self.assertIsNone(self.guest_ip.guest_name)
        self.assertIsNone(self.guest_ip.guest_assigned_by)
        self.assertIsNone(self.guest_ip.guest_assigned_date)
        self.assertIsNotNone(self.guest_ip.freed_date)
    
    def test_release_guest_ip_missing_ip_id(self):
        """Test that missing IP ID returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/release/', {})
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('required', data['error'].lower())
    
    def test_release_guest_ip_invalid_ip_id(self):
        """Test that invalid IP ID returns 404."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': 99999  # Non-existent ID
        })
        
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('not found', data['error'].lower())
    
    def test_release_guest_ip_not_guest_assigned(self):
        """Test that releasing non-guest IP returns error."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': self.regular_ip.id
        })
        
        self.assertEqual(response.status_code, 400)
        
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('not assigned to a guest', data['error'].lower())


class TestGuestIPCSRFProtection(TestCase):
    """Test CSRF protection on guest IP views."""
    
    def setUp(self):
        """Set up test data."""
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        
        self.ip_range = IPRange.objects.create(
            range_pattern="192.168.10.x",
            network_prefix="192.168.10"
        )
        
        self.free_ip = IPAddress.objects.create(
            address="192.168.10.100",
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        self.client = Client(enforce_csrf_checks=True)
    
    def test_guest_ip_assign_requires_csrf_token(self):
        """Test that CSRF protection is enforced on assignment."""
        self.client.login(username='admin', password='testpass123')
        
        # POST without CSRF token should fail
        response = self.client.post('/assets/guest-ip/assign/', {
            'ip_address': self.free_ip.address,
            'guest_name': 'John Doe'
        })
        
        self.assertEqual(response.status_code, 403)  # CSRF failure
    
    def test_guest_ip_release_requires_csrf_token(self):
        """Test that CSRF protection is enforced on release."""
        self.client.login(username='admin', password='testpass123')
        
        # POST without CSRF token should fail
        response = self.client.post('/assets/guest-ip/release/', {
            'ip_id': self.free_ip.id
        })
        
        self.assertEqual(response.status_code, 403)  # CSRF failure
