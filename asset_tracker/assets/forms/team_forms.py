"""
Forms for team management.
"""
from django import forms
from assets.models import Team, Branch


class TeamForm(forms.ModelForm):
    """Form for creating and updating teams."""
    
    class Meta:
        model = Team
        fields = ['name', 'branch', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team name'
            }),
            'branch': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_branch'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_parent'
            }),
        }
        labels = {
            'name': 'Team Name',
            'branch': 'Branch',
            'parent': 'Parent Team (Optional)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate branch dropdown with active branches only
        self.fields['branch'].queryset = Branch.objects.filter(is_active=True)
        self.fields['branch'].empty_label = "Select Branch"
        self.fields['branch'].required = True
        
        # Populate parent team dropdown
        self.fields['parent'].queryset = Team.objects.filter(parent__isnull=True).order_by('name')
        self.fields['parent'].empty_label = "None (Root Team)"
        self.fields['parent'].required = False
        
        # For editing existing teams
        if self.instance and self.instance.pk:
            # Filter parent teams to only show teams from the same branch (excluding self and descendants)
            if self.instance.branch:
                self.fields['parent'].queryset = Team.objects.filter(
                    branch=self.instance.branch,
                    parent__isnull=True
                ).exclude(pk=self.instance.pk).order_by('name')
        
        # For form submission with POST data
        if self.data:
            try:
                branch_id = self.data.get('branch')
                if branch_id:
                    # Filter parent teams by selected branch
                    self.fields['parent'].queryset = Team.objects.filter(
                        branch_id=branch_id,
                        parent__isnull=True
                    ).order_by('name')
                    
                    # Exclude current team if editing
                    if self.instance and self.instance.pk:
                        self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(
                            pk=self.instance.pk
                        )
            except (ValueError, TypeError):
                pass
    
    def clean(self):
        """Validate team data."""
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        branch = cleaned_data.get('branch')
        name = cleaned_data.get('name')
        
        # Validate parent belongs to same branch
        if parent and branch:
            if parent.branch_id != branch.id:
                raise forms.ValidationError({
                    'parent': 'Parent team must belong to the same branch.'
                })
        
        # Validate team name uniqueness within branch
        if name and branch:
            existing_teams = Team.objects.filter(name=name, branch=branch)
            
            # Exclude current team if editing
            if self.instance and self.instance.pk:
                existing_teams = existing_teams.exclude(pk=self.instance.pk)
            
            if existing_teams.exists():
                raise forms.ValidationError({
                    'name': f'A team with this name already exists in {branch.name} branch.'
                })
        
        return cleaned_data


class DeleteTeamForm(forms.Form):
    """Form for deleting teams with password confirmation."""
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        label='Admin Password',
        required=True,
        help_text='Enter your admin password to confirm team deletion'
    )
    
    def clean_password(self):
        """Validate that password is provided."""
        password = self.cleaned_data.get('password')
        
        if not password:
            raise forms.ValidationError("Password is required to delete a team.")
        
        return password
