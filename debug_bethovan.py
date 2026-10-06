import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetIPAddress, IPAddress

# Find bethovan's asset
assets = Asset.objects.filter(assigned_to__icontains='bethovan')
if not assets.exists():
    assets = Asset.objects.filter(asset_tag__icontains='bethovan')
if not assets.exists():
    # Try searching more broadly
    print("No asset found for 'bethovan'. Checking recent assets...")
    recent = Asset.objects.filter(status='active').order_by('-id')[:5]
    for a in recent:
        print(f"  {a.asset_tag} - {a.assigned_to} - created: {a.id}")
    assets = recent[:1]  # Use most recent

for asset in assets:
    print(f"\nAsset: {asset.asset_tag}")
    print(f"  assigned_to: {asset.assigned_to}")
    print(f"  ip_address (old FK): {asset.ip_address}")
    if asset.ip_address:
        print(f"    -> address: {asset.ip_address.address}")
        print(f"    -> is_assigned: {asset.ip_address.is_assigned}")
    print(f"  manual_ip (old field): {asset.manual_ip}")
    
    # Check primary IP
    primary = asset.get_primary_ip()
    print(f"\n  get_primary_ip(): {primary}")
    if primary:
        print(f"    -> ip_address FK: {primary.ip_address}")
        print(f"    -> manual_ip: {primary.manual_ip}")
        print(f"    -> is_primary: {primary.is_primary}")
        print(f"    -> get_ip_display(): {primary.get_ip_display()}")

    # Check all AssetIPAddress records
    all_ips = AssetIPAddress.objects.filter(asset=asset)
    print(f"\n  All AssetIPAddress records: {all_ips.count()}")
    for aip in all_ips:
        ip_val = aip.ip_address.address if aip.ip_address else f"manual:{aip.manual_ip}"
        print(f"    - {ip_val} | primary={aip.is_primary} | label={aip.ip_label}")
        if aip.ip_address:
            print(f"      IPAddress: is_assigned={aip.ip_address.is_assigned}, assigned_to_asset={aip.ip_address.assigned_to_asset}")

    # Check what shows on the free IP page for these IPs
    print(f"\n  Checking free IP page status for this asset's IPs:")
    if asset.ip_address:
        ip = asset.ip_address
        print(f"    Old FK IP ({ip.address}): is_assigned={ip.is_assigned}, assigned_to={ip.assigned_to_asset}")
    for aip in all_ips:
        if aip.ip_address:
            ip = aip.ip_address
            print(f"    Junction IP ({ip.address}): is_assigned={ip.is_assigned}, assigned_to={ip.assigned_to_asset}")

print("\nDone.")
