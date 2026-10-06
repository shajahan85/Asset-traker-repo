import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress

print("=" * 60)
print("STEP 1: Fix IP 192.168.70.66 directly")
print("=" * 60)

try:
    ip = IPAddress.objects.get(address='192.168.70.66')
    assoc = AssetIPAddress.objects.filter(ip_address=ip, asset__status='active').first()
    if assoc:
        ip.is_assigned = True
        ip.assigned_to_asset = assoc.asset
        ip.save()
        print(f"  Fixed! IP 192.168.70.66 now assigned to asset {assoc.asset.asset_tag}")
    else:
        print(f"  No active AssetIPAddress record found for this IP!")
except IPAddress.DoesNotExist:
    print("  IP not found in pool!")

print("\n" + "=" * 60)
print("STEP 2: Fix ALL IPs that are in AssetIPAddress but have is_assigned=False")
print("=" * 60)

# Find all AssetIPAddress records with managed IPs where the IP is not marked as assigned
mismatched = AssetIPAddress.objects.filter(
    ip_address__isnull=False,
    asset__status='active',
    ip_address__is_assigned=False
).select_related('ip_address', 'asset')

print(f"\nFound {mismatched.count()} IPs that are assigned in junction table but NOT marked in IP pool:")
for assoc in mismatched:
    print(f"  - {assoc.ip_address.address} -> Asset {assoc.asset.asset_tag} ({assoc.asset.assigned_to})")
    assoc.ip_address.is_assigned = True
    assoc.ip_address.assigned_to_asset = assoc.asset
    assoc.ip_address.save()
    print(f"    FIXED!")

print("\n" + "=" * 60)
print("STEP 3: Verify the self-healing query (checking what get_all_ips_by_range_with_vms would see)")
print("=" * 60)

# This is what the self-healing code builds
asset_ip_associations_dict = {}
for assoc in AssetIPAddress.objects.filter(
    ip_address__isnull=False,
    asset__status='active'
).select_related('asset', 'ip_address'):
    asset_ip_associations_dict[assoc.ip_address_id] = assoc

print(f"\nTotal managed IPs in AssetIPAddress junction (active assets): {len(asset_ip_associations_dict)}")

# Check which ones are still marked as not assigned
still_unassigned = IPAddress.objects.filter(
    pk__in=asset_ip_associations_dict.keys(),
    is_assigned=False
)
print(f"IPs still marked as is_assigned=False after fix: {still_unassigned.count()}")
for ip in still_unassigned:
    print(f"  - {ip.address} (ID: {ip.pk})")

print("\n" + "=" * 60)
print("STEP 4: Verify 192.168.70.66 is now correct")
print("=" * 60)

ip = IPAddress.objects.get(address='192.168.70.66')
print(f"  is_assigned: {ip.is_assigned}")
print(f"  assigned_to_asset: {ip.assigned_to_asset}")
if ip.assigned_to_asset:
    print(f"    -> Asset: {ip.assigned_to_asset.asset_tag}, assigned_to: {ip.assigned_to_asset.assigned_to}")

print("\nDone! All fixes applied.")
