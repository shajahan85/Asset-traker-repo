"""
IP management service for handling IP address assignments.
"""
from django.db import transaction
from assets.models import IPAddress, Asset


class IPManagementService:
    """Service class for IP address management."""
    
    @staticmethod
    def assign_ip(ip_address, asset):
        """
        Mark IP as assigned and link to asset.
        
        Args:
            ip_address: IPAddress instance to assign
            asset: Asset instance to assign the IP to
        """
        with transaction.atomic():
            ip_address.is_assigned = True
            ip_address.assigned_to_asset = asset
            ip_address.save()
    
    @staticmethod
    def release_ip(ip_address):
        """
        Mark IP as free and clear asset link.
        
        Args:
            ip_address: IPAddress instance to release
        """
        from django.utils import timezone
        
        with transaction.atomic():
            ip_address.is_assigned = False
            ip_address.assigned_to_asset = None
            ip_address.freed_date = timezone.now()
            ip_address.save()
    
    @staticmethod
    def change_asset_ip(asset, new_ip):
        """
        Release old IP and assign new IP to asset.
        
        Args:
            asset: Asset instance to change IP for
            new_ip: IPAddress instance to assign to the asset
        """
        with transaction.atomic():
            # Release old IP if exists
            if asset.ip_address:
                IPManagementService.release_ip(asset.ip_address)
            
            # Assign new IP
            IPManagementService.assign_ip(new_ip, asset)
            
            # Update asset's IP reference
            asset.ip_address = new_ip
            asset.save()
    
    @staticmethod
    def get_free_ips_by_range():
        """
        Return dict of ranges to free IPs, sorted numerically.
        
        Returns:
            dict: Dictionary mapping IP range patterns to lists of free IP addresses
        """
        free_ips = IPAddress.objects.filter(is_assigned=False).select_related('ip_range')
        
        result = {}
        for ip in free_ips:
            range_pattern = ip.ip_range.range_pattern
            if range_pattern not in result:
                result[range_pattern] = []
            result[range_pattern].append(ip)
        
        # Sort IPs numerically within each range
        for range_pattern in result:
            result[range_pattern] = sorted(
                result[range_pattern],
                key=lambda ip: tuple(map(int, ip.address.split('.')))
            )
        
        return result
    
    @staticmethod
    def get_all_ips_by_range():
        """
        Return dict of ranges to all IPs (both free and occupied), sorted numerically.
        Includes assigned user information for occupied IPs.
        Also checks for manual IP assignments to prevent IP conflicts.
        
        Returns:
            dict: Dictionary mapping IP range patterns to lists of all IP addresses
        """
        all_ips = IPAddress.objects.all().select_related('ip_range', 'assigned_to_asset')
        
        result = {}
        for ip in all_ips:
            range_pattern = ip.ip_range.range_pattern
            if range_pattern not in result:
                result[range_pattern] = []
            
            # Check if this IP is used as a manual IP by any active asset
            manual_asset = Asset.objects.filter(
                manual_ip=ip.address,
                status='active'
            ).first()
            
            # If IP is used manually but not marked as assigned, mark it
            if manual_asset and not ip.is_assigned:
                ip.manual_assignment = True
                ip.manual_assigned_asset = manual_asset
            else:
                ip.manual_assignment = False
                ip.manual_assigned_asset = None
            
            result[range_pattern].append(ip)
        
        # Sort IPs numerically within each range
        for range_pattern in result:
            result[range_pattern] = sorted(
                result[range_pattern],
                key=lambda ip: tuple(map(int, ip.address.split('.')))
            )
        
        return result
    
    @staticmethod
    def get_available_ips():
        """
        Return queryset of unassigned IPs.
        
        Returns:
            QuerySet: QuerySet of unassigned IPAddress instances
        """
        return IPAddress.objects.filter(is_assigned=False).select_related('ip_range')
    
    @staticmethod
    def assign_ip_to_network_device(ip_address, network_device):
        """
        Assign IP address to network device.
        
        Args:
            ip_address: IPAddress instance
            network_device: NetworkDevice instance
        """
        with transaction.atomic():
            ip_address.is_assigned = True
            ip_address.assigned_to_asset = None  # Network devices don't use this field
            ip_address.save()
    
    @staticmethod
    def get_ip_occupant_info(ip_address):
        """
        Get information about what occupies an IP address.
        Checks managed assignments, network devices, VMs, and manual IP assignments.
        
        Args:
            ip_address: IPAddress instance
        
        Returns:
            dict: {'type': 'asset'|'network_device'|'vm'|'free', 'name': str, 'object': Asset|NetworkDevice|HyperVVM|None}
        """
        # Check for VM first (reverse ForeignKey relationship - returns queryset)
        try:
            vm_queryset = ip_address.vm.all()
            if vm_queryset.exists():
                vm = vm_queryset.first()
                return {
                    'type': 'vm',
                    'name': vm.name,
                    'object': vm
                }
        except Exception:
            pass
        
        # Check for network device (OneToOne reverse relationship)
        try:
            if hasattr(ip_address, 'network_device') and ip_address.network_device is not None:
                return {
                    'type': 'network_device',
                    'name': ip_address.network_device.device_name,
                    'object': ip_address.network_device
                }
        except Exception:
            pass
        
        # Check for asset assignment (managed IP)
        if ip_address.assigned_to_asset:
            return {
                'type': 'asset',
                'name': ip_address.assigned_to_asset.assigned_to or 'Unassigned',
                'object': ip_address.assigned_to_asset
            }
        
        # Check for manual IP assignment (active assets using this IP as manual_ip)
        manual_asset = Asset.objects.filter(
            manual_ip=ip_address.address,
            status='active'
        ).first()
        
        if manual_asset:
            return {
                'type': 'asset',
                'name': manual_asset.assigned_to or 'Unassigned',
                'object': manual_asset
            }
        
        # Check for manual IP assignment (network devices using this IP as manual_ip)
        from assets.models import NetworkDevice
        manual_network_device = NetworkDevice.objects.filter(
            manual_ip=ip_address.address
        ).first()
        
        if manual_network_device:
            return {
                'type': 'network_device',
                'name': manual_network_device.device_name,
                'object': manual_network_device
            }
        
        # Check for manual IP assignment (VMs using this IP as manual_ip)
        from assets.models import HyperVVM
        manual_vm = HyperVVM.objects.filter(
            manual_ip=ip_address.address,
            is_active=True
        ).first()
        
        if manual_vm:
            return {
                'type': 'vm',
                'name': manual_vm.name,
                'object': manual_vm
            }
        
        # Free IP
        return {
            'type': 'free',
            'name': None,
            'object': None
        }
    
    @staticmethod
    def get_all_ips_by_range_with_vms():
        """
        Return dict of ranges to all IPs with VM relationship data.
        Also checks for manual IP assignments to prevent showing occupied IPs as free.
        
        Returns:
            dict: IP ranges with IPs including VM relationships
        """
        from assets.models import NetworkDevice, HyperVVM
        
        # Fetch all IPs with related data in one query
        all_ips = IPAddress.objects.all().select_related(
            'ip_range',
            'assigned_to_asset',
            'network_device',
            'testing_device'
        ).prefetch_related(
            'vm',
            'assigned_to_asset__hosted_vms',
            'assigned_to_asset__hosted_vms__ip_address'
        )
        
        # Pre-fetch all manual IP assignments in bulk (3 queries instead of N queries)
        manual_assets_dict = {}
        for asset in Asset.objects.filter(status='active', manual_ip__isnull=False).only('manual_ip', 'serial_number', 'assigned_to'):
            manual_assets_dict[asset.manual_ip] = asset
        
        manual_network_devices_dict = {}
        for device in NetworkDevice.objects.filter(manual_ip__isnull=False).only('manual_ip', 'id', 'device_name'):
            manual_network_devices_dict[device.manual_ip] = device
        
        manual_testing_devices_dict = {}
        from assets.models import TestingDevice
        for device in TestingDevice.objects.filter(manual_ip__isnull=False).only('manual_ip', 'id', 'device_name', 'assigned_user'):
            manual_testing_devices_dict[device.manual_ip] = device
        
        manual_vms_dict = {}
        for vm in HyperVVM.objects.filter(is_active=True, manual_ip__isnull=False).only('manual_ip', 'id', 'name'):
            manual_vms_dict[vm.manual_ip] = vm
        
        # Pre-fetch AssetIPAddress associations for managed IPs (to catch additional IPs)
        from assets.models import AssetIPAddress
        asset_ip_associations_dict = {}
        for assoc in AssetIPAddress.objects.filter(
            ip_address__isnull=False,
            asset__status='active'
        ).select_related('asset', 'ip_address'):
            asset_ip_associations_dict[assoc.ip_address_id] = assoc
        
        # Also pre-fetch AssetIPAddress records with manual_ip that match pool IPs
        # (users can type a pool IP manually instead of selecting from dropdown)
        manual_ip_associations_dict = {}
        for assoc in AssetIPAddress.objects.filter(
            manual_ip__isnull=False,
            asset__status='active'
        ).select_related('asset'):
            manual_ip_associations_dict[assoc.manual_ip] = assoc
        
        result = {}
        for ip in all_ips:
            range_pattern = ip.ip_range.range_pattern
            if range_pattern not in result:
                result[range_pattern] = []
            
            # Check if this IP is used as a manual IP (using pre-fetched dicts)
            manual_asset = manual_assets_dict.get(ip.address)
            manual_network_device = manual_network_devices_dict.get(ip.address)
            manual_vm = manual_vms_dict.get(ip.address)
            
            # If IP is used manually but not marked as assigned, mark it temporarily
            manual_testing_device = manual_testing_devices_dict.get(ip.address)
            if (manual_asset or manual_network_device or manual_vm or manual_testing_device) and not ip.is_assigned:
                ip.manual_assignment = True
                ip.manual_assigned_asset = manual_asset
                ip.manual_assigned_network_device = manual_network_device
                ip.manual_assigned_vm = manual_vm
                ip.manual_assigned_testing_device = manual_testing_device
            else:
                ip.manual_assignment = False
                ip.manual_assigned_asset = None
                ip.manual_assigned_network_device = None
                ip.manual_assigned_vm = None
                ip.manual_assigned_testing_device = None
            
            # Also check AssetIPAddress junction table for additional IPs not reflected in is_assigned
            if not ip.is_assigned and not ip.manual_assignment:
                # Check managed IP associations (FK link)
                assoc = asset_ip_associations_dict.get(ip.pk)
                if not assoc:
                    # Check manual IP associations (manual_ip text match)
                    assoc = manual_ip_associations_dict.get(ip.address)
                
                if assoc:
                    # This IP is assigned via the junction table but IPAddress.is_assigned wasn't set
                    # Fix it in-memory for display and also fix in DB
                    ip.is_assigned = True
                    ip.assigned_to_asset = assoc.asset
                    ip.ip_label_from_junction = assoc.ip_label
                    # Also fix the DB record so this self-heals
                    IPAddress.objects.filter(pk=ip.pk).update(
                        is_assigned=True,
                        assigned_to_asset=assoc.asset
                    )
            
            # Attach IP label from AssetIPAddress junction (for already-assigned IPs)
            if not hasattr(ip, 'ip_label_from_junction'):
                # Check if this IP has a label in the junction table
                assoc = asset_ip_associations_dict.get(ip.pk)
                if not assoc:
                    assoc = manual_ip_associations_dict.get(ip.address)
                ip.ip_label_from_junction = assoc.ip_label if assoc else None
            
            # Add VM relationship data
            # Check if this IP is assigned to a VM (reverse ForeignKey returns queryset)
            vm_queryset = ip.vm.all()
            is_vm = vm_queryset.exists()
            vm_obj = vm_queryset.first() if is_vm else None
            
            # Also check if a VM uses this IP as manual_ip (not linked via FK)
            if not is_vm and hasattr(ip, 'manual_assigned_vm') and ip.manual_assigned_vm:
                is_vm = True
                vm_obj = ip.manual_assigned_vm
            
            ip_data = {
                'ip': ip,
                'is_vm': is_vm,
                'vm': vm_obj,
                'hosted_vms': []
            }
            
            # If this IP belongs to a host machine, get its VMs
            if ip.assigned_to_asset:
                ip_data['hosted_vms'] = list(
                    ip.assigned_to_asset.hosted_vms.filter(is_active=True)
                )
            elif hasattr(ip, 'manual_assigned_asset') and ip.manual_assigned_asset:
                # Host machine found via manual_ip match - also get its VMs
                ip_data['hosted_vms'] = list(
                    ip.manual_assigned_asset.hosted_vms.filter(is_active=True)
                )
            
            result[range_pattern].append(ip_data)
        
        # Sort IPs numerically within each range
        for range_pattern in result:
            result[range_pattern] = sorted(
                result[range_pattern],
                key=lambda item: tuple(map(int, item['ip'].address.split('.')))
            )
        
        return result
    
    @staticmethod
    def is_common_vm_range(ip_address):
        """
        Check if IP belongs to a common VM range.
        
        Args:
            ip_address: IP address string or IPAddress instance
        
        Returns:
            bool: True if in common VM range (192.168.50.x)
        """
        if isinstance(ip_address, IPAddress):
            address = ip_address.address
        else:
            address = str(ip_address)
        
        return address.startswith('192.168.50.')
    
    @staticmethod
    def is_rare_vm_range(ip_address):
        """
        Check if IP belongs to a rare VM range.
        
        Args:
            ip_address: IP address string or IPAddress instance
        
        Returns:
            bool: True if in rare VM range
        """
        if isinstance(ip_address, IPAddress):
            address = ip_address.address
        else:
            address = str(ip_address)
        
        rare_prefixes = ['192.168.10.', '192.168.11.', '192.168.70.']
        return any(address.startswith(prefix) for prefix in rare_prefixes)
    
    @staticmethod
    def assign_ip_to_guest(ip_address, guest_name, admin_user):
        """
        Assign IP address to a guest temporarily.
        
        Args:
            ip_address: IPAddress instance to assign
            guest_name: str, name of the guest
            admin_user: User instance of admin making assignment
            
        Raises:
            ValidationError: If IP is already assigned
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        with transaction.atomic():
            # Refresh from DB to ensure latest state
            ip_address.refresh_from_db()
            
            # Validate IP is actually free
            if ip_address.is_assigned or ip_address.guest_name:
                raise ValidationError("This IP address is already assigned.")
            
            # Check for manual IP conflicts
            if IPManagementService._is_ip_manually_used(ip_address.address):
                raise ValidationError("This IP address is in use as a manual IP.")
            
            # Assign to guest
            ip_address.is_assigned = True
            ip_address.guest_name = guest_name.strip()
            ip_address.guest_assigned_date = timezone.now()
            ip_address.guest_assigned_by = admin_user.username
            ip_address.save()
    
    @staticmethod
    def release_guest_ip(ip_address, admin_user):
        """
        Release IP address from guest assignment.
        
        Args:
            ip_address: IPAddress instance to release
            admin_user: User instance of admin releasing IP
            
        Raises:
            ValidationError: If IP is not guest-assigned
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        with transaction.atomic():
            # Refresh from DB to ensure latest state
            ip_address.refresh_from_db()
            
            # Validate this is a guest assignment
            if not ip_address.guest_name:
                raise ValidationError("This IP is not assigned to a guest.")
            
            # Release the IP
            ip_address.is_assigned = False
            ip_address.guest_name = None
            ip_address.guest_assigned_date = None
            ip_address.guest_assigned_by = None
            ip_address.freed_date = timezone.now()
            ip_address.save()
    
    @staticmethod
    def mark_ip_occupied(ip_address, admin_user, particulars=None):
        """
        Mark a free IP address as manually occupied.
        
        Args:
            ip_address: IPAddress instance to mark
            admin_user: User instance of admin performing the action
            
        Raises:
            ValidationError: If IP is already assigned
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        with transaction.atomic():
            # Refresh from DB to ensure latest state
            ip_address.refresh_from_db()
            
            # Validate IP is actually free
            if ip_address.is_assigned or ip_address.guest_name or ip_address.manually_occupied:
                raise ValidationError("This IP address is already assigned.")
            
            # Check for manual IP conflicts
            if IPManagementService._is_ip_manually_used(ip_address.address):
                raise ValidationError("This IP address is in use as a manual IP.")
            
            # Mark as occupied
            ip_address.is_assigned = True
            ip_address.manually_occupied = True
            ip_address.occupied_by = admin_user.username
            ip_address.occupied_date = timezone.now()
            ip_address.occupied_particulars = particulars or ''
            ip_address.save()
    
    @staticmethod
    def release_occupied_ip(ip_address, admin_user):
        """
        Release a manually-occupied IP address back to free status.
        
        Args:
            ip_address: IPAddress instance to release
            admin_user: User instance of admin performing the action
            
        Raises:
            ValidationError: If IP is not manually occupied
        """
        from django.utils import timezone
        from django.core.exceptions import ValidationError
        
        with transaction.atomic():
            # Refresh from DB to ensure latest state
            ip_address.refresh_from_db()
            
            # Validate this is a manually occupied IP
            if not ip_address.manually_occupied:
                raise ValidationError("This IP is not manually occupied.")
            
            # Release the IP
            ip_address.is_assigned = False
            ip_address.manually_occupied = False
            ip_address.occupied_by = None
            ip_address.occupied_date = None
            ip_address.occupied_particulars = None
            ip_address.freed_date = timezone.now()
            ip_address.save()
    
    @staticmethod
    def _is_ip_manually_used(ip_address_str):
        """Check if an IP is used as manual IP by any entity."""
        from assets.models import NetworkDevice, HyperVVM
        
        # Check assets
        if Asset.objects.filter(manual_ip=ip_address_str, status='active').exists():
            return True
        
        # Check network devices
        if NetworkDevice.objects.filter(manual_ip=ip_address_str).exists():
            return True
        
        # Check VMs
        if HyperVVM.objects.filter(manual_ip=ip_address_str, is_active=True).exists():
            return True
        
        return False
