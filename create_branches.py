"""Script to create initial branches and assign existing assets to Kochi."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Branch, Asset

# Create branches
branches_data = [
    {'name': 'Kochi', 'code': 'KCH'},
    {'name': 'Pune', 'code': 'PUN'},
    {'name': 'Bangalore', 'code': 'BLR'},
    {'name': 'Delhi', 'code': 'DEL'},
]

print("Creating branches...")
for branch_data in branches_data:
    branch, created = Branch.objects.get_or_create(
        name=branch_data['name'],
        defaults={'code': branch_data['code']}
    )
    if created:
        print(f"✓ Created branch: {branch.name}")
    else:
        print(f"- Branch already exists: {branch.name}")

# Assign all existing assets to Kochi
kochi_branch = Branch.objects.get(name='Kochi')
assets_updated = Asset.objects.filter(branch__isnull=True).update(branch=kochi_branch)

print(f"\n✓ Assigned {assets_updated} existing assets to Kochi branch")
print("\nBranch setup complete!")
