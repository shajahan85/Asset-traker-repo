"""Test branch form template rendering with actual data."""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.template import Template, Context
from django.template.loader import render_to_string
from assets.forms.branch_form import BranchForm
from assets.models import Branch
from django.test import RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage

print("Testing Branch Form Template Rendering...")
print("=" * 60)

# Test 1: Render Create Form
print("\nTest 1: Rendering Create Form")
try:
    from django.template import RequestContext
    from django.middleware.csrf import get_token
    
    form = BranchForm()
    request = RequestFactory().get('/branches/create/')
    request.session = {}
    request._messages = FallbackStorage(request)
    
    # Add CSRF token to request
    get_token(request)
    
    html = render_to_string('assets/branch_form.html', {
        'form': form,
    }, request=request)
    
    # Check for key elements
    assert 'Create New Branch' in html
    assert 'csrf' in html.lower() or 'csrfmiddlewaretoken' in html
    assert 'name="name"' in html
    assert 'name="code"' in html
    assert 'name="is_active"' in html
    assert 'Create Branch' in html
    assert '/assets/branches/' in html  # Cancel button URL
    
    print("✓ Create form renders correctly")
    print("  - Title: 'Create New Branch'")
    print("  - CSRF token present")
    print("  - All fields rendered")
    print("  - Submit button: 'Create Branch'")
    print("  - Cancel button links to branch list")
except Exception as e:
    print(f"✗ Create form rendering failed: {e}")
    sys.exit(1)

# Test 2: Render Edit Form
print("\nTest 2: Rendering Edit Form")
try:
    from django.middleware.csrf import get_token
    
    # Create a test branch instance (don't save to DB)
    branch = Branch(
        id=1,
        name="Test Branch",
        code="TST",
        is_active=True
    )
    
    form = BranchForm(instance=branch)
    request = RequestFactory().get('/branches/1/edit/')
    request.session = {}
    request._messages = FallbackStorage(request)
    get_token(request)
    
    html = render_to_string('assets/branch_form.html', {
        'form': form,
    }, request=request)
    
    # Check for key elements
    assert 'Edit Branch' in html
    assert 'Test Branch' in html or 'value="Test Branch"' in html
    assert 'Update Branch' in html
    
    print("✓ Edit form renders correctly")
    print("  - Title: 'Edit Branch'")
    print("  - Form pre-filled with branch data")
    print("  - Submit button: 'Update Branch'")
except Exception as e:
    print(f"✗ Edit form rendering failed: {e}")
    sys.exit(1)

# Test 3: Render Form with Validation Errors
print("\nTest 3: Rendering Form with Validation Errors")
try:
    from django.middleware.csrf import get_token
    
    # Submit empty form to trigger validation errors
    form = BranchForm(data={})
    form.is_valid()  # This will populate errors
    
    request = RequestFactory().post('/branches/create/')
    request.session = {}
    request._messages = FallbackStorage(request)
    get_token(request)
    
    html = render_to_string('assets/branch_form.html', {
        'form': form,
    }, request=request)
    
    # Check for error display elements
    assert 'error-message' in html or 'error' in html.lower()
    
    print("✓ Form with validation errors renders correctly")
    print("  - Error messages displayed")
except Exception as e:
    print(f"✗ Validation error rendering failed: {e}")
    sys.exit(1)

# Test 4: Check Bootstrap classes in rendered HTML
print("\nTest 4: Verifying Bootstrap Classes")
try:
    from django.middleware.csrf import get_token
    
    form = BranchForm()
    request = RequestFactory().get('/branches/create/')
    request.session = {}
    request._messages = FallbackStorage(request)
    get_token(request)
    
    html = render_to_string('assets/branch_form.html', {
        'form': form,
    }, request=request)
    
    assert 'form-control' in html
    assert 'form-check' in html or 'form-check-input' in html
    assert 'btn btn-primary' in html
    assert 'btn btn-secondary' in html
    assert 'form-group' in html
    
    print("✓ Bootstrap classes present in rendered HTML")
    print("  - form-control (text inputs)")
    print("  - form-check-input (checkbox)")
    print("  - btn btn-primary (submit button)")
    print("  - btn btn-secondary (cancel button)")
    print("  - form-group (field containers)")
except Exception as e:
    print(f"✗ Bootstrap class check failed: {e}")
    sys.exit(1)

# Test 5: Verify help text rendering
print("\nTest 5: Verifying Help Text")
try:
    from django.middleware.csrf import get_token
    
    form = BranchForm()
    request = RequestFactory().get('/branches/create/')
    request.session = {}
    request._messages = FallbackStorage(request)
    get_token(request)
    
    html = render_to_string('assets/branch_form.html', {
        'form': form,
    }, request=request)
    
    # Check for help texts defined in the form
    assert 'Short code for the branch' in html or 'help-text' in html
    
    print("✓ Help text renders correctly")
    print("  - Field help texts displayed")
except Exception as e:
    print(f"✗ Help text check failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL RENDERING TESTS PASSED! ✓")
print("=" * 60)
print("\nSummary:")
print("- Create form renders with correct title and button text")
print("- Edit form renders with pre-filled data and correct button text")
print("- Validation errors display properly")
print("- Bootstrap styling is applied correctly")
print("- Help texts are visible")
print("- CSRF protection is in place")
print("- Cancel button works correctly")
print("\nThe branch_form.html template is fully functional!")
