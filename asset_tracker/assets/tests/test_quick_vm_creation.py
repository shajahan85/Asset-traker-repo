"""
Tests for quick VM creation from Free IP page.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from assets.models import Asset, HyperVVM, IPAddress, IPRange, OperatingSystem, Team
import json


class QuickVMCreateViewTest(TestCase):
    """Test QuickVMCreateView functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        
        # Create test OS
        self.os = OperatingSystem.objects.create(name='Windows Server 2019')
        
        # Create test team
        self.team = Team.objects.create(name='IT Team')
        
        # Create test IP range
        self.ip_range = IPRange.objects.create(
            range_pattern='192.168.50.x',
            network_prefix='192.168.50'
        )
        
        # Create test IPs
        self.host_ip = IPAddress.objects.create(
            address='192.168.50.10',
            ip_range=self.ip_range,
            is_assigned=True
        )
        
        self.vm_ip = IPAddress.objects.create(
            address='192.168.50.20',
            ip_range=self.ip_range,
            is_assigned=False
        )
        
        # Create test host asset
        self.host_asset = Asset.objects.create(
            asset_tag='BIDC001',
            system_type='Desktop',
            operating_system=self.os,
            ip_address=self.host_ip,
            team=self.team,
            status='active'
        )
        
        # Link IP to asset
        self.host_ip.assigned_to_asset = self.host_asset
        self.host_ip.save()
        
        # Create client
        self.client = Client()
    
    def test_create_vm_with_valid_data(self):
        """Test VM creation with valid data."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Prepare POST data
        data = {
            'vm_ip': '192.168.50.20',
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'TestVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['vm_name'], 'TestVM')
        
        # Verify VM was created
        vm = HyperVVM.objects.get(name='TestVM')
        self.assertEqual(vm.host_machine, self.host_asset)
        self.assertEqual(vm.ip_address, self.vm_ip)
        
        # Verify IP was assigned
        self.vm_ip.refresh_from_db()
        self.assertTrue(self.vm_ip.is_assigned)
    
    def test_create_vm_with_auto_generated_name(self):
        """Test VM creation with auto-generated name."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Prepare POST data without vm_name
        data = {
            'vm_ip': '192.168.50.20',
            'base_machine_ip': '192.168.50.10',
            'vm_name': ''  # Empty name should trigger auto-generation
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify VM name was auto-generated
        expected_name = 'VM-BIDC001-192.168.50.20'
        self.assertEqual(response_data['vm_name'], expected_name)
        
        # Verify VM was created with correct name
        vm = HyperVVM.objects.get(name=expected_name)
        self.assertEqual(vm.host_machine, self.host_asset)
    
    def test_create_vm_with_invalid_vm_ip(self):
        """Test VM creation with invalid VM IP format."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Prepare POST data with invalid IP
        data = {
            'vm_ip': '192.168.50',  # Invalid format
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'TestVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('vm_ip', response_data['field_errors'])
    
    def test_create_vm_with_nonexistent_base_machine(self):
        """Test VM creation with non-existent base machine IP."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Prepare POST data with non-existent base machine IP
        data = {
            'vm_ip': '192.168.50.20',
            'base_machine_ip': '192.168.50.99',  # Doesn't exist
            'vm_name': 'TestVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('base_machine_ip', response_data['field_errors'])
    
    def test_create_vm_with_already_assigned_ip(self):
        """Test VM creation with already assigned IP."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Mark VM IP as assigned
        self.vm_ip.is_assigned = True
        self.vm_ip.save()
        
        # Prepare POST data
        data = {
            'vm_ip': '192.168.50.20',
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'TestVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
    
    def test_create_vm_with_manual_ip(self):
        """Test VM creation with manual IP (not in IPAddress table)."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Prepare POST data with manual IP
        data = {
            'vm_ip': '10.0.0.100',  # Not in IPAddress table
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'ManualVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify VM was created with manual IP
        vm = HyperVVM.objects.get(name='ManualVM')
        self.assertEqual(vm.manual_ip, '10.0.0.100')
        self.assertIsNone(vm.ip_address)
    
    def test_create_vm_requires_authentication(self):
        """Test that VM creation requires authentication."""
        # Don't login
        
        # Prepare POST data
        data = {
            'vm_ip': '192.168.50.20',
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'TestVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check that user gets 403 Forbidden (AdminRequiredMixin behavior)
        self.assertEqual(response.status_code, 403)
    
    def test_ip_conflict_with_active_asset_manual_ip(self):
        """Test IP conflict detection when manual IP is used by active asset."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Create another asset with manual IP
        conflicting_asset = Asset.objects.create(
            asset_tag='BIDC002',
            system_type='Desktop',
            operating_system=self.os,
            manual_ip='10.0.0.50',
            team=self.team,
            status='active'
        )
        
        # Try to create VM with same manual IP
        data = {
            'vm_ip': '10.0.0.50',  # Same as conflicting_asset.manual_ip
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'ConflictVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        # Check field_errors for the actual error message
        self.assertIn('vm_ip', response_data['field_errors'])
        error_msg = str(response_data['field_errors']['vm_ip'])
        self.assertIn('IP conflict', error_msg)
        self.assertIn('active asset', error_msg)
    
    def test_ip_conflict_with_network_device(self):
        """Test IP conflict detection when IP is used by network device."""
        from assets.models import NetworkDevice
        
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Create IP for network device
        device_ip = IPAddress.objects.create(
            address='192.168.50.30',
            ip_range=self.ip_range,
            is_assigned=True
        )
        
        # Create network device
        network_device = NetworkDevice.objects.create(
            device_type='Camera',
            device_name='Security Camera 1',
            ip_address=device_ip
        )
        
        # Try to create VM with same IP
        data = {
            'vm_ip': '192.168.50.30',  # Same as network device IP
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'ConflictVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        # Check field_errors for the actual error message
        self.assertIn('vm_ip', response_data['field_errors'])
        error_msg = str(response_data['field_errors']['vm_ip'])
        self.assertIn('IP conflict', error_msg)
        self.assertIn('network device', error_msg)
    
    def test_ip_conflict_with_another_vm(self):
        """Test IP conflict detection when manual IP is used by another VM."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Create existing VM with manual IP
        existing_vm = HyperVVM.objects.create(
            name='ExistingVM',
            host_machine=self.host_asset,
            manual_ip='10.0.0.60',
            is_active=True
        )
        
        # Try to create another VM with same manual IP
        data = {
            'vm_ip': '10.0.0.60',  # Same as existing_vm.manual_ip
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'ConflictVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        # Check field_errors for the actual error message
        self.assertIn('vm_ip', response_data['field_errors'])
        error_msg = str(response_data['field_errors']['vm_ip'])
        self.assertIn('IP conflict', error_msg)
        self.assertIn('another VM', error_msg)
    
    def test_no_conflict_with_freed_asset(self):
        """Test that freed assets don't cause IP conflicts."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Create freed asset with manual IP
        freed_asset = Asset.objects.create(
            asset_tag='BIDC003',
            system_type='Desktop',
            operating_system=self.os,
            manual_ip='10.0.0.70',
            team=self.team,
            status='freed'  # Freed, not active
        )
        
        # Try to create VM with same IP - should succeed
        data = {
            'vm_ip': '10.0.0.70',  # Same as freed_asset.manual_ip
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'NoConflictVM'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response - should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify VM was created
        vm = HyperVVM.objects.get(name='NoConflictVM')
        self.assertEqual(vm.manual_ip, '10.0.0.70')
    
    def test_no_conflict_with_inactive_vm(self):
        """Test that inactive VMs don't cause IP conflicts."""
        # Login as admin
        self.client.login(username='admin', password='adminpass')
        
        # Create inactive VM with manual IP
        inactive_vm = HyperVVM.objects.create(
            name='InactiveVM',
            host_machine=self.host_asset,
            manual_ip='10.0.0.80',
            is_active=False  # Inactive
        )
        
        # Try to create VM with same IP - should succeed
        data = {
            'vm_ip': '10.0.0.80',  # Same as inactive_vm.manual_ip
            'base_machine_ip': '192.168.50.10',
            'vm_name': 'NoConflictVM2'
        }
        
        # Submit request
        response = self.client.post(
            reverse('quick_vm_create'),
            data=data
        )
        
        # Check response - should succeed
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify VM was created
        vm = HyperVVM.objects.get(name='NoConflictVM2')
        self.assertEqual(vm.manual_ip, '10.0.0.80')
