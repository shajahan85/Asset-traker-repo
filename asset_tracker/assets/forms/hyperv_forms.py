"""
Forms for Hyper-V VM management.
"""
from django import forms
from django.db import models
from assets.models import HyperVVM, Asset, IPAddress


class HyperVVMForm(forms.ModelForm):
    """Form for creating and editing Hyper-V VMs."""
    
    host_machine_select = forms.ModelChoiceField(
        queryset=Asset.objects.filter(
            status='active'
        ).select_related('ip_address').order_by('asset_tag'),
        required=False,
        empty_label="Select Host Machine",
        label='Host Machine (Asset Tag)',
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_host_machine_select'
        }),
        help_text='Select the host machine by asset tag'
    )
    
    host_machine_ip = forms.CharField(
        required=False,
        label='Host Machine IP Address',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_host_machine_ip',
            'placeholder': 'e.g., 192.168.11.100'
        }),
        help_text='Or enter host machine IP address'
    )
    
    class Meta:
        model = HyperVVM
        fields = ['name', 'manual_ip', 'power_status', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., VM-WebServer-01'
            }),
            'manual_ip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 192.168.10.50'
            }),
            'power_status': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Additional notes about this VM'
            }),
        }
        labels = {
            'name': 'VM Name',
            'manual_ip': 'VM IP Address',
            'power_status': 'Power Status',
            'notes': 'Notes',
        }
        help_texts = {
            'manual_ip': 'Enter the IP address of this virtual machine',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make manual_ip optional
        self.fields['manual_ip'].required = False
        
        # Set initial values for edit mode
        if self.instance and self.instance.pk:
            self.fields['host_machine_select'].initial = self.instance.host_machine
            # Set host machine IP
            if self.instance.host_machine.ip_address:
                self.fields['host_machine_ip'].initial = self.instance.host_machine.ip_address.address
            elif self.instance.host_machine.manual_ip:
                self.fields['host_machine_ip'].initial = self.instance.host_machine.manual_ip
    
    def label_from_instance(self, obj):
        """Custom label for host machine dropdown showing asset tag only."""
        return obj.asset_tag
    
    def clean(self):
        cleaned_data = super().clean()
        host_machine_select = cleaned_data.get('host_machine_select')
        host_machine_ip = cleaned_data.get('host_machine_ip')
        
        # At least one must be provided
        if not host_machine_select and not host_machine_ip:
            raise forms.ValidationError('Please select a host machine or enter a host machine IP address.')
        
        # If host_machine_select is provided, use it
        if host_machine_select:
            cleaned_data['host_machine'] = host_machine_select
        # If host_machine_ip is provided, find the asset
        elif host_machine_ip:
            # Find host machine by IP (check both managed and manual)
            host_asset = Asset.objects.filter(
                ip_address__address=host_machine_ip,
                status='active'
            ).first()
            
            if not host_asset:
                host_asset = Asset.objects.filter(
                    manual_ip=host_machine_ip,
                    status='active'
                ).first()
            
            if not host_asset:
                raise forms.ValidationError(f'No active asset found with IP {host_machine_ip}. Please check the IP address.')
            
            cleaned_data['host_machine'] = host_asset
        
        return cleaned_data
