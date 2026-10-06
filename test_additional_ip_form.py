#!/usr/bin/env python
"""
Quick validation test for AdditionalIPForm.
This bypasses the test infrastructure issues and directly tests the new form.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.forms.asset_forms import AdditionalIPForm
from assets.models import Asset, AssetIPAddress, OperatingSystem, Team, Branch, IPAddress, IPRange

def test_additional_ip_form():
    """Test that AdditionalIPForm works correctly."""
    print("=" * 60)
    print("Testing AdditionalIPForm")
    print("=" * 60)
    
    # Create necessary dependencies
    try:
        branch = Branch.objects.first()
        if not branch:
            branch = Branch.objects.create(name="Test Branch", code="TST")
        print(f"✓ Using branch: {branch.name}")
        
        team = Team.objects.filter(branch=branch).first()
        if not team:
            team = Team.objects.create(name="Test Team", branch=branch)
        print(f"✓ Using team: {team.name}")
        
        os_obj = OperatingSystem.objects.first()
        if not os_obj:
            os_obj = OperatingSystem.objects.create(name="Test OS")
        print(f"✓ Using OS: {os_obj.name}")
        
        # Create a test asset
        asset = Asset.objects.create(
            asset_tag="TEST_FORM_001",
            system_type="Desktop",
            operating_system=os_obj,
            team=team,
            branch=branch
        )
        print(f"✓ Created test asset: {asset.asset_tag}")
        
    except Exception as e:
        print(f"✗ Error setting up test data: {e}")
        return False
    
    # Test 1: Form with valid manual IP data
    print("\n--- Test 1: Form with valid manual IP ---")
    form_data = {
        'ip_type': 'manual',
        'ip_label': 'WiFi',
        'manual_ip': '192.168.1.200'
    }
    form = AdditionalIPForm(data=form_data)
    if form.is_valid():
        print("✓ PASSED: Form with valid manual IP is valid")
        instance = form.save(commit=False)
        instance.asset = asset
        instance.save()
        print(f"  Created: {instance} with label '{instance.ip_label}'")
    else:
        print(f"✗ FAILED: Form should be valid. Errors: {form.errors}")
        return False
    
    # Test 2: Form requires label
    print("\n--- Test 2: Form requires label ---")
    form_data = {
        'ip_type': 'manual',
        'ip_label': '',  # Empty label should fail
        'manual_ip': '192.168.1.201'
    }
    form = AdditionalIPForm(data=form_data)
    if not form.is_valid() and 'ip_label' in form.errors:
        print("✓ PASSED: Form correctly requires label")
    else:
        print(f"✗ FAILED: Form should require label. Valid: {form.is_valid()}, Errors: {form.errors}")
        return False
    
    # Test 3: Form requires IP based on ip_type
    print("\n--- Test 3: Form requires IP selection ---")
    form_data = {
        'ip_type': 'manual',
        'ip_label': 'Mobile',
        'manual_ip': ''  # Empty IP should fail when manual type selected
    }
    form = AdditionalIPForm(data=form_data)
    if not form.is_valid() and 'manual_ip' in form.errors:
        print("✓ PASSED: Form correctly requires IP when manual type selected")
    else:
        print(f"✗ FAILED: Form should require manual IP. Valid: {form.is_valid()}, Errors: {form.errors}")
        return False
    
    # Test 4: Form clears unused field based on ip_type
    print("\n--- Test 4: Form clears unused IP field ---")
    form_data = {
        'ip_type': 'manual',
        'ip_label': 'VPN',
        'manual_ip': '192.168.1.202',
        'ip_address': ''  # This should be cleared since ip_type is manual
    }
    form = AdditionalIPForm(data=form_data)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        if cleaned_data['manual_ip'] == '192.168.1.202' and cleaned_data['ip_address'] is None:
            print("✓ PASSED: Form correctly clears unused ip_address field")
        else:
            print(f"✗ FAILED: Form should clear ip_address. Cleaned data: {cleaned_data}")
            return False
    else:
        print(f"✗ FAILED: Form should be valid. Errors: {form.errors}")
        return False
    
    # Test 5: Form sets is_primary to False on save
    print("\n--- Test 5: Form sets is_primary=False ---")
    form_data = {
        'ip_type': 'manual',
        'ip_label': 'Backup',
        'manual_ip': '192.168.1.203'
    }
    form = AdditionalIPForm(data=form_data)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.asset = asset
        instance.save()
        if instance.is_primary == False:
            print("✓ PASSED: Form correctly sets is_primary=False")
            print(f"  Created: {instance} with is_primary={instance.is_primary}")
        else:
            print(f"✗ FAILED: is_primary should be False but got {instance.is_primary}")
            return False
    else:
        print(f"✗ FAILED: Form should be valid. Errors: {form.errors}")
        return False
    
    # Test 6: Verify form has expected fields
    print("\n--- Test 6: Form has expected fields ---")
    form = AdditionalIPForm()
    expected_fields = ['ip_type', 'ip_label', 'ip_address', 'manual_ip']
    missing_fields = [f for f in expected_fields if f not in form.fields]
    if not missing_fields:
        print(f"✓ PASSED: Form has all expected fields: {expected_fields}")
    else:
        print(f"✗ FAILED: Form is missing fields: {missing_fields}")
        return False
    
    # Cleanup
    print("\n--- Cleanup ---")
    try:
        asset.delete()
        print("✓ Cleaned up test asset")
    except Exception as e:
        print(f"⚠ Warning: Could not cleanup test asset: {e}")
    
    return True

if __name__ == "__main__":
    print("\n")
    success = test_additional_ip_form()
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
