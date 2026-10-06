"""
Hyper-V VM management service for handling VM CRUD operations.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from assets.models import HyperVVM
from assets.services.ip_management_service import IPManagementService


class HyperVService:
    """Business logic for Hyper-V VM management."""
    
    @staticmethod
    @transaction.atomic
    def create_vm(data, user):
        """
        Create a new Hyper-V VM.
        
        Args:
            data: Dictionary with VM data
            user: User creating the VM
        
        Returns:
            HyperVVM: Created VM instance
        
        Raises:
            ValidationError: If validation fails
        """
        vm = HyperVVM(
            name=data['name'],
            host_machine=data['host_machine'],
            notes=data.get('notes', '')
        )
        
        # Handle IP assignment
        if data.get('ip_address'):
            vm.ip_address = data['ip_address']
            IPManagementService.assign_ip(data['ip_address'], None)
        elif data.get('manual_ip'):
            vm.manual_ip = data['manual_ip']
        
        vm.full_clean()
        vm.save()
        
        return vm
    
    @staticmethod
    @transaction.atomic
    def update_vm(vm, data, user):
        """
        Update an existing Hyper-V VM.
        
        Args:
            vm: HyperVVM instance to update
            data: Dictionary with updated data
            user: User updating the VM
        
        Returns:
            HyperVVM: Updated VM instance
        """
        old_ip = vm.ip_address
        
        vm.name = data['name']
        vm.host_machine = data['host_machine']
        vm.notes = data.get('notes', '')
        
        # Handle IP changes
        new_ip = data.get('ip_address')
        if old_ip != new_ip:
            if old_ip:
                IPManagementService.release_ip(old_ip)
            if new_ip:
                IPManagementService.assign_ip(new_ip, None)
            vm.ip_address = new_ip
        
        vm.full_clean()
        vm.save()
        
        return vm
    
    @staticmethod
    @transaction.atomic
    def delete_vm(vm, user, soft_delete=False):
        """
        Delete a Hyper-V VM and release its IP.
        
        Args:
            vm: HyperVVM instance to delete
            user: User deleting the VM
            soft_delete: If True, mark as inactive instead of deleting
        """
        if vm.ip_address:
            IPManagementService.release_ip(vm.ip_address)
        
        if soft_delete:
            vm.is_active = False
            vm.ip_address = None
            vm.save()
        else:
            vm.delete()
    
    @staticmethod
    def get_vms_for_host(host_asset):
        """
        Get all VMs hosted on a specific asset.
        
        Args:
            host_asset: Asset instance
        
        Returns:
            QuerySet: VMs hosted on this asset
        """
        return HyperVVM.objects.filter(
            host_machine=host_asset,
            is_active=True
        ).select_related('ip_address')
    
    @staticmethod
    def get_host_for_vm_ip(vm_ip_address):
        """
        Get the host machine for a VM IP address.
        
        Args:
            vm_ip_address: IPAddress instance
        
        Returns:
            Asset or None: Host machine if VM exists
        """
        try:
            vm = HyperVVM.objects.select_related('host_machine').get(
                ip_address=vm_ip_address,
                is_active=True
            )
            return vm.host_machine
        except HyperVVM.DoesNotExist:
            return None
