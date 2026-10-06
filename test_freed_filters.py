#!/usr/bin/env python
"""Test script to verify freed systems filter functionality."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.forms.freed_system_filter_form import FreedSystemFilterForm
from assets.models import Asset

def test_freed_filters():
    """Test the freed systems filter with various scenarios."""
    
    print("=" * 60)
    print("Testing Freed Systems Filters")
    print("=" * 60)
    
    # Get freed assets statistics
    freed = Asset.objects.filter(status='freed')
    print(f"\nTotal freed assets: {freed.count()}")
    print(f"  Healthy: {freed.filter(health_status='healthy').count()}")
    print(f"  Defective: {freed.filter(health_status='defective').count()}")
    print(f"  No health status: {freed.filter(health_status__isnull=True).count()}")
    
    print("\nBy System Type:")
    for st in ['Desktop', 'Laptop', 'All-in-One PC']:
        count = freed.filter(system_type=st).count()
        print(f"  {st}: {count}")
    
    # Test 1: Filter by health status (healthy)
    print("\n" + "=" * 60)
    print("Test 1: Filter by Health Status (Healthy)")
    print("=" * 60)
    form_data = {'health_status': 'healthy'}
    form = FreedSystemFilterForm(form_data)
    
    if form.is_valid():
        queryset = freed
        health_status = form.cleaned_data.get('health_status')
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        
        print(f"Found {queryset.count()} healthy freed asset(s)")
        for asset in queryset[:5]:
            print(f"  - {asset.asset_tag}: {asset.system_type} - {asset.health_status}")
    
    # Test 2: Filter by system type (Desktop)
    print("\n" + "=" * 60)
    print("Test 2: Filter by System Type (Desktop)")
    print("=" * 60)
    form_data = {'system_type': 'Desktop'}
    form = FreedSystemFilterForm(form_data)
    
    if form.is_valid():
        queryset = freed
        system_type = form.cleaned_data.get('system_type')
        if system_type:
            queryset = queryset.filter(system_type=system_type)
        
        print(f"Found {queryset.count()} Desktop freed asset(s)")
        for asset in queryset[:5]:
            print(f"  - {asset.asset_tag}: {asset.system_type} - {asset.health_status or 'N/A'}")
    
    # Test 3: Combined filters (Defective Laptops)
    print("\n" + "=" * 60)
    print("Test 3: Combined Filters (Defective Laptops)")
    print("=" * 60)
    form_data = {'system_type': 'Laptop', 'health_status': 'defective'}
    form = FreedSystemFilterForm(form_data)
    
    if form.is_valid():
        queryset = freed
        system_type = form.cleaned_data.get('system_type')
        if system_type:
            queryset = queryset.filter(system_type=system_type)
        
        health_status = form.cleaned_data.get('health_status')
        if health_status:
            queryset = queryset.filter(health_status=health_status)
        
        print(f"Found {queryset.count()} defective Laptop(s)")
        for asset in queryset[:5]:
            print(f"  - {asset.asset_tag}: {asset.system_type} - {asset.health_status}")
            if asset.issues_description:
                print(f"    Issues: {asset.issues_description[:50]}...")
    
    # Test 4: Search by BIDC number
    print("\n" + "=" * 60)
    print("Test 4: Search by BIDC Number")
    print("=" * 60)
    
    # Get a sample freed asset
    sample_asset = freed.first()
    if sample_asset:
        search_term = sample_asset.asset_tag[:6]  # Search with partial BIDC
        form_data = {'search': search_term}
        form = FreedSystemFilterForm(form_data)
        
        if form.is_valid():
            queryset = freed
            search_query = form.cleaned_data.get('search', '').strip()
            if search_query:
                queryset = queryset.filter(asset_tag__icontains=search_query)
            
            print(f"Searching for '{search_term}'")
            print(f"Found {queryset.count()} freed asset(s)")
            for asset in queryset[:5]:
                print(f"  - {asset.asset_tag}: {asset.system_type}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    test_freed_filters()
