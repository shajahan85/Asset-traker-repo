import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetIPAddress

asset = Asset.objects.get(asset_tag='BIDC1331')

# Check if primary exists
primary = asset.get_primary_ip()
if not primary:
    # Create primary junction record from old FK
    if asset.ip_address:
        AssetIPAddress.objects.create(
            asset=asset,
            ip_address=asset.ip_address,
            manual_ip=None,
            is_primary=True
        )
        print(f"Created primary IP record for {asset.asset_tag}: {asset.ip_address.address}")
    elif asset.manual_ip:
        AssetIPAddress.objects.create(
            asset=asset,
            ip_address=None,
            manual_ip=asset.manual_ip,
            is_primary=True
        )
        print(f"Created primary IP record for {asset.asset_tag}: {asset.manual_ip}")
else:
    print(f"Primary already exists: {primary.get_ip_display()}")
