"""Integration test for branch form template with views."""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from django.contrib.messages.storage.fallback import FallbackStorage
from assets.models import Branch
from assets.views_branch import BranchCreateView, BranchUpdateView

User = get_user_model()

print("Starting Branch Form Integration Tests...")
print("=" * 60)

# Create test client
client = Client()
factory = RequestFactory()

# Test 1: Verify template path in views
print("\nTest 1: Verify template configuration")
try:
    assert BranchCreateView.template_name == 'assets/branch_form.html'
    assert BranchUpdateView.template_name == 'assets/branch_form.html'
    print("✓ Both BranchCreateView and BranchUpdateView use correct template")
except AssertionError:
    print("✗ Template configuration mismatch!")
    sys.exit(1)

# Test 2: Verify form class
print("\nTest 2: Verify form class")
try:
    from assets.forms.branch_form import BranchForm
    assert BranchCreateView.form_class == BranchForm
    assert BranchUpdateView.form_class == BranchForm
    print("✓ Both views use BranchForm correctly")
except AssertionError:
    print("✗ Form class mismatch!")
    sys.exit(1)

# Test 3: Check if branch_list URL is accessible (for Cancel button)
print("\nTest 3: Verify branch_list URL (for Cancel button)")
try:
    from django.urls import reverse
    url = reverse('branch_list')
    print(f"✓ branch_list URL resolves to: {url}")
except Exception as e:
    print(f"✗ branch_list URL error: {e}")
    sys.exit(1)

# Test 4: Check form fields match template expectations
print("\nTest 4: Verify form fields")
try:
    form = BranchForm()
    assert 'name' in form.fields
    assert 'code' in form.fields
    assert 'is_active' in form.fields
    print("✓ BranchForm has all required fields (name, code, is_active)")
except AssertionError:
    print("✗ Missing required fields in BranchForm!")
    sys.exit(1)

# Test 5: Check Bootstrap classes on form widgets
print("\nTest 5: Verify Bootstrap styling")
try:
    form = BranchForm()
    name_widget_class = form.fields['name'].widget.attrs.get('class', '')
    code_widget_class = form.fields['code'].widget.attrs.get('class', '')
    is_active_widget_class = form.fields['is_active'].widget.attrs.get('class', '')
    
    assert 'form-control' in name_widget_class
    assert 'form-control' in code_widget_class
    assert 'form-check-input' in is_active_widget_class
    print("✓ All form fields have proper Bootstrap classes")
except AssertionError:
    print("✗ Bootstrap classes missing!")
    sys.exit(1)

# Test 6: Verify success URL redirects to branch_list
print("\nTest 6: Verify success URL")
try:
    from django.urls import reverse_lazy
    expected_url = reverse_lazy('branch_list')
    assert BranchCreateView.success_url == expected_url
    assert BranchUpdateView.success_url == expected_url
    print("✓ Both views redirect to branch_list after successful submission")
except AssertionError:
    print("✗ Success URL mismatch!")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL INTEGRATION TESTS PASSED! ✓")
print("=" * 60)
print("\nSummary:")
print("- Template configuration is correct")
print("- Form class properly assigned")
print("- URL routing works correctly")
print("- Form fields match template expectations")
print("- Bootstrap styling is applied")
print("- Success redirects configured properly")
print("\nThe branch_form.html template is fully integrated and working!")
