"""
Management command to debug IP field issues when editing assets.

This command helps diagnose why the IP field might not be pre-populating
correctly in the asset edit form.

Usage:
    python manage.py debug_ip_field
"""

from django.core.management.base import BaseCommand
from assets.models import Asset, IPAddress, AssetIPAddress
from assets.forms.asset_forms import get_filtered_free_ips


class Command(BaseCommand):
    """Debug IP field initialization in asset edit forms."""
    
    help = 'Debug IP field issues by showing how get_primary_ip() and form initialization works'
    
    def handle(self, *args, **options):
        """Execute the debug analysis."""
        self.stdout.write(self.style.SUCCESS('=== IP Field Debugging Tool ==='))
        self.stdout.write('')
        
        # Find the first asset that has a primary IP
        asset_with_ip = None
        for asset in Asset.objects.all().order_by('serial_number'):
            primary_ip = asset.get_primary_ip()
            if primary_ip and primary_ip.ip_address:
                asset_with_ip = asset
                break
        
        if not asset_with_ip:
            self.stdout.write(self.style.ERROR('No assets found with a managed IP address.'))
            self.stdout.write('')
            
            # Show some statistics
            total_assets = Asset.objects.count()
            assets_with_manual_ip = Asset.objects.filter(
                asset_ip_addresses__manual_ip__isnull=False
            ).distinct().count()
            
            self.stdout.write(f'Total assets: {total_assets}')
            self.stdout.write(f'Assets with manual IP: {assets_with_manual_ip}')
            return
        
        # Display asset information
        self.stdout.write(self.style.WARNING(f'Testing with Asset: {asset_with_ip.asset_tag}'))
        self.stdout.write(f'Serial Number: {asset_with_ip.serial_number}')
        self.stdout.write(f'System Type: {asset_with_ip.system_type}')
        self.stdout.write('')
        
        # Step 1: Show what get_primary_ip() returns
        self.stdout.write(self.style.SUCCESS('Step 1: Checking asset.get_primary_ip()'))
        primary_ip = asset_with_ip.get_primary_ip()
        
        if primary_ip:
            self.stdout.write(f'  ✓ Found primary IP association: {primary_ip}')
            self.stdout.write(f'    Type: {type(primary_ip).__name__}')
            self.stdout.write(f'    ID: {primary_ip.pk}')
            self.stdout.write(f'    is_primary: {primary_ip.is_primary}')
        else:
            self.stdout.write(self.style.ERROR('  ✗ No primary IP association found'))
            return
        
        self.stdout.write('')
        
        # Step 2: Show what primary_ip.ip_address is
        self.stdout.write(self.style.SUCCESS('Step 2: Checking primary_ip.ip_address'))
        
        if primary_ip.ip_address:
            self.stdout.write(f'  ✓ IP Address object exists: {primary_ip.ip_address}')
            self.stdout.write(f'    Type: {type(primary_ip.ip_address).__name__}')
            self.stdout.write(f'    Address: {primary_ip.ip_address.address}')
            self.stdout.write(f'    Is Assigned: {primary_ip.ip_address.is_assigned}')
        else:
            self.stdout.write(self.style.ERROR('  ✗ No ip_address (might be manual IP)'))
            if primary_ip.manual_ip:
                self.stdout.write(f'    Manual IP: {primary_ip.manual_ip}')
            return
        
        self.stdout.write('')
        
        # Step 3: Show what primary_ip.ip_address.pk is
        self.stdout.write(self.style.SUCCESS('Step 3: Checking primary_ip.ip_address.pk'))
        ip_pk = primary_ip.ip_address.pk
        self.stdout.write(f'  ✓ IP Address PK: {ip_pk}')
        self.stdout.write(f'    Type: {type(ip_pk).__name__}')
        self.stdout.write('')
        
        # Step 4: Simulate what the form does
        self.stdout.write(self.style.SUCCESS('Step 4: Simulating form initialization'))
        self.stdout.write('')
        
        # This is what the form does in __init__
        current_managed_ip_id = None
        if asset_with_ip and asset_with_ip.pk:
            primary_ip_check = asset_with_ip.get_primary_ip()
            if primary_ip_check and primary_ip_check.ip_address:
                current_managed_ip_id = primary_ip_check.ip_address.pk
                self.stdout.write(f'  current_managed_ip_id = {current_managed_ip_id}')
        
        # Get available IPs (what form does)
        if current_managed_ip_id:
            self.stdout.write(f'  Calling get_filtered_free_ips(include_current_ip_id={current_managed_ip_id})')
            available_ips = get_filtered_free_ips(include_current_ip_id=current_managed_ip_id)
        else:
            self.stdout.write('  Calling get_filtered_free_ips() without current IP')
            available_ips = get_filtered_free_ips()
        
        self.stdout.write(f'  Available IPs returned: {len(available_ips)}')
        self.stdout.write('')
        
        # Check if current IP is in the available list
        current_ip_in_list = any(ip.pk == current_managed_ip_id for ip in available_ips)
        if current_ip_in_list:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Current IP (pk={current_managed_ip_id}) IS in available IPs list'))
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ Current IP (pk={current_managed_ip_id}) NOT in available IPs list'))
        
        self.stdout.write('')
        
        # Show what the form choices would look like
        self.stdout.write(self.style.SUCCESS('Step 5: Form field initialization'))
        form_choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [
            (ip.pk, str(ip.address)) for ip in available_ips
        ]
        
        self.stdout.write(f'  Total choices (including empty): {len(form_choices)}')
        self.stdout.write('')
        
        # Show first 5 choices
        self.stdout.write('  Sample choices (first 5):')
        for value, label in form_choices[:5]:
            marker = ' <-- CURRENT' if value == current_managed_ip_id else ''
            self.stdout.write(f'    ({value}, "{label}"){marker}')
        
        if len(form_choices) > 5:
            self.stdout.write(f'    ... and {len(form_choices) - 5} more')
        
        self.stdout.write('')
        
        # Show what initial value would be set
        self.stdout.write(self.style.SUCCESS('Step 6: Initial value for ip_address field'))
        initial_value = primary_ip.ip_address.pk if primary_ip and primary_ip.ip_address else None
        self.stdout.write(f'  initial_value = {initial_value}')
        self.stdout.write(f'  Type: {type(initial_value).__name__ if initial_value else "None"}')
        self.stdout.write('')
        
        # Verify the initial value matches a choice
        choice_values = [choice[0] for choice in form_choices]
        if initial_value in choice_values:
            self.stdout.write(self.style.SUCCESS(f'  ✓ Initial value {initial_value} IS in form choices'))
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ Initial value {initial_value} NOT in form choices'))
            self.stdout.write(self.style.ERROR('    This is why the field appears empty!'))
        
        self.stdout.write('')
        
        # Additional diagnostics
        self.stdout.write(self.style.SUCCESS('Step 7: Additional diagnostics'))
        
        # Check if IP is in allowed ranges
        ip_address_str = primary_ip.ip_address.address
        allowed_ranges = ['192.168.10.', '192.168.11.', '192.168.50.', '192.168.70.']
        in_allowed_range = any(ip_address_str.startswith(prefix) for prefix in allowed_ranges)
        
        if in_allowed_range:
            self.stdout.write(f'  ✓ IP {ip_address_str} IS in allowed ranges')
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ IP {ip_address_str} NOT in allowed ranges'))
            self.stdout.write(f'    Allowed ranges: {", ".join(allowed_ranges)}')
            self.stdout.write(self.style.WARNING('    This is why the IP is not appearing in the dropdown!'))
        
        self.stdout.write('')
        
        # Check is_assigned status
        self.stdout.write(f'  IP is_assigned: {primary_ip.ip_address.is_assigned}')
        
        if primary_ip.ip_address.assigned_to_asset:
            self.stdout.write(f'  IP assigned_to_asset: {primary_ip.ip_address.assigned_to_asset.asset_tag}')
        else:
            self.stdout.write('  IP assigned_to_asset: None')
        
        self.stdout.write('')
        
        # Final summary
        self.stdout.write(self.style.SUCCESS('=== Summary ==='))
        
        if not in_allowed_range:
            self.stdout.write(self.style.ERROR('ISSUE FOUND: IP is outside allowed ranges'))
            self.stdout.write(f'  Current IP: {ip_address_str}')
            self.stdout.write(f'  Allowed ranges: {", ".join(allowed_ranges)}')
            self.stdout.write('')
            self.stdout.write('SOLUTION: Either:')
            self.stdout.write('  1. Update get_filtered_free_ips() to include this IP range')
            self.stdout.write('  2. Ensure IPs are in the allowed ranges')
        elif not current_ip_in_list:
            self.stdout.write(self.style.ERROR('ISSUE FOUND: Current IP not in available list'))
            self.stdout.write('  This could be due to a query issue in get_filtered_free_ips()')
        else:
            self.stdout.write(self.style.SUCCESS('No issues found! IP should display correctly.'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Debug complete!'))
