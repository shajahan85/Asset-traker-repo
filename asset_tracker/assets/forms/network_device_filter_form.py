"""
Filter form for network devices list filtering.

This form provides filtering options for the network devices view,
including device name and IP address search filters.
"""

from django import forms


class NetworkDeviceFilterForm(forms.Form):
    """Form for filtering network devices in the network devices list view."""
    
    device_name = forms.CharField(
        label='Device Name',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by device name...'
        })
    )
    
    ip_address = forms.CharField(
        label='IP Address',
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by IP address...'
        })
    )
