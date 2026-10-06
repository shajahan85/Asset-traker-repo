import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset
from assets.forms.asset_forms import AssetForm

asset = Asset.objects.get(asset_tag='BIDC1544')
print(f'Asset: {asset.asset_tag}')
print(f'User: {asset.assigned_to}')
print(f'OS: {asset.operating_system}')
print(f'OS ID: {asset.operating_system.id if asset.operating_system else None}')

# Get primary IP
primary_ip = asset.get_primary_ip()
print(f'Primary IP: {primary_ip}')
if primary_ip:
    print(f'  - IP Address: {primary_ip.ip_address}')
    print(f'  - Manual IP: {primary_ip.manual_ip}')

# Create form
form = AssetForm(instance=asset)

# Check if OS is in queryset
if asset.operating_system:
    os_in_qs = asset.operating_system in form.fields['operating_system'].queryset
    print(f'\nOS in queryset: {os_in_qs}')
    
    os_ids = list(form.fields['operating_system'].queryset.values_list('id', flat=True))
    print(f'OS queryset IDs (first 10): {os_ids[:10]}')
    print(f'Current OS ID {asset.operating_system.id} in list: {asset.operating_system.id in os_ids}')
    
    # Get all OS objects
    all_os_in_qs = list(form.fields['operating_system'].queryset.values_list('id', 'name'))
    print(f'\nAll OS in queryset:')
    for os_id, os_name in all_os_in_qs[:20]:
        marker = ' <-- CURRENT' if os_id == asset.operating_system.id else ''
        print(f'  ID {os_id}: {os_name}{marker}')
