"""Form for adding secondary IP addresses to assets."""
from django import forms
from assets.models import IPAddress
from assets.forms.asset_forms import get_filtered_free_ips


class SecondaryIPForm(forms.Form):
    """Form for adding secondary IP addresses to assets."""
    
    IP_TYPE_CHOICES = [
        ('managed', 'Managed IP (from IP pool)'),
        ('manual', 'Manual IP (enter manually)'),
    ]
    
    ip_type = forms.ChoiceField(
        choices=IP_TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Secondary IP',
        initial='managed'
    )
    
    ip_address = forms.ModelChoiceField(
        queryset=IPAddress.objects.none(),
        required=False,
        empty_label="Select IP Address",
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_managed_ip'}),
        label='Secondary IP (Managed)'
    )
    
    manual_ip = forms.GenericIPAddressField(
        protocol='IPv4',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_manual_ip_input',
            'placeholder': 'e.g., 192.168.1.100',
            'style': 'display:none;'
        }),
        label='Secondary IP (Manual)'
    )
    
    def __init__(self, *args, **kwargs):
        asset = kwargs.pop('asset', None)
        super().__init__(*args, **kwargs)
        
        # Populate managed IP dropdown with filtered free IPs
        available_ips = get_filtered_free_ips()
        self.fields['ip_address'].choices = [('', 'Select IP Address (192.168.10/11/50/70.x)')] + [
            (ip.pk, str(ip.address)) for ip in available_ips
        ]
    
    def clean(self):
        """Validate that exactly one IP type is provided."""
        cleaned_data = super().clean()
        ip_type = cleaned_data.get('ip_type')
        ip_address = cleaned_data.get('ip_address')
        manual_ip = cleaned_data.get('manual_ip')
        
        if ip_type == 'managed':
            if not ip_address:
                raise forms.ValidationError("Please select a managed IP address.")
            cleaned_data['manual_ip'] = None
        elif ip_type == 'manual':
            if not manual_ip:
                raise forms.ValidationError("Please enter a manual IP address.")
            cleaned_data['ip_address'] = None
        
        return cleaned_data
