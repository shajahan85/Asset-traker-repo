#!/usr/bin/env python
"""Check why IP 192.168.11.79 is showing as free when it's assigned to Swetha."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, IPAddress, NetworkDevice, HyperVVM

def check_ip_issue():
    """Investigate the IP assignment issue."""
    
    print("=" * 70)
    print("Investigating IP 192.168.11.79 Issue")
    print("=" * 70)
    
    # Check BIDC1041 (Swetha's asset)
    print("\n1. Checking BIDC1041 (Swetha's asset):")
    try:
        asset = Asset.objects.get(asset_tag='BIDC1041')
        print(f"   Asset Tag: {asset.asset_tag}")
        print(f"   Assigned to: {asset.assigned_to}")
        print(f"   Status: {asset.status}")
        print(f"   IP Address (managed): {asset.ip_address.address if asset.ip_address else 'None'}")
        print(f"   IP Address ID: {asset.ip_address.id if asset.ip_address else 'None'}")
        print(f"   Manual IP: {asset.manual_ip or 'None'}")
    except Asset.DoesNotExist:
        print("   Asset BIDC1041 not found!")
    
    # Check IPAddress table for 192.168.11.79
    print("\n2. Checking IPAddress table for 192.168.11.79:")
    try:
        ip = IPAddress.objects.get(address='192.168.11.79')
        print(f"   IP exists in IPAddress table")
        print(f"   IP ID: {ip.id}")
        print(f"   Is assigned: {ip.is_assigned}")
        
        # Check what's using this IP
        print("\n3. Checking what's using this IP:")
        
        # Check active assets
        active_assets = Asset.objects.filter(ip_address=ip, status='active')
        print(f"   Active assets using this IP: {active_assets.count()}")
        for a in active_assets:
            print(f"     - {a.asset_tag}: {a.assigned_to} (status: {a.status})")
        
        # Check freed assets
        freed_assets = Asset.objects.filter(ip_address=ip, status='freed')
        print(f"   Freed assets using this IP: {freed_assets.count()}")
        for a in freed_assets:
            print(f"     - {a.asset_tag}: {a.assigned_to} (status: {a.status})")
        
        # Check scrapped assets
        scrapped_assets = Asset.objects.filter(ip_address=ip, status='scrapped')
        print(f"   Scrapped assets using this IP: {scrapped_assets.count()}")
        for a in scrapped_assets:
            print(f"     - {a.asset_tag}: {a.assigned_to} (status: {a.status})")
        
        # Check network devices
        try:
            network_device = NetworkDevice.objects.get(ip_address=ip)
            print(f"   Network device using this IP: {network_device.device_name}")
        except NetworkDevice.DoesNotExist:
            print(f"   No network device using this IP")
        
        # Check VMs
        vms = HyperVVM.objects.filter(ip_address=ip)
        print(f"   VMs using this IP: {vms.count()}")
        for vm in vms:
            print(f"     - {vm.name} (active: {vm.is_active})")
        
    except IPAddress.DoesNotExist:
        print("   IP 192.168.11.79 NOT found in IPAddress table!")
        print("   This IP might be a manual IP only")
    
    # Check for manual IP usage
    print("\n4. Checking for manual IP usage (192.168.11.79):")
    manual_ip_assets = Asset.objects.filter(manual_ip='192.168.11.79')
    print(f"   Assets with manual IP 192.168.11.79: {manual_ip_assets.count()}")
    for a in manual_ip_assets:
        print(f"     - {a.asset_tag}: {a.assigned_to} (status: {a.status})")
    
    # Check all active assets to find similar issues
    print("\n5. Checking for other assets with similar issues:")
    print("   (Active assets with manual IPs that might not be in IPAddress table)")
    
    active_with_manual = Asset.objects.filter(status='active', manual_ip__isnull=False, ip_address__isnull=True)
    print(f"   Found {active_with_manual.count()} active assets with manual IPs only")
    
    if active_with_manual.count() > 0:
        print("   Sample (first 10):")
        for a in active_with_manual[:10]:
            print(f"     - {a.asset_tag}: {a.assigned_to} - Manual IP: {a.manual_ip}")
    
    print("\n" + "=" * 70)
    print("Investigation Complete")
    print("=" * 70)

if __name__ == '__main__':
    check_ip_issue()
