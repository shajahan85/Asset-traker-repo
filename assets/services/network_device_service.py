"""
Network device service for managing non-system network devices.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from assets.models import NetworkDevice, IPAddress
from assets.services.ip_management_service import IPManagementService


class NetworkDeviceService:
    """Service class for network device management."""
    
    @staticmethod
    def create_network_device(data, user):
        """
        Create network device with IP assignment.
        
        Args:
            data: Dictionary with device_type, device_name, ip_address_id (optional), manual_ip (optional)
            user: User creating the device
        
        Returns:
            NetworkDevice: Created device instance
        
        Raises:
            ValidationError: If IP is already assigned or if neither IP is provided
        """
        with transaction.atomic():
            ip_address_id = data.get('ip_address_id')
            manual_ip = data.get('manual_ip')
            
            # Validate that at least one IP is provided
            if not ip_address_id and not manual_ip:
                raise ValidationError('Either IP Address or Manual IP must be provided.')
            
            # Validate that both IPs are not provided
            if ip_address_id and manual_ip:
                raise ValidationError('Please provide either IP Address or Manual IP, not both.')
            
            # Handle managed IP
            if ip_address_id:
                ip_address = IPAddress.objects.get(id=ip_address_id)
                
                if ip_address.is_assigned:
                    raise ValidationError({'ip_address': 'IP address already in use'})
                
                device = NetworkDevice.objects.create(
                    device_type=data['device_type'],
                    device_name=data['device_name'],
                    ip_address=ip_address
                )
                
                # Mark IP as assigned using existing service
                IPManagementService.assign_ip_to_network_device(ip_address, device)
            else:
                # Handle manual IP
                device = NetworkDevice.objects.create(
                    device_type=data['device_type'],
                    device_name=data['device_name'],
                    manual_ip=manual_ip
                )
            
            return device
    
    @staticmethod
    def update_network_device(device, data, user):
        """
        Update network device with IP change handling.
        
        Args:
            device: NetworkDevice instance to update
            data: Dictionary with updated fields (device_type, device_name, ip_address_id, manual_ip)
            user: User updating the device
        
        Returns:
            NetworkDevice: Updated device instance
        
        Raises:
            ValidationError: If new IP is already assigned
        """
        with transaction.atomic():
            old_ip = device.ip_address
            old_manual_ip = device.manual_ip
            new_ip_id = data.get('ip_address_id')
            new_manual_ip = data.get('manual_ip')
            
            # Validate that at least one IP is provided
            if not new_ip_id and not new_manual_ip:
                raise ValidationError('Either IP Address or Manual IP must be provided.')
            
            # Validate that both IPs are not provided
            if new_ip_id and new_manual_ip:
                raise ValidationError('Please provide either IP Address or Manual IP, not both.')
            
            # Handle IP changes
            if new_ip_id:
                # Switching to or updating managed IP
                new_ip = IPAddress.objects.get(id=new_ip_id)
                
                # Check if IP changed
                if not old_ip or old_ip.id != new_ip.id:
                    if new_ip.is_assigned:
                        raise ValidationError({'ip_address': 'IP address already in use'})
                    
                    # Release old managed IP if exists
                    if old_ip:
                        IPManagementService.release_ip(old_ip)
                    
                    # Assign new IP
                    device.ip_address = new_ip
                    device.manual_ip = None
                    IPManagementService.assign_ip_to_network_device(new_ip, device)
            else:
                # Switching to or updating manual IP
                # Release old managed IP if exists
                if old_ip:
                    IPManagementService.release_ip(old_ip)
                
                device.ip_address = None
                device.manual_ip = new_manual_ip
            
            # Update other fields
            device.device_type = data.get('device_type', device.device_type)
            device.device_name = data.get('device_name', device.device_name)
            device.save()
            
            return device
    
    @staticmethod
    def delete_network_device(device, user):
        """
        Delete network device and release IP.
        
        Args:
            device: NetworkDevice instance to delete
            user: User deleting the device
        """
        with transaction.atomic():
            ip_address = device.ip_address
            device.delete()
            # Only release IP if it was a managed IP address
            if ip_address:
                IPManagementService.release_ip(ip_address)
