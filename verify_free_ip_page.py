#!/usr/bin/env python
"""Verify the Free IP page will display manual IPs correctly."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.services.ip_management_service import IPManagementService
from assets.models import IPAddress

def verify_free_ip_page():
    """Verify that the Free IP page data is correct."""
    
    print("=" * 70)
    print("Verifying Free IP Page Data")
    print("=" * 70)
    
    # Get the data that the Free IP page uses (simulating the view)
    ip_ranges = IPManagementService.get_all_ips_by_range_with_vms()
    
    # Enhance each IP with occupant info (simulating what the view does)
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            ip = ip_data['ip']
            occupant_info = IPManagementService.get_ip_occupant_info(ip)
            ip.occupant_type = occupant_info['type']
            ip.occupant_name = occupant_info['name']
    
    # Find problematic IPs (manual assignments)
    print("\n1. Checking for manual IP assignments in 192.168.11.x range:")
    
    if '192.168.11.x' in ip_ranges:
        ip_data_list = ip_ranges['192.168.11.x']
        manual_ips = []
        
        for ip_data in ip_data_list:
            ip = ip_data['ip']
            
            # Check if this IP has manual assignment
            if hasattr(ip, 'manual_assignment') and ip.manual_assignment:
                manual_ips.append({
                    'address': ip.address,
                    'asset_tag': ip.manual_assigned_asset.asset_tag,
                    'user': ip.manual_assigned_asset.assigned_to,
                    'occupant_type': ip.occupant_type,
                    'occupant_name': ip.occupant_name
                })
        
        print(f"   Found {len(manual_ips)} manual IP assignments")
        print("\n   Sample manual IPs (first 10):")
        for manual_ip in manual_ips[:10]:
            print(f"   - {manual_ip['address']}: {manual_ip['asset_tag']} ({manual_ip['user']})")
            print(f"     Occupant Type: {manual_ip['occupant_type']}")
            print(f"     Occupant Name: {manual_ip['occupant_name']}")
            
            # Verify it will show as red (occupied)
            if manual_ip['occupant_type'] == 'asset':
                print(f"     ✓ Will show as RED (occupied)")
            else:
                print(f"     ✗ Will show as GREEN (free) - PROBLEM!")
    
    # Specifically check 192.168.11.79 (Swetha)
    print("\n2. Specifically checking 192.168.11.79 (Swetha):")
    
    found = False
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            if ip_data['ip'].address == '192.168.11.79':
                found = True
                ip = ip_data['ip']
                
                print(f"   IP Address: {ip.address}")
                print(f"   Occupant Type: {ip.occupant_type}")
                print(f"   Occupant Name: {ip.occupant_name}")
                print(f"   Is Assigned (DB): {ip.is_assigned}")
                
                if hasattr(ip, 'manual_assignment'):
                    print(f"   Manual Assignment: {ip.manual_assignment}")
                    if ip.manual_assignment:
                        print(f"   Manual Asset: {ip.manual_assigned_asset.asset_tag}")
                
                # Determine color
                if ip.occupant_type == 'vm':
                    color = "BLUE (VM)"
                elif ip.occupant_type == 'free':
                    color = "GREEN (Free)"
                else:
                    color = "RED (Occupied)"
                
                print(f"\n   Will display as: {color}")
                
                if color == "RED (Occupied)":
                    print(f"   ✓ CORRECT: IP will show as occupied by {ip.occupant_name}")
                else:
                    print(f"   ✗ PROBLEM: IP should show as occupied but will show as {color}")
                
                break
        if found:
            break
    
    if not found:
        print("   ✗ IP 192.168.11.79 not found in results!")
    
    # Count total IPs by type
    print("\n3. Summary of all IPs by type:")
    
    type_counts = {'free': 0, 'asset': 0, 'vm': 0, 'network_device': 0}
    manual_count = 0
    
    for range_pattern, ip_data_list in ip_ranges.items():
        for ip_data in ip_data_list:
            ip = ip_data['ip']
            type_counts[ip.occupant_type] = type_counts.get(ip.occupant_type, 0) + 1
            
            if hasattr(ip, 'manual_assignment') and ip.manual_assignment:
                manual_count += 1
    
    print(f"   Free IPs: {type_counts['free']}")
    print(f"   Occupied by Assets: {type_counts['asset']}")
    print(f"   Occupied by VMs: {type_counts['vm']}")
    print(f"   Occupied by Network Devices: {type_counts['network_device']}")
    print(f"   Manual Assignments: {manual_count}")
    
    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)
    print("\nThe Free IP page should now correctly show:")
    print("  - Manual IPs as RED (occupied) with user names")
    print("  - Managed IPs as RED (occupied) with user names")
    print("  - VMs as BLUE with VM names")
    print("  - Free IPs as GREEN")

if __name__ == '__main__':
    verify_free_ip_page()
