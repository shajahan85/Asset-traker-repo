#!/usr/bin/env python
"""
Quick validation test for ip_label functionality in AssetIPAddress model.
This bypasses the test infrastructure issues and directly tests the new feature.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.core.exceptions import ValidationError
from assets.models import Asset, AssetIPAddress, OperatingSystem, Team, Branch

def test_ip_label_validation():
    """Test that ip_label validation works correctly."""
    print("=" * 60)
    print("Testing IP Label Validation for AssetIPAddress Model")
    print("=" * 60)
    
    # Create necessary dependencies
    try:
        branch = Branch.objects.first()
        if not branch:
            print("✗ No branch found. Creating test branch...")
            branch = Branch.objects.create(name="Test Branch", code="TST")
            print(f"✓ Created branch: {branch.name}")
        else:
            print(f"✓ Using existing branch: {branch.name}")
        
        team = Team.objects.filter(branch=branch).first()
        if not team:
            print("✗ No team found for branch. Creating test team...")
            team = Team.objects.create(name="Test Team", branch=branch)
            print(f"✓ Created team: {team.name}")
        else:
            print(f"✓ Using existing team: {team.name}")
        
        os_obj = OperatingSystem.objects.first()
        if not os_obj:
            print("✗ No OS found. Creating test OS...")
            os_obj = OperatingSystem.objects.create(name="Test OS")
            print(f"✓ Created OS: {os_obj.name}")
        else:
            print(f"✓ Using existing OS: {os_obj.name}")
        
        # Create a test asset
        asset = Asset.objects.create(
            asset_tag="TEST_IP_LABEL_001",
            system_type="Desktop",
            operating_system=os_obj,
            team=team,
            branch=branch
        )
        print(f"✓ Created test asset: {asset.asset_tag}")
        
    except Exception as e:
        print(f"✗ Error setting up test data: {e}")
        return False
    
    # Test 1: Primary IP should not have label
    print("\n--- Test 1: Primary IP cannot have label ---")
    try:
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.100',
            is_primary=True,
            ip_label='WiFi'  # This should fail
        )
        ip_assoc.full_clean()
        print("✗ FAILED: Primary IP with label should be rejected")
        return False
    except ValidationError as e:
        if 'ip_label' in str(e):
            print("✓ PASSED: Primary IP with label correctly rejected")
        else:
            print(f"✗ FAILED: Wrong validation error: {e}")
            return False
    
    # Test 2: Additional IP (non-primary) requires label
    print("\n--- Test 2: Additional IP requires label ---")
    try:
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.101',
            is_primary=False,
            ip_label=None  # This should fail
        )
        ip_assoc.full_clean()
        print("✗ FAILED: Additional IP without label should be rejected")
        return False
    except ValidationError as e:
        if 'ip_label' in str(e):
            print("✓ PASSED: Additional IP without label correctly rejected")
        else:
            print(f"✗ FAILED: Wrong validation error: {e}")
            return False
    
    # Test 3: Additional IP with whitespace-only label should be rejected
    print("\n--- Test 3: Whitespace-only label rejected ---")
    try:
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.102',
            is_primary=False,
            ip_label='   '  # This should fail
        )
        ip_assoc.full_clean()
        print("✗ FAILED: Whitespace-only label should be rejected")
        return False
    except ValidationError as e:
        if 'ip_label' in str(e):
            print("✓ PASSED: Whitespace-only label correctly rejected")
        else:
            print(f"✗ FAILED: Wrong validation error: {e}")
            return False
    
    # Test 4: Primary IP with null label should be accepted
    print("\n--- Test 4: Primary IP with null label accepted ---")
    try:
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.103',
            is_primary=True,
            ip_label=None  # This should pass
        )
        ip_assoc.full_clean()
        ip_assoc.save()
        print("✓ PASSED: Primary IP with null label correctly accepted")
        print(f"  Created: {ip_assoc}")
    except ValidationError as e:
        print(f"✗ FAILED: Primary IP with null label should be accepted. Error: {e}")
        return False
    
    # Test 5: Additional IP with valid label should be accepted
    print("\n--- Test 5: Additional IP with valid label accepted ---")
    try:
        ip_assoc = AssetIPAddress(
            asset=asset,
            manual_ip='192.168.1.104',
            is_primary=False,
            ip_label='WiFi'  # This should pass
        )
        ip_assoc.full_clean()
        ip_assoc.save()
        print("✓ PASSED: Additional IP with valid label correctly accepted")
        print(f"  Created: {ip_assoc} with label '{ip_assoc.ip_label}'")
    except ValidationError as e:
        print(f"✗ FAILED: Additional IP with valid label should be accepted. Error: {e}")
        return False
    
    # Test 6: Verify ip_label field exists and is accessible
    print("\n--- Test 6: IP label field accessible ---")
    try:
        saved_ip = AssetIPAddress.objects.filter(asset=asset, is_primary=False).first()
        if saved_ip and saved_ip.ip_label == 'WiFi':
            print(f"✓ PASSED: IP label field is accessible and has correct value: '{saved_ip.ip_label}'")
        else:
            print(f"✗ FAILED: Could not retrieve or verify ip_label value")
            return False
    except Exception as e:
        print(f"✗ FAILED: Error accessing ip_label field: {e}")
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
    success = test_ip_label_validation()
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        sys.exit(1)
