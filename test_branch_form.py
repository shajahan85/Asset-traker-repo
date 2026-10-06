#!/usr/bin/env python
"""Quick test to verify branch form template renders correctly."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'asset_tracker.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

# Create test admin user
User.objects.filter(username='testadmin').delete()
admin = User.objects.create_superuser('testadmin', 'admin@test.com', 'testpass123')

# Test branch create form
client = Client()
client.login(username='testadmin', password='testpass123')
response = client.get('/assets/branches/create/')

print(f'Status Code: {response.status_code}')
print(f'Content Type: {response.get("Content-Type", "N/A")}')

if response.status_code == 200:
    content = response.content.decode('utf-8')
    
    # Check for essential elements
    checks = {
        'CSRF Token': 'csrfmiddlewaretoken' in content,
        'Name Field': 'id_name' in content,
        'Code Field': 'id_code' in content,
        'Is Active Field': 'id_is_active' in content,
        'Submit Button': 'type="submit"' in content,
        'Cancel Button': 'href="/assets/branches/"' in content or 'branch_list' in content,
        'Form Title': 'Create' in content or 'Branch' in content,
    }
    
    print('\nTemplate Elements Check:')
    for check_name, result in checks.items():
        status = '✓' if result else '✗'
        print(f'  {status} {check_name}')
    
    all_passed = all(checks.values())
    print(f'\n{"SUCCESS: All checks passed!" if all_passed else "FAILURE: Some checks failed"}')
else:
    print(f'ERROR: Failed to render form (Status {response.status_code})')

# Cleanup
admin.delete()
