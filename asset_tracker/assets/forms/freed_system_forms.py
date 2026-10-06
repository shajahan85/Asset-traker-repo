"""
Django forms for freed system management.
"""
from django import forms
from django.db import models
from django.core.exceptions import ValidationError
from assets.models import Asset, OperatingSystem, IPAddress


def get_filtered_free_ips(include_current_ip_id=None):
    """
    Get free IPs filtered to specific ranges for easier selection.
    IPs are sorted numerically in ascending order.
    
    Args:
        include_current_ip_id: Optional IP ID to include even if assigned (for editing)
    
    Returns:
        List of IPAddress objects filtered to common ranges, sorted numerically
    """
    # Define the allowed IP ranges
    allowed_ranges = ['192.168.10.', '192.168.11.', '192.168.50.', '192.168.70.']
    
    # Build query to filter by ranges
    range_query = models.Q()
    for range_prefix in allowed_ranges:
        range_query |= models.Q(address__startswith=range_prefix)
    
    # Get free IPs in the specified ranges
    if include_current_ip_id:
        # Include current IP and free IPs in specified ranges
        ips = IPAddress.objects.filter(
            (models.Q(is_assigned=False) & range_query) | 
            models.Q(pk=include_current_ip_id)
        )
    else:
        # Only free IPs in specified ranges
        ips = IPAddress.objects.filter(
            is_assigned=False
        ).filter(range_query)
    
    # Convert to list and sort numerically by IP address
    ip_list = list(ips)
    ip_list.sort(key=lambda ip: tuple(int(part) for part in ip.address.split('.')))
    
    return ip_list


class FreedSystemForm(forms.ModelForm):
    """Form for manually creating freed systems."""
    
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'system_type', 'operating_system', 
            'ip_address', 'manual_ip', 'health_status', 
            'issues_description', 'manufacturer', 'particulars'
        ]
        widgets = {
            'asset_tag': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique asset tag'
            }),
            'system_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'operating_system': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ip_address': forms.Select(attrs={
                'class': 'form-control'
            }),
            'manual_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10.0.0.50'
            }),
            'health_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'issues_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issues with this defective system'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dell, HP, Lenovo'
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about the system'
            })
        }
        labels = {
            'asset_tag': 'Asset Tag',
            'system_type': 'System Type',
            'operating_system': 'Operating System',
            'ip_address': 'IP Address (Managed)',
            'manual_ip': 'IP Address (Manual)',
            'health_status': 'Health Status',
            'issues_description': 'Issues Description',
            'manufacturer': 'Manufacturer',
            'particulars': 'Particulars'
        }
        help_texts = {
            'ip_address': 'Select from managed IP addresses',
            'manual_ip': 'Or enter an IP address manually',
            'health_status': 'Select the operational status of this system',
            'issues_description': 'Required if health status is Defective'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make health_status required
        self.fields['health_status'].required = True
        
        # Populate operating system dropdown
        self.fields['operating_system'].queryset = OperatingSystem.objects.all()
        self.fields['operating_system'].empty_label = "Select Operating System"
        
        # Populate IP address dropdown with filtered available IPs
        available_ips = get_filtered_free_ips()
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x) (Optional)')] + [(ip.pk, str(ip.address)) for ip in available_ips]
        self.fields['ip_address'].required = False
        
        # Set field requirements
        self.fields['asset_tag'].required = True
        self.fields['system_type'].required = True
        self.fields['operating_system'].required = True
        self.fields['manual_ip'].required = False
        self.fields['issues_description'].required = False
        self.fields['manufacturer'].required = False
        self.fields['particulars'].required = False
    
    def clean(self):
        """Custom validation to enforce conditional requirements."""
        cleaned_data = super().clean()
        health_status = cleaned_data.get('health_status')
        issues_description = cleaned_data.get('issues_description')
        
        # Validate issues_description required for defective systems
        if health_status == 'defective':
            if not issues_description or not issues_description.strip():
                raise ValidationError({
                    'issues_description': 'Issue description is required for defective systems.'
                })
        
        return cleaned_data


class FreedSystemEditForm(forms.ModelForm):
    """Form for editing freed system health status."""
    
    class Meta:
        model = Asset
        fields = ['health_status', 'issues_description', 'particulars']
        widgets = {
            'health_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'issues_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issues with this defective system'
            }),
            'particulars': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional details about the system'
            })
        }
        labels = {
            'health_status': 'Health Status',
            'issues_description': 'Issues Description',
            'particulars': 'Particulars'
        }
        help_texts = {
            'health_status': 'Update the operational status of this system',
            'issues_description': 'Required if health status is Defective'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make health_status required
        self.fields['health_status'].required = True
        self.fields['issues_description'].required = False
        self.fields['particulars'].required = False
    
    def clean(self):
        """Custom validation to enforce conditional requirements."""
        cleaned_data = super().clean()
        health_status = cleaned_data.get('health_status')
        issues_description = cleaned_data.get('issues_description')
        
        # Validate issues_description required for defective systems
        if health_status == 'defective':
            if not issues_description or not issues_description.strip():
                raise ValidationError({
                    'issues_description': 'Issue description is required for defective systems.'
                })
        
        return cleaned_data
