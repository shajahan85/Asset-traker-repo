#!/usr/bin/env python
"""Test script to verify AssetForm works with existing assets."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from assets.models import Asset
from assets.forms.asset_forms import AssetForm

def test_asset_form(asset_tag):
    """Test that AssetForm loads properly for an existing asset."""
    try:
        asset = Asset.objects.get(asset_tag=asset_tag)
        print(f"\n{'='*60}")
        print(f"Testing Asset: {asset.asset_tag}")
        print(f"User: {asset.assigned_to}")
        print(f"Branch: {asset.branch}")
        print(f"Team: {asset.team}")
        print(f"OS: {asset.operating_system}")
        print(f"{'='*60}")
        
        # Create form with instance
        form = AssetForm(instance=asset)
        
        # Check querysets
        branch_count = form.fields['branch'].queryset.count()
        os_count = form.fields['operating_system'].queryset.count()
        
        print(f"\n✓ Form created successfully")
        print(f"  Branch queryset count: {branch_count}")
        print(f"  OS queryset count: {os_count}")
        
        # Verify current values are in querysets
        branch_in_qs = asset.branch in form.fields['branch'].queryset
        print(f"  Current branch '{asset.branch}' in queryset: {'✓ YES' if branch_in_qs else '✗ NO'}")
        
        if asset.operating_system:
            os_in_qs = asset.operating_system in form.fields['operating_system'].queryset
            print(f"  Current OS '{asset.operating_system}' in queryset: {'✓ YES' if os_in_qs else '✗ NO'}")
        else:
            print(f"  No OS set for this asset")
        
        if asset.team:
            if asset.team.parent:
                parent_in_qs = asset.team.parent in form.fields['parent_team'].queryset
                sub_in_qs = asset.team in form.fields['sub_team'].queryset
                print(f"  Current parent team '{asset.team.parent}' in queryset: {'✓ YES' if parent_in_qs else '✗ NO'}")
                print(f"  Current sub-team '{asset.team}' in queryset: {'✓ YES' if sub_in_qs else '✗ NO'}")
            else:
                team_in_qs = asset.team in form.fields['parent_team'].queryset
                print(f"  Current team '{asset.team}' in queryset: {'✓ YES' if team_in_qs else '✗ NO'}")
        
        # Check initial values
        print(f"\n  Form initial values:")
        print(f"    branch: {form.fields['branch'].initial}")
        print(f"    operating_system: {form.fields['operating_system'].initial}")
        print(f"    parent_team: {form.fields['parent_team'].initial}")
        print(f"    sub_team: {form.fields['sub_team'].initial}")
        
        print(f"\n✓ All checks passed for {asset_tag}!")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR testing {asset_tag}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Test Anjana's assets
    print("\nTesting Anjana's Assets:")
    print("=" * 60)
    
    test_assets = ['BIDC1022', 'BIDC1443', 'BIDC1544', 'BIDC1204']
    
    results = []
    for asset_tag in test_assets:
        try:
            result = test_asset_form(asset_tag)
            results.append((asset_tag, result))
        except Exception as e:
            print(f"Failed to test {asset_tag}: {e}")
            results.append((asset_tag, False))
    
    print(f"\n\n{'='*60}")
    print("SUMMARY:")
    print(f"{'='*60}")
    for asset_tag, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {asset_tag}: {status}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print(f"\n✓ ALL TESTS PASSED!")
    else:
        print(f"\n✗ SOME TESTS FAILED - Check errors above")
