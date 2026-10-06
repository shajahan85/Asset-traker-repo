import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, IPAddress, AssetIPAddress
from assets.forms.asset_forms import AssetForm, AdditionalIPFormSet, get_filtered_free_ips

asset = Asset.objects.get(asset_tag='BIDC1569')
ip = asset.ip_address  # 192.168.11.164

print("=" * 60)
print(f"Asset: {asset.asset_tag}, IP: {ip.address} (pk={ip.pk})")
print("=" * 60)

# Check if the IP appears in the filtered free IPs list
primary_ip_record = asset.get_primary_ip()
current_ip_id = None
if primary_ip_record and primary_ip_record.ip_address:
    current_ip_id = primary_ip_record.ip_address.pk
    print(f"\nPrimary IP from junction: {primary_ip_record.ip_address.address} (pk={current_ip_id})")

available_ips = get_filtered_free_ips(include_current_ip_id=current_ip_id)
print(f"\nAvailable IPs in dropdown ({len(available_ips)} total):")

# Check if 192.168.11.164 is in the list
found = False
for avail_ip in available_ips:
    if avail_ip.pk == ip.pk:
        found = True
        print(f"  FOUND: {avail_ip.address} (pk={avail_ip.pk})")
        break

if not found:
    print(f"  ** NOT FOUND! IP {ip.address} (pk={ip.pk}) is NOT in the dropdown choices!")
    print(f"  ** This means form submission with this IP selected will FAIL validation!")
    print(f"\n  Checking why:")
    print(f"    IP is_assigned: {ip.is_assigned}")
    print(f"    IP assigned_to_asset: {ip.assigned_to_asset}")
    
    # Check the allowed ranges
    allowed_ranges = ['192.168.10.', '192.168.11.', '192.168.50.', '192.168.70.']
    in_range = any(ip.address.startswith(r) for r in allowed_ranges)
    print(f"    IP in allowed range: {in_range}")
    
    # Check what get_filtered_free_ips does
    from django.db import models
    range_query = models.Q()
    for range_prefix in allowed_ranges:
        range_query |= models.Q(address__startswith=range_prefix)
    
    if current_ip_id:
        test_qs = IPAddress.objects.filter(
            (models.Q(is_assigned=False) & range_query) | 
            models.Q(pk=current_ip_id)
        )
        print(f"    Query with include_current_ip_id={current_ip_id}: {test_qs.filter(pk=ip.pk).exists()}")
    else:
        print(f"    current_ip_id is None - the include filter isn't working!")
else:
    print(f"  IP is in the dropdown - this should work fine.")

# Also simulate form validation
print("\n" + "=" * 60)
print("SIMULATING FORM SUBMISSION")
print("=" * 60)

# Minimal POST data (just changing the name)
from django.test import RequestFactory
post_data = {
    'asset_tag': 'BIDC1569',
    'system_type': 'Desktop',
    'branch': str(asset.branch_id),
    'assigned_to': 'Kharunnisa New Name',
    'ip_address': str(ip.pk),  # The managed IP
    'primary_ip_type': 'managed',
    'parent_team': str(asset.team.parent_id) if asset.team and asset.team.parent else str(asset.team_id) if asset.team else '',
    'sub_team': str(asset.team_id) if asset.team and asset.team.parent else '',
    'team': str(asset.team_id) if asset.team else '',
    # Formset management data
    'asset_ip_addresses-TOTAL_FORMS': '1',
    'asset_ip_addresses-INITIAL_FORMS': '1',
    'asset_ip_addresses-MIN_NUM_FORMS': '0',
    'asset_ip_addresses-MAX_NUM_FORMS': '10',
    # Existing additional IP form data (the primary in junction)
    'asset_ip_addresses-0-id': str(primary_ip_record.pk) if primary_ip_record else '',
    'asset_ip_addresses-0-ip_type': 'managed',
    'asset_ip_addresses-0-ip_address': str(primary_ip_record.ip_address.pk) if primary_ip_record and primary_ip_record.ip_address else '',
    'asset_ip_addresses-0-manual_ip': '',
    'asset_ip_addresses-0-ip_label': 'Primary',
}

form = AssetForm(post_data, instance=asset)
print(f"\nForm is_valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Form errors: {form.errors}")

# Check formset
formset = AdditionalIPFormSet(
    post_data,
    instance=asset,
    queryset=asset.asset_ip_addresses.filter(is_primary=False)
)
print(f"\nFormset is_valid: {formset.is_valid()}")
if not formset.is_valid():
    print(f"Formset errors: {formset.errors}")
    print(f"Non-form errors: {formset.non_form_errors()}")

print("\nDone.")
