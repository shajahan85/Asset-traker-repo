"""Views for managing secondary IP addresses on assets."""
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError

from assets.models import Asset, AssetIPAddress
from assets.forms.secondary_ip_form import SecondaryIPForm
from assets.services.asset_ip_service import AssetIPService
from assets.permissions.decorators import AdminRequiredMixin


class AddSecondaryIPView(AdminRequiredMixin, View):
    """View for adding secondary IP addresses to assets."""
    
    def get(self, request, pk):
        """Display form to add secondary IP."""
        asset = get_object_or_404(Asset, pk=pk)
        form = SecondaryIPForm(asset=asset)
        
        context = {
            'asset': asset,
            'form': form,
            'primary_ip': asset.get_primary_ip(),
            'secondary_ips': asset.get_secondary_ips(),
        }
        return render(request, 'assets/add_secondary_ip.html', context)
    
    def post(self, request, pk):
        """Process secondary IP addition."""
        asset = get_object_or_404(Asset, pk=pk)
        form = SecondaryIPForm(request.POST, asset=asset)
        
        if form.is_valid():
            try:
                ip_type = form.cleaned_data['ip_type']
                
                if ip_type == 'managed':
                    ip_address = form.cleaned_data['ip_address']
                    AssetIPService.add_secondary_ip(
                        asset=asset,
                        ip_address=ip_address,
                        user=request.user
                    )
                    messages.success(request, f'Secondary IP {ip_address.address} added successfully.')
                else:
                    manual_ip = form.cleaned_data['manual_ip']
                    AssetIPService.add_secondary_ip(
                        asset=asset,
                        manual_ip=manual_ip,
                        user=request.user
                    )
                    messages.success(request, f'Secondary IP {manual_ip} added successfully.')
                
                return redirect('asset_update', pk=asset.pk)
            
            except ValidationError as e:
                messages.error(request, str(e))
                return self.get(request, pk)
        
        # Form invalid
        context = {
            'asset': asset,
            'form': form,
            'primary_ip': asset.get_primary_ip(),
            'secondary_ips': asset.get_secondary_ips(),
        }
        return render(request, 'assets/add_secondary_ip.html', context)


class RemoveSecondaryIPView(AdminRequiredMixin, View):
    """View for removing secondary IP addresses from assets."""
    
    def post(self, request, pk):
        """Process secondary IP removal."""
        asset_ip = get_object_or_404(AssetIPAddress, pk=pk)
        asset = asset_ip.asset
        
        try:
            ip_display = asset_ip.get_ip_display()
            AssetIPService.remove_secondary_ip(asset_ip, user=request.user)
            messages.success(request, f'Secondary IP {ip_display} removed successfully.')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('asset_update', pk=asset.pk)


class SetPrimaryIPView(AdminRequiredMixin, View):
    """View for changing which IP is the primary IP."""
    
    def post(self, request, pk):
        """Process primary IP change."""
        asset_ip = get_object_or_404(AssetIPAddress, pk=pk)
        asset = asset_ip.asset
        
        try:
            AssetIPService.set_primary_ip(asset, asset_ip, user=request.user)
            ip_display = asset_ip.get_ip_display()
            messages.success(request, f'IP {ip_display} is now the primary IP.')
        except ValidationError as e:
            messages.error(request, str(e))
        
        return redirect('asset_update', pk=asset.pk)
