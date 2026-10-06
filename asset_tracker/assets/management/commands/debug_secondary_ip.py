"""
Debug management command to check secondary IP field population when editing assets.

This command helps identify why secondary IP addresses aren't appearing when editing assets
by showing:
1. What get_primary_ip() returns
2. What get_secondary_ips() returns
3. Secondary IP details (managed vs manual)
4. What the form __init__ does for secondary IPs
5. What the queryset would be for secondary_ip_address field
6. What the initial value would be set to

Usage:
    python manage.py debug_secondary_ip [--create-test-asset]

Options:
    --create-test-asset    Create a test asset with managed primary and secondary IPs
"""
from django.core.management.base import BaseCommand
from django.db.models import Q
from assets.models import Asset, IPAddress, AssetIPAddress, Branch, OperatingSystem
from assets.forms.asset_forms import get_filtered_free_ips


class Command(BaseCommand):
    help = 'Debug secondary IP field population when editing assets'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--create-test-asset',
            action='store_true',
            help='Create a test asset with managed primary and secondary IPs',
        )

    def handle(self, *args, **options):
        """Execute the debug command."""
        # Handle --create-test-asset option
        if options['create_test_asset']:
            self.create_test_asset()
            return
        
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Secondary IP Debug Command'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        # Find an asset that has BOTH primary and secondary IPs (prefer managed secondary)
        asset_with_both_ips = None
        asset_with_manual_secondary = None
        
        self.stdout.write(self.style.WARNING('Searching for an asset with both primary and secondary IPs...'))
        self.stdout.write('')
        
        for asset in Asset.objects.all():
            primary = asset.get_primary_ip()
            secondary_ips = asset.get_secondary_ips()
            
            if primary and secondary_ips.exists():
                # Check if secondary is managed
                secondary = secondary_ips.first()
                if secondary.ip_address:
                    # Found one with managed secondary IP - prefer this
                    asset_with_both_ips = asset
                    break
                elif not asset_with_manual_secondary:
                    # Keep track of one with manual secondary as fallback
                    asset_with_manual_secondary = asset
        
        # If no asset with managed secondary found, use one with manual secondary
        if not asset_with_both_ips and asset_with_manual_secondary:
            asset_with_both_ips = asset_with_manual_secondary
            self.stdout.write(self.style.WARNING('Note: Using asset with MANUAL secondary IP (no managed secondary IPs found)'))
            self.stdout.write('')
        
        if not asset_with_both_ips:
            self.stdout.write(self.style.ERROR('No asset found with both primary and secondary IPs!'))
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('Creating a test scenario...'))
            
            # Find an asset with just a primary IP
            asset = Asset.objects.filter(
                asset_ip_addresses__is_primary=True
            ).first()
            
            if not asset:
                self.stdout.write(self.style.ERROR('No assets found with any IPs at all!'))
                return
            
            self.stdout.write(self.style.SUCCESS(f'Found asset: {asset.asset_tag}'))
            self.stdout.write(self.style.WARNING('This asset only has a primary IP. Consider adding a secondary IP to test.'))
            asset_with_both_ips = asset
        else:
            self.stdout.write(self.style.SUCCESS(f'Found asset: {asset_with_both_ips.asset_tag}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('1. Asset Information'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        asset = asset_with_both_ips
        self.stdout.write(f'Asset Tag: {asset.asset_tag}')
        self.stdout.write(f'System Type: {asset.system_type}')
        self.stdout.write(f'Branch: {asset.branch}')
        self.stdout.write('')
        
        # Show what get_primary_ip() returns
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('2. get_primary_ip() Result'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        primary_ip = asset.get_primary_ip()
        if primary_ip:
            self.stdout.write(f'Primary IP exists: YES')
            self.stdout.write(f'  - ID: {primary_ip.pk}')
            self.stdout.write(f'  - Is Primary: {primary_ip.is_primary}')
            self.stdout.write(f'  - Managed IP: {primary_ip.ip_address.address if primary_ip.ip_address else "None"}')
            self.stdout.write(f'  - Manual IP: {primary_ip.manual_ip if primary_ip.manual_ip else "None"}')
            self.stdout.write(f'  - Display: {primary_ip.get_ip_display()}')
        else:
            self.stdout.write(self.style.ERROR('No primary IP found!'))
        
        self.stdout.write('')
        
        # Show what get_secondary_ips() returns
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('3. get_secondary_ips() Result'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        secondary_ips = asset.get_secondary_ips()
        self.stdout.write(f'Number of secondary IPs: {secondary_ips.count()}')
        self.stdout.write('')
        
        if secondary_ips.exists():
            for idx, sec_ip in enumerate(secondary_ips, 1):
                self.stdout.write(f'Secondary IP #{idx}:')
                self.stdout.write(f'  - ID: {sec_ip.pk}')
                self.stdout.write(f'  - Is Primary: {sec_ip.is_primary}')
                self.stdout.write(f'  - Managed IP: {sec_ip.ip_address.address if sec_ip.ip_address else "None"}')
                self.stdout.write(f'  - Managed IP ID: {sec_ip.ip_address.pk if sec_ip.ip_address else "None"}')
                self.stdout.write(f'  - Manual IP: {sec_ip.manual_ip if sec_ip.manual_ip else "None"}')
                self.stdout.write(f'  - Display: {sec_ip.get_ip_display()}')
                self.stdout.write('')
        else:
            self.stdout.write(self.style.WARNING('No secondary IPs found!'))
        
        self.stdout.write('')
        
        # Simulate what the form __init__ does for secondary IPs
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('4. Form __init__ Logic Simulation'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        self.stdout.write('Simulating: secondary_ips = self.instance.asset_ip_addresses.filter(is_primary=False)')
        simulated_query = asset.asset_ip_addresses.filter(is_primary=False)
        self.stdout.write(f'  Query exists: {simulated_query.exists()}')
        self.stdout.write(f'  Query count: {simulated_query.count()}')
        self.stdout.write('')
        
        if simulated_query.exists():
            self.stdout.write('Simulating: secondary_ip = secondary_ips.first()')
            secondary_ip = simulated_query.first()
            self.stdout.write(f'  secondary_ip: {secondary_ip}')
            self.stdout.write(f'  secondary_ip.id: {secondary_ip.pk}')
            self.stdout.write(f'  secondary_ip.ip_address: {secondary_ip.ip_address}')
            self.stdout.write(f'  secondary_ip.manual_ip: {secondary_ip.manual_ip}')
            self.stdout.write('')
            
            if secondary_ip.ip_address:
                self.stdout.write(self.style.SUCCESS('  Type: MANAGED'))
                self.stdout.write(f'  secondary_ip_type initial would be: "managed"')
                self.stdout.write(f'  secondary_ip.ip_address.pk: {secondary_ip.ip_address.pk}')
            elif secondary_ip.manual_ip:
                self.stdout.write(self.style.SUCCESS('  Type: MANUAL'))
                self.stdout.write(f'  secondary_ip_type initial would be: "manual"')
                self.stdout.write(f'  secondary_manual_ip initial would be: {secondary_ip.manual_ip}')
        else:
            self.stdout.write(self.style.WARNING('  No secondary IP to process'))
        
        self.stdout.write('')
        
        # Show what get_filtered_free_ips returns
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('5. get_filtered_free_ips() Analysis'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        # Get current managed IP IDs
        current_managed_ip_id = None
        current_secondary_ip_id = None
        
        if primary_ip and primary_ip.ip_address:
            current_managed_ip_id = primary_ip.ip_address.pk
            self.stdout.write(f'Primary managed IP ID: {current_managed_ip_id}')
        
        if secondary_ips.exists():
            secondary_ip = secondary_ips.first()
            if secondary_ip.ip_address:
                current_secondary_ip_id = secondary_ip.ip_address.pk
                self.stdout.write(f'Secondary managed IP ID: {current_secondary_ip_id}')
        
        self.stdout.write('')
        
        # Test get_filtered_free_ips with secondary IP included
        if current_secondary_ip_id:
            self.stdout.write(f'Calling: get_filtered_free_ips(include_current_ip_id={current_secondary_ip_id})')
            available_secondary_ips = get_filtered_free_ips(include_current_ip_id=current_secondary_ip_id)
            self.stdout.write(f'  Number of IPs returned: {len(available_secondary_ips)}')
            
            # Check if current secondary IP is in the list
            secondary_ip_in_list = any(ip.pk == current_secondary_ip_id for ip in available_secondary_ips)
            self.stdout.write(f'  Current secondary IP in list: {secondary_ip_in_list}')
            
            if secondary_ip_in_list:
                self.stdout.write(self.style.SUCCESS('  ✓ Current secondary IP is included!'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ Current secondary IP is NOT included!'))
            
            self.stdout.write('')
            self.stdout.write('  First 5 IPs in list:')
            for ip in available_secondary_ips[:5]:
                marker = ' ← CURRENT SECONDARY' if ip.pk == current_secondary_ip_id else ''
                self.stdout.write(f'    - {ip.address} (ID: {ip.pk}){marker}')
        else:
            self.stdout.write(self.style.WARNING('No managed secondary IP to test with'))
            self.stdout.write('')
            self.stdout.write('Testing scenario: What if the code does NOT pass include_current_ip_id?')
            self.stdout.write('Calling: get_filtered_free_ips()')
            available_secondary_ips_no_include = get_filtered_free_ips()
            self.stdout.write(f'  Number of free IPs: {len(available_secondary_ips_no_include)}')
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('If a managed secondary IP were assigned to this asset,'))
            self.stdout.write(self.style.WARNING('it would NOT appear in the queryset unless include_current_ip_id'))
            self.stdout.write(self.style.WARNING('is passed to get_filtered_free_ips()!'))
        
        self.stdout.write('')
        
        # Show queryset for secondary_ip_address field
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('6. secondary_ip_address Field Queryset'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        # Simulate form logic
        exclude_ip_ids = []
        if current_managed_ip_id:
            exclude_ip_ids.append(current_managed_ip_id)
            self.stdout.write(f'Excluding primary IP: {current_managed_ip_id}')
        
        if current_secondary_ip_id:
            available_secondary_ips = get_filtered_free_ips(include_current_ip_id=current_secondary_ip_id)
        else:
            available_secondary_ips = get_filtered_free_ips()
        
        self.stdout.write(f'Available secondary IPs before filtering: {len(available_secondary_ips)}')
        
        # Filter out the primary IP from secondary options
        available_secondary_ips = [ip for ip in available_secondary_ips if ip.pk not in exclude_ip_ids]
        
        self.stdout.write(f'Available secondary IPs after filtering: {len(available_secondary_ips)}')
        self.stdout.write('')
        
        # Set the queryset for secondary IP address field
        secondary_queryset = IPAddress.objects.filter(
            pk__in=[ip.pk for ip in available_secondary_ips]
        ).order_by('address')
        
        self.stdout.write(f'Final queryset count: {secondary_queryset.count()}')
        
        if current_secondary_ip_id:
            queryset_contains_current = secondary_queryset.filter(pk=current_secondary_ip_id).exists()
            self.stdout.write(f'Queryset contains current secondary IP: {queryset_contains_current}')
            
            if queryset_contains_current:
                self.stdout.write(self.style.SUCCESS('  ✓ Current secondary IP is in queryset!'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ Current secondary IP is NOT in queryset!'))
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('  This is the problem! The current secondary IP is being filtered out.'))
        
        self.stdout.write('')
        
        # Show what initial value would be set
        self.stdout.write(self.style.SUCCESS('-' * 80))
        self.stdout.write(self.style.SUCCESS('7. Initial Value for secondary_ip_address Field'))
        self.stdout.write(self.style.SUCCESS('-' * 80))
        
        if current_secondary_ip_id:
            self.stdout.write(f'secondary_ip_address.initial would be set to: {current_secondary_ip_id}')
            
            # Check if this ID exists in the queryset
            if secondary_queryset.filter(pk=current_secondary_ip_id).exists():
                self.stdout.write(self.style.SUCCESS('  ✓ Initial value exists in queryset - field will display correctly'))
            else:
                self.stdout.write(self.style.ERROR('  ✗ Initial value does NOT exist in queryset - field will be empty!'))
                self.stdout.write('')
                self.stdout.write(self.style.ERROR('  ROOT CAUSE: The initial value is set but the IP is not in the queryset'))
                self.stdout.write(self.style.ERROR('  because it was filtered out (likely due to being assigned).'))
        else:
            self.stdout.write(self.style.WARNING('No secondary IP, so initial value would not be set'))
        
        self.stdout.write('')
        
        # Summary and recommendations
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('8. Summary and Recommendations'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        
        if current_secondary_ip_id:
            secondary_ip_obj = IPAddress.objects.get(pk=current_secondary_ip_id)
            self.stdout.write(f'Current Secondary IP: {secondary_ip_obj.address} (ID: {current_secondary_ip_id})')
            self.stdout.write(f'  is_assigned: {secondary_ip_obj.is_assigned}')
            self.stdout.write(f'  assigned_to_asset: {secondary_ip_obj.assigned_to_asset}')
            self.stdout.write('')
            
            if secondary_ip_obj.is_assigned:
                self.stdout.write(self.style.WARNING('The secondary IP is marked as assigned.'))
                self.stdout.write(self.style.WARNING('get_filtered_free_ips() only returns free IPs (is_assigned=False)'))
                self.stdout.write(self.style.WARNING('unless include_current_ip_id is specified.'))
                self.stdout.write('')
                self.stdout.write(self.style.SUCCESS('RECOMMENDATION:'))
                self.stdout.write(self.style.SUCCESS('The form logic should pass include_current_ip_id for the secondary IP'))
                self.stdout.write(self.style.SUCCESS('just like it does for the primary IP.'))
        else:
            self.stdout.write(self.style.WARNING('No secondary IP to analyze'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Debug Complete'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
    
    def create_test_asset(self):
        """Create a test asset with managed primary and secondary IPs."""
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('Creating Test Asset'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        # Get first available branch
        branch = Branch.objects.filter(is_active=True).first()
        if not branch:
            self.stdout.write(self.style.ERROR('No active branch found!'))
            return
        
        self.stdout.write(f'Using branch: {branch.name}')
        
        # Get first OS
        os = OperatingSystem.objects.first()
        if not os:
            self.stdout.write(self.style.ERROR('No operating system found!'))
            return
        
        self.stdout.write(f'Using OS: {os.name}')
        
        # Get two free IPs from filtered ranges
        free_ips = get_filtered_free_ips()
        if len(free_ips) < 2:
            self.stdout.write(self.style.ERROR('Need at least 2 free IPs in filtered ranges!'))
            return
        
        primary_ip = free_ips[0]
        secondary_ip = free_ips[1]
        
        self.stdout.write(f'Using primary IP: {primary_ip.address} (ID: {primary_ip.pk})')
        self.stdout.write(f'Using secondary IP: {secondary_ip.address} (ID: {secondary_ip.pk})')
        self.stdout.write('')
        
        # Create asset
        import random
        asset_tag = f'DEBUG-TEST-{random.randint(1000, 9999)}'
        
        asset = Asset.objects.create(
            asset_tag=asset_tag,
            system_type='Desktop',
            operating_system=os,
            branch=branch
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created asset: {asset_tag}'))
        
        # Create primary IP association
        AssetIPAddress.objects.create(
            asset=asset,
            ip_address=primary_ip,
            is_primary=True
        )
        
        primary_ip.is_assigned = True
        primary_ip.assigned_to_asset = asset
        primary_ip.save()
        
        self.stdout.write(self.style.SUCCESS(f'Assigned primary IP: {primary_ip.address}'))
        
        # Create secondary IP association
        AssetIPAddress.objects.create(
            asset=asset,
            ip_address=secondary_ip,
            is_primary=False
        )
        
        secondary_ip.is_assigned = True
        secondary_ip.assigned_to_asset = asset
        secondary_ip.save()
        
        self.stdout.write(self.style.SUCCESS(f'Assigned secondary IP: {secondary_ip.address}'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS(f'Test asset created: {asset_tag}'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        self.stdout.write(f'Now run: python manage.py debug_secondary_ip')
        self.stdout.write('to see the debug information for this asset.')
        self.stdout.write('')
