import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress, HyperVVM

print("=" * 60)
print("CHECKING VM IP: 192.168.10.41")
print("=" * 60)

# Check the VM IP in the pool
try:
    vm_ip = IPAddress.objects.get(address='192.168.10.41')
    print(f"\nIPAddress record:")
    print(f"  ID: {vm_ip.pk}")
    print(f"  is_assigned: {vm_ip.is_assigned}")
    print(f"  assigned_to_asset: {vm_ip.assigned_to_asset}")
    
    # Check VM relationship
    vms = vm_ip.vm.all()
    print(f"  vm.all() count: {vms.count()}")
    for vm in vms:
        print(f"    VM: {vm.name}, is_active: {vm.is_active}, host: {vm.host_machine.asset_tag}")
except IPAddress.DoesNotExist:
    print("  NOT FOUND in IP pool!")

# Check AssetIPAddress junction for this IP
assocs = AssetIPAddress.objects.filter(ip_address__address='192.168.10.41')
print(f"\n  AssetIPAddress records for 192.168.10.41: {assocs.count()}")
for a in assocs:
    print(f"    Asset: {a.asset.asset_tag}, is_primary={a.is_primary}, status={a.asset.status}")

# Manual IP check
manual_assocs = AssetIPAddress.objects.filter(manual_ip='192.168.10.41')
print(f"  AssetIPAddress with manual_ip='192.168.10.41': {manual_assocs.count()}")
for a in manual_assocs:
    print(f"    Asset: {a.asset.asset_tag}, is_primary={a.is_primary}, status={a.asset.status}")

print("\n" + "=" * 60)
print("CHECKING HOST IP: 192.168.11.127")
print("=" * 60)

# Check the host IP in the pool
try:
    host_ip = IPAddress.objects.get(address='192.168.11.127')
    print(f"\nIPAddress record:")
    print(f"  ID: {host_ip.pk}")
    print(f"  is_assigned: {host_ip.is_assigned}")
    print(f"  assigned_to_asset: {host_ip.assigned_to_asset}")
    if host_ip.assigned_to_asset:
        print(f"    -> Asset: {host_ip.assigned_to_asset.asset_tag}, assigned_to: {host_ip.assigned_to_asset.assigned_to}")
        # Check hosted VMs
        hosted = host_ip.assigned_to_asset.hosted_vms.filter(is_active=True)
        print(f"    -> Hosted VMs: {hosted.count()}")
        for vm in hosted:
            print(f"       - {vm.name}: {vm.get_display_ip()}")
except IPAddress.DoesNotExist:
    print("  NOT FOUND in IP pool!")

# Check AssetIPAddress junction for host IP
assocs = AssetIPAddress.objects.filter(ip_address__address='192.168.11.127')
print(f"\n  AssetIPAddress records (managed FK): {assocs.count()}")
for a in assocs:
    print(f"    Asset: {a.asset.asset_tag}, is_primary={a.is_primary}")

manual_assocs = AssetIPAddress.objects.filter(manual_ip='192.168.11.127')
print(f"  AssetIPAddress records (manual_ip): {manual_assocs.count()}")
for a in manual_assocs:
    print(f"    Asset: {a.asset.asset_tag}, is_primary={a.is_primary}, status={a.asset.status}")
    # Check hosted VMs for this asset
    hosted = a.asset.hosted_vms.filter(is_active=True)
    print(f"    -> Hosted VMs on this asset: {hosted.count()}")
    for vm in hosted:
        print(f"       - {vm.name}: {vm.get_display_ip()}")

# Check what get_all_ips_by_range_with_vms would produce for these IPs
print("\n" + "=" * 60)
print("SIMULATING FREE IP PAGE LOGIC")
print("=" * 60)

# For VM IP 192.168.10.41
try:
    vm_ip = IPAddress.objects.get(address='192.168.10.41')
    vm_queryset = vm_ip.vm.all()
    is_vm = vm_queryset.exists()
    print(f"\n  192.168.10.41:")
    print(f"    is_vm (vm.all().exists()): {is_vm}")
    if is_vm:
        vm_obj = vm_queryset.first()
        print(f"    vm: {vm_obj.name}")
        print(f"    -> Would show as occupant_type='vm'")
    elif vm_ip.assigned_to_asset:
        print(f"    -> Would show as occupant_type='asset' (assigned_to: {vm_ip.assigned_to_asset.assigned_to})")
    elif not vm_ip.is_assigned:
        print(f"    -> Would show as occupant_type='free'")
except IPAddress.DoesNotExist:
    print(f"  192.168.10.41: NOT IN POOL")

# For Host IP 192.168.11.127
try:
    host_ip = IPAddress.objects.get(address='192.168.11.127')
    vm_queryset = host_ip.vm.all()
    is_vm = vm_queryset.exists()
    print(f"\n  192.168.11.127:")
    print(f"    is_assigned: {host_ip.is_assigned}")
    print(f"    assigned_to_asset: {host_ip.assigned_to_asset}")
    print(f"    is_vm: {is_vm}")
    if host_ip.assigned_to_asset:
        hosted = host_ip.assigned_to_asset.hosted_vms.filter(is_active=True)
        print(f"    hosted_vms count: {hosted.count()}")
        print(f"    -> Would show as occupant_type='asset' with hosted VMs")
    elif not host_ip.is_assigned:
        print(f"    -> Would show as occupant_type='free' *** THIS IS THE BUG ***")
except IPAddress.DoesNotExist:
    print(f"  192.168.11.127: NOT IN POOL")

print("\nDone.")
