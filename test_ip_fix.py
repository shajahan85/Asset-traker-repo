#!/usr/bin/env python
"""Test the IP fix for manual IP assignments."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress
from assets.services.ip_management_service import IPManagementService

def test_ip_fix():
    """Test that manual IPs are now correctly identified as occupied."""
    
    print("=" * 70)
    print("Testing IP Fix for Manual IP Assignments")
    print("=" * 70)
    
    # Test IP 192.168.11.79 (Swetha's manual IP)
    print("\n1. Testing IP 192.168.11.79 (Swetha's manual IP):")
    try:
        ip = IPAddress.objects.get(address='192.168.11.79')
        print(f"   IP Address: {ip.address}")
        print(f"   Is Assigned (database): {ip.is_assigned}")
        
        # Get occupant info using the updated method
        occupant_info = IPManagementService.get_ip_occupant_info(ip)
        print(f"   Occupant Type: {occupant_info['type']}")
        print(f"   Occupant Name: {occupant_info['name']}")
        if occupant_info['object']:
            print(f"   Asset Tag: {occupant_info['object'].asset_tag}")
        
        if occupant_info['type'] == 'asset' and occupant_info['name'] == 'Swetha':
            print("   ✓ PASS: IP correctly identified as occupied by Swetha")
        else:
            print("   ✗ FAIL: IP not correctly identified")
    
    except IPAddress.DoesNotExist:
        print("   ✗ FAIL: IP not found in database")
    
    # Test a few more manual IPs
    print("\n2. Testing other manual IPs:")
    test_ips = [
        '192.168.11.211',  # Keerthi s
        '192.168.11.157',  # Krishnaprasad_qc
        '192.168.11.174',  # Anu thomas_qc
    ]
    
    for test_ip in test_ips:
        try:
            ip = IPAddress.objects.get(address=test_ip)
            occupant_info = IPManagementService.get_ip_occupant_info(ip)
            
            if occupant_info['type'] == 'asset':
                print(f"   {test_ip}: ✓ Occupied by {occupant_info['name']}")
            else:
                print(f"   {test_ip}: ✗ Showing as {occupant_info['type']}")
        except IPAddress.DoesNotExist:
            print(f"   {test_ip}: Not in IPAddress table")
    
    # Test the full IP range method
    print("\n3. Testing get_all_ips_by_range_with_vms():")
    ip_ranges = IPManagementService.get_all_ips_by_range_with_vms()
    
    # Find 192.168.11.79 in the results
    found = False
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            if ip_data['ip'].address == '192.168.11.79':
                found = True
                ip_obj = ip_data['ip']
                print(f"   Found 192.168.11.79 in range {range_pattern}")
                print(f"   Has manual_assignment flag: {hasattr(ip_obj, 'manual_assignment')}")
                if hasattr(ip_obj, 'manual_assignment'):
                    print(f"   manual_assignment: {ip_obj.manual_assignment}")
                    if ip_obj.manual_assignment:
                        print(f"   manual_assigned_asset: {ip_obj.manual_assigned_asset.asset_tag}")
                        print(f"   ✓ PASS: IP has manual assignment flag set")
                    else:
                        print(f"   ✗ FAIL: manual_assignment flag is False")
                break
        if found:
            break
    
    if not found:
        print("   ✗ FAIL: IP 192.168.11.79 not found in results")
    
    # Count how many IPs have manual assignments
    print("\n4. Counting IPs with manual assignments:")
    manual_count = 0
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            ip_obj = ip_data['ip']
            if hasattr(ip_obj, 'manual_assignment') and ip_obj.manual_assignment:
                manual_count += 1
    
    print(f"   Found {manual_count} IPs with manual assignments")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)

if __name__ == '__main__':
    test_ip_fix()
