"""
Django forms for scrapped system management.
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


class ScrappedSystemForm(forms.ModelForm):
    """Form for manually creating scrapped systems."""
    
    class Meta:
        model = Asset
        fields = [
            'asset_tag', 'system_type', 'operating_system', 
            'ip_address', 'manual_ip', 'scrapping_reason', 
            'manufacturer', 'particulars'
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
            'scrapping_reason': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Explain why this system is being scrapped'
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
            'scrapping_reason': 'Scrapping Reason',
            'manufacturer': 'Manufacturer',
            'particulars': 'Particulars'
        }
        help_texts = {
            'ip_address': 'Select from managed IP addresses',
            'manual_ip': 'Or enter an IP address manually',
            'scrapping_reason': 'Explain why this system is being scrapped'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
        self.fields['scrapping_reason'].required = True
        self.fields['manufacturer'].required = False
        self.fields['particulars'].required = False
    
    def clean(self):
        """Custom validation."""
        cleaned_data = super().clean()
        scrapping_reason = cleaned_data.get('scrapping_reason')
        
        # Validate scrapping_reason is provided
        if not scrapping_reason or not scrapping_reason.strip():
            raise ValidationError({
                'scrapping_reason': 'Scrapping reason is required.'
            })
        
        return cleaned_data
