import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()
from assets.models import HyperVVM, IPAddress
vm = HyperVVM.objects.get(name='N8N')
print(f"VM: {vm.name}")
print(f"  ip_address FK: {vm.ip_address}")
print(f"  manual_ip: {vm.manual_ip}")
print(f"  host_machine: {vm.host_machine.asset_tag}")
print(f"  is_active: {vm.is_active}")
if vm.ip_address:
    print(f"  ip_address.address: {vm.ip_address.address}")
    print(f"  ip_address.is_assigned: {vm.ip_address.is_assigned}")

# Also check if 192.168.10.41 exists in pool and what its vm reverse looks like
try:
    ip = IPAddress.objects.get(address='192.168.10.41')
    print(f"\nIPAddress 192.168.10.41 vm reverse:")
    print(f"  vm.all(): {list(ip.vm.all())}")
    print(f"  vm.count(): {ip.vm.count()}")
except IPAddress.DoesNotExist:
    print("  IP not in pool")
