"""
Filter form for asset list filtering.

This form provides filtering options for the asset list view,
including operating system, asset tag, team, branch, and assigned user filters.
"""

from django import forms
from assets.models import OperatingSystem, Team, Branch


class AssetFilterForm(forms.Form):
    """Form for filtering assets in the asset list view."""
    
    branch = forms.ChoiceField(
        label='Branch',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    operating_system = forms.ChoiceField(
        label='Operating System',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    system_type = forms.ChoiceField(
        label='System Type',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    asset_tag = forms.CharField(
        label='Asset Tag',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by asset tag...'
        })
    )
    
    team = forms.ChoiceField(
        label='Team',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    assigned_to = forms.CharField(
        label='Assigned To',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by user name...'
        })
    )
    
    employee_code = forms.CharField(
        label='Employee Code',
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by employee code...'
        })
    )
    
    ip_address = forms.CharField(
        label='IP Address',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by IP address...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form and populate dropdown choices from database.
        """
        super().__init__(*args, **kwargs)
        
        # Populate branch choices
        branch_choices = [('', '-- All Branches --')]
        branch_choices.extend([
            (branch.id, branch.name) 
            for branch in Branch.objects.filter(is_active=True).order_by('name')
        ])
        self.fields['branch'].choices = branch_choices
        
        # Populate operating system choices
        os_choices = [('', '-- All Operating Systems --')]
        os_choices.extend([
            (os.id, os.name) 
            for os in OperatingSystem.objects.all().order_by('name')
        ])
        self.fields['operating_system'].choices = os_choices
        
        # Populate system type choices
        from assets.models import Asset
        system_type_choices = [('', '-- All System Types --')]
        system_type_choices.extend([
            (choice[0], choice[1]) 
            for choice in Asset.SYSTEM_TYPE_CHOICES
        ])
        self.fields['system_type'].choices = system_type_choices
        
        # Populate team choices
        team_choices = [('', '-- All Teams --')]
        team_choices.extend([
            (team.id, team.name) 
            for team in Team.objects.all().order_by('name')
        ])
        self.fields['team'].choices = team_choices
