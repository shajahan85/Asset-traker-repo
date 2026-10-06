"""Forms for branch management."""
from django import forms
from assets.models import Branch


class BranchForm(forms.ModelForm):
    """Form for creating and editing branches."""
    
    class Meta:
        model = Branch
        fields = ['name', 'code', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch name (e.g., Kochi)'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter branch code (e.g., KCH)',
                'maxlength': '10'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'name': 'Branch Name',
            'code': 'Branch Code',
            'is_active': 'Active',
        }
        help_texts = {
            'code': 'Short code for the branch (e.g., KCH, PUN, BLR, DEL)',
            'is_active': 'Inactive branches cannot be assigned to new assets',
        }
    
    def clean_code(self):
        """Validate and uppercase the branch code."""
        code = self.cleaned_data.get('code', '').strip().upper()
        return code
    
    def clean_name(self):
        """Validate branch name."""
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError('Branch name is required.')
        return name
