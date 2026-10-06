"""Tests for branch management templates."""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from assets.models import Branch

User = get_user_model()


class BranchFormTemplateTest(TestCase):
    """Test branch form template rendering and functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        # Create admin user for testing
        self.admin_user = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True,
            is_superuser=True
        )
        # Create test branch
        self.branch = Branch.objects.create(
            name='Test Branch',
            code='TST',
            is_active=True
        )
    
    def test_branch_create_template_loads(self):
        """Test that branch create form template loads correctly."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('branch_create'))
        
        # Check template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/branch_form.html')
        
        # Check title shows "Create"
        self.assertContains(response, 'Create New Branch')
        
        # Check form fields are present
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="code"')
        self.assertContains(response, 'name="is_active"')
        
        # Check CSRF token
        self.assertContains(response, 'csrfmiddlewaretoken')
        
        # Check buttons
        self.assertContains(response, 'Create Branch')
        self.assertContains(response, 'Cancel')
    
    def test_branch_update_template_loads(self):
        """Test that branch edit form template loads correctly."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('branch_update', kwargs={'pk': self.branch.pk}))
        
        # Check template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assets/branch_form.html')
        
        # Check title shows "Edit"
        self.assertContains(response, 'Edit Branch')
        
        # Check form is pre-filled with branch data
        self.assertContains(response, 'Test Branch')
        self.assertContains(response, 'TST')
        
        # Check buttons
        self.assertContains(response, 'Update Branch')
        self.assertContains(response, 'Cancel')
    
    def test_branch_form_validation_errors_display(self):
        """Test that validation errors are displayed in template."""
        self.client.login(username='admin', password='testpass123')
        
        # Submit empty form
        response = self.client.post(reverse('branch_create'), {
            'name': '',
            'code': '',
            'is_active': True
        })
        
        # Should show validation errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error-message')
    
    def test_branch_form_help_text_display(self):
        """Test that help text is displayed for fields."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('branch_create'))
        
        # Check help text is displayed
        self.assertContains(response, 'Short code for the branch')
        self.assertContains(response, 'Inactive branches cannot be assigned')
    
    def test_branch_form_cancel_button_links_to_list(self):
        """Test that cancel button links to branch list."""
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('branch_create'))
        
        # Check cancel button links to branch list
        self.assertContains(response, reverse('branch_list'))
    
    def test_branch_create_form_submission(self):
        """Test creating a branch through the form."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post(reverse('branch_create'), {
            'name': 'New Branch',
            'code': 'NEW',
            'is_active': True
        })
        
        # Should redirect to branch list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('branch_list'))
        
        # Branch should be created
        self.assertTrue(Branch.objects.filter(name='New Branch', code='NEW').exists())
    
    def test_branch_update_form_submission(self):
        """Test updating a branch through the form."""
        self.client.login(username='admin', password='testpass123')
        
        response = self.client.post(
            reverse('branch_update', kwargs={'pk': self.branch.pk}),
            {
                'name': 'Updated Branch',
                'code': 'UPD',
                'is_active': False
            }
        )
        
        # Should redirect to branch list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('branch_list'))
        
        # Branch should be updated
        self.branch.refresh_from_db()
        self.assertEqual(self.branch.name, 'Updated Branch')
        self.assertEqual(self.branch.code, 'UPD')
        self.assertEqual(self.branch.is_active, False)
