import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, IPRange

print("=" * 60)
print("CHECKING IP 192.168.10.100")
print("=" * 60)

# Check if it exists
exists = IPAddress.objects.filter(address='192.168.10.100').exists()
print(f"\n192.168.10.100 exists in IPAddress table: {exists}")

if not exists:
    # Find the correct IP range for 192.168.10.x
    ip_range = IPRange.objects.filter(range_pattern__startswith='192.168.10.').first()
    if not ip_range:
        # Try a broader search
        ip_range = IPRange.objects.filter(range_pattern__contains='192.168.10').first()
    
    if ip_range:
        print(f"\nFound IP range: {ip_range.range_pattern} (ID: {ip_range.pk})")
        # Create the missing IP
        ip = IPAddress.objects.create(
            address='192.168.10.100',
            ip_range=ip_range,
            is_assigned=False
        )
        print(f"Created IPAddress: {ip.address} (ID: {ip.pk})")
    else:
        print("\nNo matching IP range found! Available ranges:")
        for r in IPRange.objects.all():
            print(f"  - {r.range_pattern}")
else:
    ip = IPAddress.objects.get(address='192.168.10.100')
    print(f"  ID: {ip.pk}")
    print(f"  ip_range: {ip.ip_range.range_pattern}")
    print(f"  is_assigned: {ip.is_assigned}")
    print(f"  assigned_to_asset: {ip.assigned_to_asset}")

# Also check what IPs exist around 192.168.10.100
print("\n" + "=" * 60)
print("IPs around 192.168.10.100:")
print("=" * 60)
nearby = IPAddress.objects.filter(
    address__startswith='192.168.10.'
).order_by('address')

# Find IPs between .95 and .105
for ip in nearby:
    parts = ip.address.split('.')
    last_octet = int(parts[3])
    if 95 <= last_octet <= 105:
        print(f"  {ip.address} - assigned: {ip.is_assigned}")

print("\nDone.")
