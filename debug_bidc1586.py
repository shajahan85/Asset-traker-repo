import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress

print("=" * 60)
print("CHECKING ASSET BIDC1586")
print("=" * 60)

try:
    asset = Asset.objects.get(asset_tag='BIDC1586')
    print(f"\nAsset found:")
    print(f"  asset_tag: {asset.asset_tag}")
    print(f"  assigned_to: {asset.assigned_to}")
    print(f"  status: {asset.status}")
    print(f"  ip_address (old FK field): {asset.ip_address}")
    print(f"  manual_ip (old field): {asset.manual_ip}")
    
    # Check get_primary_ip (what the template uses)
    primary_ip = asset.get_primary_ip()
    print(f"\n  get_primary_ip() returns: {primary_ip}")
    if primary_ip:
        print(f"    -> ip_address FK: {primary_ip.ip_address}")
        print(f"    -> manual_ip: {primary_ip.manual_ip}")
        print(f"    -> is_primary: {primary_ip.is_primary}")
        print(f"    -> get_ip_display(): {primary_ip.get_ip_display()}")
    else:
        print("    -> None! This is why the main page shows '—'")
    
    # Check all AssetIPAddress records
    all_ips = AssetIPAddress.objects.filter(asset=asset)
    print(f"\n  All AssetIPAddress records: {all_ips.count()}")
    for aip in all_ips:
        ip_display = aip.ip_address.address if aip.ip_address else f"manual:{aip.manual_ip}"
        print(f"    - {ip_display} | is_primary={aip.is_primary} | label={aip.ip_label}")
        
except Asset.DoesNotExist:
    print("Asset BIDC1586 not found!")

# Also check a few other assets that might show the same problem
print("\n" + "=" * 60)
print("CHECKING ASSETS WITH NO PRIMARY IP IN JUNCTION TABLE")
print("=" * 60)

# Get active assets that have no primary IP in AssetIPAddress
from django.db.models import Q, Exists, OuterRef

assets_without_primary = Asset.objects.filter(
    status='active'
).exclude(
    asset_ip_addresses__is_primary=True
).order_by('asset_tag')[:10]

print(f"\nFirst 10 active assets WITHOUT a primary IP in AssetIPAddress table:")
for asset in assets_without_primary:
    has_old_ip = asset.ip_address is not None
    has_manual = asset.manual_ip is not None and asset.manual_ip != ''
    all_junction = AssetIPAddress.objects.filter(asset=asset).count()
    print(f"  {asset.asset_tag} | old FK ip: {asset.ip_address} | manual_ip: {asset.manual_ip} | junction records: {all_junction}")

print(f"\nTotal active assets without primary IP: {Asset.objects.filter(status='active').exclude(asset_ip_addresses__is_primary=True).count()}")
print(f"Total active assets: {Asset.objects.filter(status='active').count()}")

print("\nDone.")
