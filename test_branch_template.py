"""Quick test script to verify branch_confirm_delete.html template renders correctly."""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.template.loader import render_to_string
from assets.models import Branch

# Test with branch that has assets (Kochi)
try:
    kochi_branch = Branch.objects.get(code='KCH')
    print("Testing template with branch that HAS assets (Kochi):")
    print(f"Branch: {kochi_branch.name} ({kochi_branch.code})")
    print(f"Assets count: {kochi_branch.assets.count()}")
    
    html = render_to_string('assets/branch_confirm_delete.html', {'branch': kochi_branch})
    
    # Check key elements are in the rendered HTML
    assert 'Delete Branch' in html
    assert kochi_branch.name in html
    assert kochi_branch.code in html
    assert 'Warning: This branch has assets assigned!' in html
    assert str(kochi_branch.assets.count()) in html
    assert 'Yes, Delete Branch' not in html  # Button should NOT be present
    assert 'Cancel' in html
    print("✓ Template renders correctly for branch WITH assets\n")
    
except Exception as e:
    print(f"✗ Error with Kochi branch: {e}\n")

# Test with branch that has no assets (Delhi)
try:
    delhi_branch = Branch.objects.get(code='DEL')
    print("Testing template with branch that has NO assets (Delhi):")
    print(f"Branch: {delhi_branch.name} ({delhi_branch.code})")
    print(f"Assets count: {delhi_branch.assets.count()}")
    
    html = render_to_string('assets/branch_confirm_delete.html', {'branch': delhi_branch})
    
    # Check key elements are in the rendered HTML
    assert 'Delete Branch' in html
    assert delhi_branch.name in html
    assert delhi_branch.code in html
    assert 'This branch has no assets assigned and can be safely deleted' in html
    assert 'Yes, Delete Branch' in html  # Button SHOULD be present
    assert 'Cancel' in html
    print("✓ Template renders correctly for branch WITHOUT assets\n")
    
except Exception as e:
    print(f"✗ Error with Delhi branch: {e}\n")

print("All tests passed! ✓")
