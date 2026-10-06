"""
Forms for testing device management.

This module provides forms for creating, updating, and filtering testing devices.
"""

from django import forms
from assets.models import TestingDevice, IPAddress


class TestingDeviceForm(forms.ModelForm):
    """Form for creating and updating testing devices."""
    
    # Manual IP entry field (not part of model form)
    ip_manual_entry = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter IP address manually (e.g., 192.168.1.100)'
        }),
        label='Manual IP Address',
        help_text='Enter an IP address if not available in the dropdown'
    )
    
    class Meta:
        model = TestingDevice
        fields = ['device_name', 'assigned_user', 'ip_address']
        widgets = {
            'device_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., iPhone 12 Pro, Samsung Galaxy Tab S8'
            }),
            'assigned_user': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter user name'
            }),
            'ip_address': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'device_name': 'Device Name',
            'assigned_user': 'Assigned User',
            'ip_address': 'IP Address',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Populate IP address dropdown with free IPs
        free_ips = IPAddress.objects.filter(is_assigned=False).order_by('address')
        self.fields['ip_address'].queryset = free_ips
        self.fields['ip_address'].empty_label = "Select IP Address (optional)"
        self.fields['ip_address'].required = False
        
        # For editing, include the currently assigned IP
        if self.instance and self.instance.pk and self.instance.ip_address:
            self.fields['ip_address'].queryset = IPAddress.objects.filter(
                models.Q(pk=self.instance.ip_address.pk) | models.Q(is_assigned=False)
            ).order_by('address')
        
        # Pre-populate manual IP if editing with manual IP
        if self.instance and self.instance.pk and self.instance.manual_ip:
            self.fields['ip_manual_entry'].initial = self.instance.manual_ip
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        ip_address = cleaned_data.get('ip_address')
        ip_manual_entry = cleaned_data.get('ip_manual_entry', '').strip()
        
        # Ensure either managed IP or manual IP is provided, but not both
        if ip_address and ip_manual_entry:
            raise forms.ValidationError('Please provide either IP Address or Manual IP, not both.')
        
        return cleaned_data


class TestingDeviceFilterForm(forms.Form):
    """Form for filtering testing devices in the testing devices list view."""
    
    device_name = forms.CharField(
        label='Device Name',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by device name...'
        })
    )
    
    assigned_user = forms.CharField(
        label='Assigned User',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by user name...'
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


# Import Q for queryset filtering in __init__
from django.db import models
