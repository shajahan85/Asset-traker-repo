import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, AssetIPAddress

assets = Asset.objects.filter(assigned_to__icontains='kharunnisa')
print(f"Assets for Kharunnisa: {assets.count()}")

for asset in assets:
    print(f"\nAsset: {asset.asset_tag}")
    print(f"  assigned_to: {asset.assigned_to}")
    print(f"  status: {asset.status}")
    print(f"  system_type: {asset.system_type}")
    print(f"  branch: {asset.branch}")
    print(f"  team: {asset.team}")
    print(f"  ip_address FK: {asset.ip_address}")
    print(f"  manual_ip: {asset.manual_ip}")
    print(f"  hardware_serial_number: '{asset.hardware_serial_number}'")
    
    # Check all AssetIPAddress records
    all_ips = AssetIPAddress.objects.filter(asset=asset)
    print(f"\n  AssetIPAddress records: {all_ips.count()}")
    for aip in all_ips:
        ip_val = aip.ip_address.address if aip.ip_address else f"manual:{aip.manual_ip}"
        print(f"    - {ip_val} | primary={aip.is_primary} | label='{aip.ip_label}'")
        if aip.ip_address:
            print(f"      ip_address.pk={aip.ip_address.pk}")

    # Simulate what the form would do
    print(f"\n  Simulating form validation...")
    from assets.forms.asset_forms import AssetForm
    
    # Check if system_type requires serial number
    if asset.system_type in ['Laptop', 'All-in-One PC']:
        print(f"  ** system_type is '{asset.system_type}' - requires hardware_serial_number")
        if not asset.hardware_serial_number or not asset.hardware_serial_number.strip():
            print(f"  ** PROBLEM: hardware_serial_number is empty! This will fail validation.")

print("\nDone.")
