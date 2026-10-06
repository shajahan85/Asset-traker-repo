import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress, Asset, AssetIPAddress, HyperVVM

print("=" * 60)
print("CHECKING HOST MACHINES WITH VMs")
print("=" * 60)

# Find all active VMs
active_vms = HyperVVM.objects.filter(is_active=True).select_related('host_machine', 'ip_address')
print(f"\nTotal active VMs: {active_vms.count()}")

# Get unique host assets
host_assets = set()
for vm in active_vms:
    if vm.host_machine:
        host_assets.add(vm.host_machine)

print(f"Unique host assets: {len(host_assets)}")

for host in host_assets:
    print(f"\n  Host: {host.asset_tag} (assigned to: {host.assigned_to})")
    print(f"    ip_address (old FK): {host.ip_address}")
    print(f"    manual_ip (old field): {host.manual_ip}")
    
    # Check the IPAddress record for the host
    if host.ip_address:
        ip = host.ip_address
        print(f"    IPAddress record: {ip.address}")
        print(f"      is_assigned: {ip.is_assigned}")
        print(f"      assigned_to_asset: {ip.assigned_to_asset}")
        if ip.assigned_to_asset:
            print(f"        -> {ip.assigned_to_asset.asset_tag}")
    
    # Check AssetIPAddress junction
    junction_records = AssetIPAddress.objects.filter(asset=host)
    print(f"    AssetIPAddress records: {junction_records.count()}")
    for j in junction_records:
        ip_display = j.ip_address.address if j.ip_address else f"manual:{j.manual_ip}"
        print(f"      - {ip_display} | primary={j.is_primary}")
    
    # List its VMs
    vms = host.hosted_vms.filter(is_active=True)
    print(f"    Active VMs: {vms.count()}")
    for vm in vms:
        vm_ip = vm.ip_address.address if vm.ip_address else vm.manual_ip or "No IP"
        print(f"      - {vm.name}: {vm_ip}")

# Now check: what does get_all_ips_by_range_with_vms see for these host IPs?
print("\n" + "=" * 60)
print("CHECKING WHAT THE FREE IP PAGE WOULD SHOW")
print("=" * 60)

from assets.services.ip_management_service import IPManagementService

for host in host_assets:
    if host.ip_address:
        ip = host.ip_address
        # Simulate what the view does
        occupant_info = IPManagementService.get_ip_occupant_info(ip)
        print(f"\n  Host IP {ip.address} ({host.asset_tag}):")
        print(f"    Occupant type: {occupant_info['type']}")
        print(f"    Occupant name: {occupant_info['name']}")
        
        # Check if ip.assigned_to_asset is set correctly
        ip.refresh_from_db()
        print(f"    After refresh - is_assigned: {ip.is_assigned}, assigned_to_asset: {ip.assigned_to_asset}")

print("\nDone.")
