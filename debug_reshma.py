import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetIPAddress, IPAddress

print("=" * 60)
print("CHECKING IP 192.168.70.250")
print("=" * 60)

# Check IPAddress pool record
try:
    ip = IPAddress.objects.get(address='192.168.70.250')
    print(f"IPAddress record (ID: {ip.pk}):")
    print(f"  is_assigned: {ip.is_assigned}")
    print(f"  assigned_to_asset: {ip.assigned_to_asset}")
    print(f"  manually_occupied: {ip.manually_occupied}")
    print(f"  guest_name: {ip.guest_name}")
except IPAddress.DoesNotExist:
    print("  NOT FOUND in IP pool!")

# Check AssetIPAddress junction - managed FK
assocs = AssetIPAddress.objects.filter(ip_address__address='192.168.70.250')
print(f"\nAssetIPAddress (managed FK): {assocs.count()}")
for a in assocs:
    print(f"  Asset: {a.asset.asset_tag}, assigned_to: {a.asset.assigned_to}, primary={a.is_primary}, label={a.ip_label}, status={a.asset.status}")

# Check AssetIPAddress junction - manual IP
manual_assocs = AssetIPAddress.objects.filter(manual_ip='192.168.70.250')
print(f"\nAssetIPAddress (manual_ip): {manual_assocs.count()}")
for a in manual_assocs:
    print(f"  Asset: {a.asset.asset_tag}, assigned_to: {a.asset.assigned_to}, primary={a.is_primary}, label={a.ip_label}, status={a.asset.status}")

# Check Reshma's assets
print("\n" + "=" * 60)
print("CHECKING RESHMA'S ASSETS")
print("=" * 60)
reshma = Asset.objects.filter(assigned_to__icontains='reshma')
for asset in reshma:
    print(f"\n  Asset: {asset.asset_tag}, status: {asset.status}")
    print(f"  ip_address FK: {asset.ip_address}")
    print(f"  manual_ip: {asset.manual_ip}")
    all_ips = AssetIPAddress.objects.filter(asset=asset)
    print(f"  AssetIPAddress records: {all_ips.count()}")
    for aip in all_ips:
        ip_val = aip.ip_address.address if aip.ip_address else f"manual:{aip.manual_ip}"
        print(f"    - {ip_val} | primary={aip.is_primary} | label={aip.ip_label}")

print("\nDone.")
