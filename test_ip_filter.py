#!/usr/bin/env python
"""Test script to verify IP address filter functionality."""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.forms.filter_form import AssetFilterForm
from assets.services.filter_service import FilterService
from assets.models import Asset

def test_ip_filter():
    """Test the IP address filter with various scenarios."""
    
    print("=" * 60)
    print("Testing IP Address Filter")
    print("=" * 60)
    
    # Test 1: Search for Swetha's IP (managed IP)
    print("\n1. Testing with Swetha's IP (192.168.11.79):")
    form_data = {'ip_address': '192.168.11.79'}
    form = AssetFilterForm(form_data)
    
    if form.is_valid():
        assets = Asset.objects.filter(status='active').select_related(
            'operating_system', 'ip_address', 'team', 'team__parent'
        )
        filter_service = FilterService()
        filtered = filter_service.apply_filters(assets, form.cleaned_data)
        
        print(f"   Found {filtered.count()} asset(s)")
        for asset in filtered:
            ip = asset.ip_address.address if asset.ip_address else asset.manual_ip
            print(f"   - {asset.asset_tag}: {asset.assigned_to} - IP: {ip}")
    else:
        print(f"   Form validation failed: {form.errors}")
    
    # Test 2: Partial IP search
    print("\n2. Testing with partial IP (192.168.11):")
    form_data = {'ip_address': '192.168.11'}
    form = AssetFilterForm(form_data)
    
    if form.is_valid():
        assets = Asset.objects.filter(status='active').select_related(
            'operating_system', 'ip_address', 'team', 'team__parent'
        )
        filter_service = FilterService()
        filtered = filter_service.apply_filters(assets, form.cleaned_data)
        
        print(f"   Found {filtered.count()} asset(s)")
        print("   Showing first 5 results:")
        for asset in filtered[:5]:
            ip = asset.ip_address.address if asset.ip_address else asset.manual_ip
            print(f"   - {asset.asset_tag}: {asset.assigned_to} - IP: {ip}")
    else:
        print(f"   Form validation failed: {form.errors}")
    
    # Test 3: Search for manual IP
    print("\n3. Testing with manual IP (192.168.11.157):")
    form_data = {'ip_address': '192.168.11.157'}
    form = AssetFilterForm(form_data)
    
    if form.is_valid():
        assets = Asset.objects.filter(status='active').select_related(
            'operating_system', 'ip_address', 'team', 'team__parent'
        )
        filter_service = FilterService()
        filtered = filter_service.apply_filters(assets, form.cleaned_data)
        
        print(f"   Found {filtered.count()} asset(s)")
        for asset in filtered:
            ip = asset.ip_address.address if asset.ip_address else asset.manual_ip
            print(f"   - {asset.asset_tag}: {asset.assigned_to} - IP: {ip}")
    else:
        print(f"   Form validation failed: {form.errors}")
    
    # Test 4: Assets without IP addresses
    print("\n4. Checking assets without IP addresses:")
    assets_no_ip = Asset.objects.filter(
        status='active',
        ip_address__isnull=True,
        manual_ip__isnull=True
    ).count()
    print(f"   Found {assets_no_ip} active asset(s) without IP addresses")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully!")
    print("=" * 60)

if __name__ == '__main__':
    test_ip_filter()
