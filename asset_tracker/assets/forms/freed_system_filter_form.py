"""
Filter form for freed systems list filtering.

This form provides filtering options for the freed systems view,
including asset tag search, system type, health status, and branch filters.
"""

from django import forms
from assets.models import Asset, Branch


class FreedSystemFilterForm(forms.Form):
    """Form for filtering freed systems in the freed systems list view."""
    
    search = forms.CharField(
        label='Asset Tag',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by asset tag...'
        })
    )
    
    branch = forms.ModelChoiceField(
        label='Branch',
        queryset=Branch.objects.filter(is_active=True),
        required=False,
        empty_label='-- All Branches --',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    system_type = forms.ChoiceField(
        label='System Type',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    health_status = forms.ChoiceField(
        label='Health Status',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form and populate dropdown choices.
        """
        super().__init__(*args, **kwargs)
        
        # Populate system type choices
        system_type_choices = [('', '-- All System Types --')]
        system_type_choices.extend([
            (choice[0], choice[1]) 
            for choice in Asset.SYSTEM_TYPE_CHOICES
        ])
        self.fields['system_type'].choices = system_type_choices
        
        # Populate health status choices
        health_status_choices = [('', '-- All Health Status --')]
        health_status_choices.extend([
            (choice[0], choice[1]) 
            for choice in Asset.HEALTH_STATUS_CHOICES
        ])
        self.fields['health_status'].choices = health_status_choices
