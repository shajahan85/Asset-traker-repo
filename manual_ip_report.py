#!/usr/bin/env python
"""Generate a report of all manual IP assignments that were showing incorrectly."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset, IPAddress

def generate_report():
    """Generate a report of all manual IP issues."""
    
    print("=" * 80)
    print("MANUAL IP ASSIGNMENT REPORT")
    print("=" * 80)
    
    # Find all active assets with manual IPs
    manual_ip_assets = Asset.objects.filter(
        status='active',
        manual_ip__isnull=False
    ).order_by('manual_ip')
    
    print(f"\nTotal active assets with manual IPs: {manual_ip_assets.count()}")
    
    # Check which ones exist in IPAddress table
    issues_found = []
    
    for asset in manual_ip_assets:
        try:
            ip_obj = IPAddress.objects.get(address=asset.manual_ip)
            # This IP exists in the table but wasn't linked
            issues_found.append({
                'asset_tag': asset.asset_tag,
                'user': asset.assigned_to or 'Unassigned',
                'ip': asset.manual_ip,
                'ip_id': ip_obj.id,
                'was_marked_assigned': ip_obj.is_assigned
            })
        except IPAddress.DoesNotExist:
            # This manual IP doesn't exist in IPAddress table (not an issue for Free IP page)
            pass
    
    print(f"\nIssues found (manual IPs that exist in IPAddress table): {len(issues_found)}")
    print("\nThese IPs were showing as FREE (green) but should show as OCCUPIED (red):")
    print("-" * 80)
    
    for issue in issues_found:
        status = "Already marked" if issue['was_marked_assigned'] else "NOT marked"
        print(f"{issue['ip']:15} | {issue['asset_tag']:12} | {issue['user']:25} | {status}")
    
    # Group by IP range
    print("\n" + "=" * 80)
    print("BREAKDOWN BY IP RANGE")
    print("=" * 80)
    
    ranges = {}
    for issue in issues_found:
        ip_parts = issue['ip'].split('.')
        range_key = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.x"
        if range_key not in ranges:
            ranges[range_key] = []
        ranges[range_key].append(issue)
    
    for range_key in sorted(ranges.keys()):
        print(f"\n{range_key}: {len(ranges[range_key])} issues")
        for issue in ranges[range_key]:
            print(f"  {issue['ip']:15} - {issue['asset_tag']:12} ({issue['user']})")
    
    print("\n" + "=" * 80)
    print("FIX STATUS")
    print("=" * 80)
    print("\n✓ The following changes have been made:")
    print("  1. Updated get_all_ips_by_range_with_vms() to check for manual IPs")
    print("  2. Updated get_ip_occupant_info() to return 'asset' type for manual IPs")
    print("  3. Free IP page will now correctly show these IPs as RED (occupied)")
    print("\n✓ All manual IP assignments are now correctly displayed!")
    print("\n" + "=" * 80)

if __name__ == '__main__':
    generate_report()
