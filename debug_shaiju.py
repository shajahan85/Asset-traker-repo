import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress

print("=" * 60)
print("FINDING SHAIJU'S ASSETS AND ALL THEIR IPs")
print("=" * 60)

# Search for shaiju in any form
shaiju_assets = Asset.objects.filter(assigned_to__icontains='shaiju')
print(f"\nAssets with 'shaiju' in assigned_to: {shaiju_assets.count()}")

for asset in shaiju_assets:
    print(f"\n  Asset: {asset.asset_tag}")
    print(f"  Status: {asset.status}")
    print(f"  Assigned to: {asset.assigned_to}")
    print(f"  System type: {asset.system_type}")
    print(f"  ip_address (old FK): {asset.ip_address}")
    print(f"  manual_ip (old field): {asset.manual_ip}")
    
    # Check all AssetIPAddress records
    all_ips = AssetIPAddress.objects.filter(asset=asset).select_related('ip_address')
    print(f"  AssetIPAddress records: {all_ips.count()}")
    for aip in all_ips:
        ip_display = aip.ip_address.address if aip.ip_address else f"manual:{aip.manual_ip}"
        print(f"    - {ip_display} | primary={aip.is_primary} | label={aip.ip_label}")
        if aip.ip_address:
            print(f"      IPAddress record: is_assigned={aip.ip_address.is_assigned}, assigned_to={aip.ip_address.assigned_to_asset}")

# Also check if 192.168.70.66 appears in ANY AssetIPAddress record (including non-active)
print("\n" + "=" * 60)
print("ALL AssetIPAddress records referencing IP 192.168.70.66")
print("=" * 60)

try:
    ip_obj = IPAddress.objects.get(address='192.168.70.66')
    all_assocs = AssetIPAddress.objects.filter(ip_address=ip_obj)
    print(f"\nTotal records: {all_assocs.count()}")
    for assoc in all_assocs:
        print(f"  Asset: {assoc.asset.asset_tag}, status={assoc.asset.status}, assigned_to={assoc.asset.assigned_to}")
        print(f"    is_primary={assoc.is_primary}, label={assoc.ip_label}")
except IPAddress.DoesNotExist:
    print("  IP not in pool")

# Also check if 192.168.70.66 was used as manual_ip in AssetIPAddress
manual_assocs = AssetIPAddress.objects.filter(manual_ip='192.168.70.66')
print(f"\nAssetIPAddress with manual_ip='192.168.70.66': {manual_assocs.count()}")
for assoc in manual_assocs:
    print(f"  Asset: {assoc.asset.asset_tag}, status={assoc.asset.status}")

# Show the IP from the pool
print("\n" + "=" * 60)
print("IP 192.168.70.66 in the IP pool")
print("=" * 60)
try:
    ip = IPAddress.objects.get(address='192.168.70.66')
    print(f"  ID: {ip.pk}")
    print(f"  is_assigned: {ip.is_assigned}")
    print(f"  assigned_to_asset: {ip.assigned_to_asset}")
    print(f"  ip_range: {ip.ip_range}")
except IPAddress.DoesNotExist:
    print("  NOT FOUND")

print("\nDone.")
