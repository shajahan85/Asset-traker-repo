#!/usr/bin/env python
"""Test the filtered IP dropdown functionality."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import IPAddress
from django.db import models

def test_filtered_ips():
    """Test that the IP filtering works correctly."""
    
    print("=" * 70)
    print("Testing Filtered IP Dropdown")
    print("=" * 70)
    
    # Define the allowed IP ranges
    allowed_ranges = ['192.168.10.', '192.168.11.', '192.168.50.', '192.168.70.']
    
    # Build query to filter by ranges
    range_query = models.Q()
    for range_prefix in allowed_ranges:
        range_query |= models.Q(address__startswith=range_prefix)
    
    # Get free IPs in the specified ranges
    filtered_ips = IPAddress.objects.filter(
        is_assigned=False
    ).filter(range_query).order_by('address')
    
    print(f"\nTotal free IPs in system: {IPAddress.objects.filter(is_assigned=False).count()}")
    print(f"Free IPs in specified ranges: {filtered_ips.count()}")
    
    # Count by range
    print("\nBreakdown by range:")
    for range_prefix in allowed_ranges:
        count = filtered_ips.filter(address__startswith=range_prefix).count()
        print(f"  {range_prefix}x: {count} free IPs")
    
    # Show sample IPs from each range
    print("\nSample free IPs (first 5 from each range):")
    for range_prefix in allowed_ranges:
        range_ips = filtered_ips.filter(address__startswith=range_prefix)[:5]
        if range_ips:
            print(f"\n  {range_prefix}x:")
            for ip in range_ips:
                print(f"    - {ip.address}")
    
    # Test that IPs outside the ranges are excluded
    print("\n" + "=" * 70)
    print("Verification: IPs outside specified ranges")
    print("=" * 70)
    
    all_free_ips = IPAddress.objects.filter(is_assigned=False)
    excluded_ips = all_free_ips.exclude(range_query)
    
    print(f"\nFree IPs excluded from dropdown: {excluded_ips.count()}")
    if excluded_ips.count() > 0:
        print("Sample excluded IPs (first 10):")
        for ip in excluded_ips[:10]:
            print(f"  - {ip.address}")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)
    print("\nThe IP dropdown will now show only free IPs from:")
    print("  - 192.168.10.x")
    print("  - 192.168.11.x")
    print("  - 192.168.50.x")
    print("  - 192.168.70.x")
    print(f"\nTotal: {filtered_ips.count()} free IPs available for selection")

if __name__ == '__main__':
    test_filtered_ips()
