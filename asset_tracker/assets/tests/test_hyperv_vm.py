"""
Basic tests for Hyper-V VM functionality.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from assets.models import Asset, HyperVVM, IPAddress, IPRange, OperatingSystem, Team
from assets.services.hyperv_service import HyperVService
from assets.services.ip_management_service import IPManagementService


class HyperVVMModelTest(TestCase):
    """Test HyperVVM model basic functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create test OS
        self.os = OperatingSystem.objects.create(name='Windows 10')
        
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
        self.host_ip.assigned_to_asset = self.host_asset
        self.host_ip.save()
    
    def test_create_vm(self):
        """Test creating a VM."""
        vm_data = {
            'name': 'TestVM-01',
            'host_machine': self.host_asset,
            'ip_address': self.vm_ip,
            'notes': 'Test VM'
        }
        
        vm = HyperVService.create_vm(vm_data, self.user)
        
        self.assertEqual(vm.name, 'TestVM-01')
        self.assertEqual(vm.host_machine, self.host_asset)
        self.assertEqual(vm.ip_address, self.vm_ip)
        self.assertTrue(vm.is_active)
        
        # Check IP is marked as assigned
        self.vm_ip.refresh_from_db()
        self.assertTrue(self.vm_ip.is_assigned)
    
    def test_vm_without_ip(self):
        """Test creating a VM without IP address."""
        vm_data = {
            'name': 'TestVM-NoIP',
            'host_machine': self.host_asset,
            'notes': 'VM without IP'
        }
        
        vm = HyperVService.create_vm(vm_data, self.user)
        
        self.assertEqual(vm.name, 'TestVM-NoIP')
        self.assertIsNone(vm.ip_address)
        self.assertEqual(vm.get_display_ip(), 'No IP assigned')
    
    def test_vm_host_relationship(self):
        """Test bidirectional VM-host relationship."""
        vm_data = {
            'name': 'TestVM-Relationship',
            'host_machine': self.host_asset,
        }
        
        vm = HyperVService.create_vm(vm_data, self.user)
        
        # Test forward relationship (host -> VM)
        hosted_vms = self.host_asset.hosted_vms.all()
        self.assertIn(vm, hosted_vms)
        
        # Test backward relationship (VM -> host)
        self.assertEqual(vm.host_machine, self.host_asset)
    
    def test_delete_vm_releases_ip(self):
        """Test that deleting a VM releases its IP."""
        vm_data = {
            'name': 'TestVM-Delete',
            'host_machine': self.host_asset,
            'ip_address': self.vm_ip,
        }
        
        vm = HyperVService.create_vm(vm_data, self.user)
        
        # Verify IP is assigned
        self.vm_ip.refresh_from_db()
        self.assertTrue(self.vm_ip.is_assigned)
        
        # Delete VM
        HyperVService.delete_vm(vm, self.user)
        
        # Verify IP is released
        self.vm_ip.refresh_from_db()
        self.assertFalse(self.vm_ip.is_assigned)
    
    def test_ip_range_classification(self):
        """Test IP range classification for VM ranges."""
        # Test common VM range
        self.assertTrue(IPManagementService.is_common_vm_range('192.168.50.100'))
        self.assertFalse(IPManagementService.is_common_vm_range('192.168.10.100'))
        
        # Test rare VM ranges
        self.assertTrue(IPManagementService.is_rare_vm_range('192.168.10.50'))
        self.assertTrue(IPManagementService.is_rare_vm_range('192.168.11.50'))
        self.assertTrue(IPManagementService.is_rare_vm_range('192.168.70.50'))
        self.assertFalse(IPManagementService.is_rare_vm_range('192.168.50.50'))
    
    def test_get_vms_for_host(self):
        """Test getting all VMs for a host."""
        # Create multiple VMs
        vm1_data = {'name': 'VM1', 'host_machine': self.host_asset}
        vm2_data = {'name': 'VM2', 'host_machine': self.host_asset}
        
        vm1 = HyperVService.create_vm(vm1_data, self.user)
        vm2 = HyperVService.create_vm(vm2_data, self.user)
        
        # Get VMs for host
        vms = HyperVService.get_vms_for_host(self.host_asset)
        
        self.assertEqual(vms.count(), 2)
        self.assertIn(vm1, vms)
        self.assertIn(vm2, vms)
