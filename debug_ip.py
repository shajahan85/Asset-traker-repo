import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress

# Check the IPAddress record for 192.168.70.66
print("=" * 60)
print("CHECKING IP: 192.168.70.66")
print("=" * 60)

try:
    ip = IPAddress.objects.get(address='192.168.70.66')
    print(f"\nIPAddress record found:")
    print(f"  ID: {ip.pk}")
    print(f"  is_assigned: {ip.is_assigned}")
    print(f"  assigned_to_asset: {ip.assigned_to_asset}")
    if ip.assigned_to_asset:
        print(f"    -> Asset tag: {ip.assigned_to_asset.asset_tag}")
        print(f"    -> Assigned to: {ip.assigned_to_asset.assigned_to}")
    print(f"  guest_name: {ip.guest_name}")
    print(f"  freed_date: {ip.freed_date}")
except IPAddress.DoesNotExist:
    print("  IPAddress record NOT FOUND in IP pool!")

# Check AssetIPAddress junction table
print("\n" + "=" * 60)
print("CHECKING AssetIPAddress JUNCTION TABLE")
print("=" * 60)

# Check if this IP is referenced in AssetIPAddress
associations = AssetIPAddress.objects.filter(ip_address__address='192.168.70.66')
print(f"\nAssetIPAddress records referencing 192.168.70.66: {associations.count()}")
for assoc in associations:
    print(f"  - Asset: {assoc.asset.asset_tag} (assigned to: {assoc.asset.assigned_to})")
    print(f"    is_primary: {assoc.is_primary}")
    print(f"    ip_label: {assoc.ip_label}")
    print(f"    asset status: {assoc.asset.status}")

# Also check if any asset has this as manual_ip
print("\n" + "=" * 60)
print("CHECKING manual_ip FIELD ON ASSETS")
print("=" * 60)

manual_assets = Asset.objects.filter(manual_ip='192.168.70.66')
print(f"\nAssets with manual_ip='192.168.70.66': {manual_assets.count()}")
for asset in manual_assets:
    print(f"  - Asset: {asset.asset_tag}, assigned_to: {asset.assigned_to}, status: {asset.status}")

# Check if Shaiju appears anywhere
print("\n" + "=" * 60)
print("CHECKING FOR 'shaiju' IN ASSETS")
print("=" * 60)

shaiju_assets = Asset.objects.filter(assigned_to__icontains='shaiju')
print(f"\nAssets assigned to shaiju: {shaiju_assets.count()}")
for asset in shaiju_assets:
    print(f"  - Asset: {asset.asset_tag}, status: {asset.status}")
    primary_ip = asset.get_primary_ip()
    if primary_ip:
        print(f"    Primary IP: {primary_ip.get_ip_display()} (is_primary={primary_ip.is_primary})")
    secondary_ips = asset.get_secondary_ips()
    for sec in secondary_ips:
        print(f"    Additional IP: {sec.get_ip_display()} (label={sec.ip_label})")

# Also show all AssetIPAddress for shaiju's assets
print("\n" + "=" * 60)
print("ALL AssetIPAddress records for Shaiju's assets:")
print("=" * 60)
for asset in shaiju_assets:
    all_ips = AssetIPAddress.objects.filter(asset=asset)
    for aip in all_ips:
        ip_display = aip.ip_address.address if aip.ip_address else aip.manual_ip
        print(f"  Asset {asset.asset_tag}: IP={ip_display}, is_primary={aip.is_primary}, label={aip.ip_label}")
        if aip.ip_address:
            print(f"    -> IPAddress.is_assigned={aip.ip_address.is_assigned}, assigned_to_asset={aip.ip_address.assigned_to_asset}")

print("\nDone.")
