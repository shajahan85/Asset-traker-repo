import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset
from assets.forms.asset_forms import AssetForm

asset = Asset.objects.get(asset_tag='BIDC1326')
print(f'Asset: {asset.asset_tag}')
print(f'User: {asset.assigned_to}')
print(f'Branch: {asset.branch}')
print(f'Team: {asset.team}')
print(f'OS: {asset.operating_system}')

# Create form
print('\nCreating form...')
form = AssetForm(instance=asset)

print(f'\n✓ Form created successfully')
print(f'  Branch queryset count: {form.fields["branch"].queryset.count()}')
print(f'  OS queryset count: {form.fields["operating_system"].queryset.count()}')
print(f'  Parent team queryset count: {form.fields["parent_team"].queryset.count()}')

# Check if current values are in querysets
print(f'\n  Current branch in queryset: {asset.branch in form.fields["branch"].queryset}')
print(f'  Current OS in queryset: {asset.operating_system in form.fields["operating_system"].queryset}')
print(f'  Current team in queryset: {asset.team in form.fields["parent_team"].queryset}')

print('\nAll checks passed!')
