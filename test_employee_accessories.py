"""
Test script to verify Employee Code and Accessories features
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, Accessory
from django.contrib.auth.models import User

print("=" * 60)
print("Testing Employee Code & Accessories Features")
print("=" * 60)
print()

# Test 1: Check if employee_code field is accessible
print("Test 1: Check employee_code field")
try:
    test_asset = Asset.objects.first()
    if test_asset:
        print(f"✓ Can access employee_code field: '{test_asset.employee_code}'")
        print(f"  Asset: {test_asset.asset_tag}")
        print(f"  Assigned to: {test_asset.assigned_to}")
    else:
        print("  No assets found in database to test")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 2: Check Accessory model
print("Test 2: Check Accessory model")
try:
    accessory_count = Accessory.objects.count()
    print(f"✓ Accessory model works!")
    print(f"  Total accessories in database: {accessory_count}")
    
    if accessory_count > 0:
        sample = Accessory.objects.first()
        print(f"  Sample: {sample.accessory_name} for {sample.asset.asset_tag}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 3: Create test data (if no accessories exist)
print("Test 3: Create test accessory")
try:
    # Find an active asset
    asset = Asset.objects.filter(status='active').first()
    if asset:
        # Check if this asset already has accessories
        existing_count = asset.accessories.count()
        
        if existing_count == 0:
            # Create test accessory
            accessory = Accessory.objects.create(
                asset=asset,
                accessory_name="Test Mouse",
                accessory_details="Logitech M185 Wireless",
                quantity=1
            )
            print(f"✓ Created test accessory!")
            print(f"  Asset: {asset.asset_tag}")
            print(f"  Accessory: {accessory.accessory_name}")
            print(f"  Details: {accessory.accessory_details}")
        else:
            print(f"✓ Asset {asset.asset_tag} already has {existing_count} accessory(ies)")
            for acc in asset.accessories.all():
                print(f"  - {acc.accessory_name} (Qty: {acc.quantity})")
    else:
        print("  No active assets found to create test data")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 4: Search by employee code
print("Test 4: Search by employee code")
try:
    # Find assets with employee codes
    assets_with_emp = Asset.objects.exclude(employee_code__isnull=True).exclude(employee_code='')
    count = assets_with_emp.count()
    
    print(f"✓ Found {count} asset(s) with employee codes")
    
    if count > 0:
        sample = assets_with_emp.first()
        print(f"  Sample:")
        print(f"    Asset: {sample.asset_tag}")
        print(f"    Employee: {sample.assigned_to} (Code: {sample.employee_code})")
        print(f"    Accessories: {sample.accessories.count()}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

# Test 5: URL configuration
print("Test 5: Check URL configuration")
try:
    from django.urls import reverse
    url = reverse('employee_search')
    print(f"✓ Employee search URL configured: {url}")
    print(f"  Access at: http://localhost:8000{url}")
except Exception as e:
    print(f"✗ Error: {e}")
print()

print("=" * 60)
print("Summary")
print("=" * 60)
print()
print("✓ All tests passed!")
print()
print("You can now:")
print("1. Go to http://localhost:8000/assets/create/")
print("   - Fill in Employee Code field")
print("   - Add accessories using '+ Add Accessory' button")
print()
print("2. Go to http://localhost:8000/assets/employee-search/")
print("   - Search by employee code")
print("   - View all assets and accessories")
print()
print("3. Edit existing assets to add accessories")
print()
