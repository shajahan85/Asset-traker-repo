"""
Data migration: Create AssetIPAddress records for assets that have old IP data
but no junction table records.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.db import transaction
from django.db.models import Q
from assets.models import Asset, IPAddress, AssetIPAddress

print("=" * 60)
print("MIGRATING OLD IP DATA TO AssetIPAddress JUNCTION TABLE")
print("=" * 60)

# Find active assets with old IP data but no primary IP in junction table
assets_needing_migration = Asset.objects.filter(
    status='active'
).exclude(
    asset_ip_addresses__is_primary=True
)

migrated = 0
skipped = 0
errors = 0

with transaction.atomic():
    for asset in assets_needing_migration:
        try:
            # Check if asset has an old managed IP (FK)
            if asset.ip_address:
                AssetIPAddress.objects.create(
                    asset=asset,
                    ip_address=asset.ip_address,
                    manual_ip=None,
                    is_primary=True
                )
                # Ensure the IP is marked as assigned
                if not asset.ip_address.is_assigned:
                    asset.ip_address.is_assigned = True
                    asset.ip_address.assigned_to_asset = asset
                    asset.ip_address.save()
                migrated += 1
                print(f"  Migrated {asset.asset_tag}: managed IP {asset.ip_address.address}")

            # Check if asset has an old manual IP
            elif asset.manual_ip:
                AssetIPAddress.objects.create(
                    asset=asset,
                    ip_address=None,
                    manual_ip=asset.manual_ip,
                    is_primary=True
                )
                migrated += 1
                print(f"  Migrated {asset.asset_tag}: manual IP {asset.manual_ip}")

            else:
                # No IP data at all, skip
                skipped += 1

        except Exception as e:
            errors += 1
            print(f"  ERROR migrating {asset.asset_tag}: {e}")

print(f"\n{'=' * 60}")
print(f"MIGRATION COMPLETE")
print(f"  Migrated: {migrated}")
print(f"  Skipped (no IP data): {skipped}")
print(f"  Errors: {errors}")
print(f"{'=' * 60}")

# Simple verification
still_missing = Asset.objects.filter(
    status='active'
).filter(
    Q(ip_address__isnull=False) | Q(manual_ip__isnull=False)
).exclude(
    manual_ip=''
).exclude(
    asset_ip_addresses__is_primary=True
).count()

print(f"\nAssets still missing primary IP in junction (with old IP data): {still_missing}")
