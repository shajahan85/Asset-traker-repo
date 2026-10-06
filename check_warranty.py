import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset

# Check how many assets have warranty dates
with_warranty = Asset.objects.filter(warranty_expiration__isnull=False)
print(f"Assets with warranty_expiration set: {with_warranty.count()}")
print(f"Total active assets: {Asset.objects.filter(status='active').count()}")

# Show the ones that have warranty dates
for asset in with_warranty[:10]:
    print(f"  {asset.asset_tag} | status={asset.status} | warranty={asset.warranty_expiration}")

# Also check if maybe the field is being saved as empty string instead of null
empty_warranty = Asset.objects.filter(warranty_expiration='')
print(f"\nAssets with empty string warranty: {empty_warranty.count()}")
