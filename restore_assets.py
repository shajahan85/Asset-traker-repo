from assets.models import Asset

asset_tags = ['1168', '1198', '1199', '1228', '1306', '1311', '1388', '1389']

for tag in asset_tags:
    try:
        asset = Asset.objects.get(asset_tag=tag, status='freed')
        old_tag = asset.asset_tag
        asset.asset_tag = f'BIDC{tag}'
        asset.status = 'active'
        asset.freed_date = None
        asset.health_status = None
        asset.issues_description = None
        asset.save()
        print(f'✓ Restored {old_tag} -> {asset.asset_tag} (status: {asset.status})')
    except Asset.DoesNotExist:
        print(f'✗ Asset {tag} not found in freed systems')
    except Exception as e:
        print(f'✗ Error restoring {tag}: {str(e)}')

print(f'\nTotal assets processed: {len(asset_tags)}')
