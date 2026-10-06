import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetIPAddress, IPAddress

# 1. Clean up the stale junction record from the freed test asset
stale = AssetIPAddress.objects.filter(
    manual_ip='192.168.70.250',
    asset__asset_tag='TEST-WORKFLOW-599'
)
print(f"Removing stale junction record from TEST-WORKFLOW-599: {stale.count()}")
stale.delete()

# 2. Fix the IPAddress pool record to point to Reshma's active asset
ip = IPAddress.objects.get(address='192.168.70.250')
reshma_asset = Asset.objects.get(asset_tag='BIDC1414')
ip.is_assigned = True
ip.assigned_to_asset = reshma_asset
ip.save()
print(f"Fixed: 192.168.70.250 now points to {reshma_asset.asset_tag} ({reshma_asset.assigned_to})")

# 3. Verify
ip.refresh_from_db()
print(f"\nVerification:")
print(f"  is_assigned: {ip.is_assigned}")
print(f"  assigned_to_asset: {ip.assigned_to_asset}")
print(f"  assigned_to_asset.assigned_to: {ip.assigned_to_asset.assigned_to}")

print("\nDone.")
