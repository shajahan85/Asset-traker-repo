from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .models import Asset, OperatingSystem, Team, HyperVVM, IPAddress
from .forms import AssetForm
from .forms.import_form import AssetImportForm
from .forms.filter_form import AssetFilterForm
from .permissions import AdminRequiredMixin
from .services.asset_service import AssetService
from .services.import_service import ImportService
from .services.export_service import ExportService
from .services.filter_service import FilterService
from .services.hyperv_service import HyperVService
import re


class AssetListView(LoginRequiredMixin, ListView):
    """Display all active assets ordered by serial number with filtering support."""
    model = Asset
    template_name = 'assets/asset_list.html'
    context_object_name = 'assets'
    login_url = '/login/'

    def get_queryset(self):
        """Return active assets with filters applied, ordered by asset_tag."""
        # Start with base queryset of active assets
        queryset = Asset.objects.filter(status='active').select_related(
            'operating_system', 'ip_address', 'team', 'team__parent', 'branch'
        ).prefetch_related(
            'asset_ip_addresses', 'asset_ip_addresses__ip_address', 'accessories'
        ).order_by('asset_tag')
        
        # Initialize filter form with GET parameters
        filter_form = AssetFilterForm(self.request.GET)
        
        # Apply filters if form is valid
        if filter_form.is_valid():
            filter_service = FilterService()
            queryset = filter_service.apply_filters(queryset, filter_form.cleaned_data)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter form to template context."""
        context = super().get_context_data(**kwargs)
        
        # Initialize filter form with GET parameters to preserve filter values
        context['filter_form'] = AssetFilterForm(self.request.GET)
        
        return context


class AssetCreateView(AdminRequiredMixin, CreateView):
    """Handle asset creation (admin only)."""
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('asset_list')

    def get_context_data(self, **kwargs):
        """Add formset to context."""
        from .forms.asset_forms import AdditionalIPFormSet, AccessoryFormSet
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            context['additional_ip_formset'] = AdditionalIPFormSet(
                self.request.POST,
                instance=self.object
            )
            context['accessory_formset'] = AccessoryFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            context['additional_ip_formset'] = AdditionalIPFormSet(
                instance=self.object
            )
            context['accessory_formset'] = AccessoryFormSet(
                instance=self.object
            )
        
        return context

    def form_valid(self, form):
        """Process form submission using AssetService.create_asset()."""
        from .forms.asset_forms import AdditionalIPFormSet, AccessoryFormSet
        from django.db import transaction
        
        # Get formset from context
        context = self.get_context_data()
        additional_ip_formset = context['additional_ip_formset']
        accessory_formset = context['accessory_formset']
        
        # Validate formset
        if not additional_ip_formset.is_valid():
            return self.form_invalid(form)
        
        # Validate accessory formset (only if there's data)
        # For new assets, accessories can't be added yet, so skip validation if formset is empty
        if accessory_formset.has_changed() and not accessory_formset.is_valid():
            messages.error(self.request, 'Please correct the errors in accessories.')
            return self.form_invalid(form)
        
        try:
            # Wrap all saves in a transaction
            with transaction.atomic():
                # Prepare data dictionary from cleaned form data
                data = {}
                
                # Asset tag (required)
                data['asset_tag'] = form.cleaned_data['asset_tag']
                
                # System type (required)
                data['system_type'] = form.cleaned_data['system_type']
                
                # Hardware serial number
                data['hardware_serial_number'] = form.cleaned_data.get('hardware_serial_number', '')
                
                # Manufacturer (optional)
                data['manufacturer'] = form.cleaned_data.get('manufacturer', '')
                
                # Operating System - check manual entry first, then dropdown
                os_manual_entry = self.request.POST.get('os_manual_entry', '').strip()
                if os_manual_entry:
                    os_obj, created = OperatingSystem.objects.get_or_create(name=os_manual_entry)
                    data['operating_system'] = os_obj.id
                elif form.cleaned_data.get('operating_system'):
                    data['operating_system'] = form.cleaned_data['operating_system'].id
                else:
                    data['operating_system'] = None
                
                # IP Address - check manual entry first, then dropdown
                ip_manual_entry = self.request.POST.get('ip_manual_entry', '').strip()
                if ip_manual_entry:
                    data['manual_ip'] = ip_manual_entry
                    data['ip_address'] = None
                elif form.cleaned_data.get('ip_address'):
                    data['ip_address'] = form.cleaned_data['ip_address'].id
                    data['manual_ip'] = None
                else:
                    data['ip_address'] = None
                    data['manual_ip'] = None
                
                # Particulars (optional)
                data['particulars'] = form.cleaned_data.get('particulars', '')
                
                # Assigned to (optional)
                data['assigned_to'] = form.cleaned_data.get('assigned_to', '')
                
                # Employee code (optional)
                data['employee_code'] = form.cleaned_data.get('employee_code', '')
                
                # Team (from hidden field set by form clean method)
                if form.cleaned_data.get('team'):
                    data['team'] = form.cleaned_data['team'].id
                else:
                    data['team'] = None
                
                # Branch (required)
                if form.cleaned_data.get('branch'):
                    data['branch'] = form.cleaned_data['branch'].id
                else:
                    data['branch'] = None
                
                # Warranty expiration (optional)
                data['warranty_expiration'] = form.cleaned_data.get('warranty_expiration')

                # Create asset using service
                # Get checkbox value - skip notification if unchecked
                skip_notification = not form.cleaned_data.get('send_notification', True)
                asset = AssetService.create_asset(data, self.request.user, skip_notification)
                
                # Create primary IP junction record
                from assets.models import AssetIPAddress as AssetIPModel
                ip_manual_entry = self.request.POST.get('ip_manual_entry', '').strip()
                new_managed_ip = form.cleaned_data.get('ip_address')
                
                if ip_manual_entry:
                    AssetIPModel.objects.create(
                        asset=asset,
                        ip_address=None,
                        manual_ip=ip_manual_entry,
                        is_primary=True
                    )
                elif new_managed_ip:
                    AssetIPModel.objects.create(
                        asset=asset,
                        ip_address=new_managed_ip,
                        manual_ip=None,
                        is_primary=True
                    )
                    # Mark IP as assigned (service may already do this, but ensure it)
                    new_managed_ip.is_assigned = True
                    new_managed_ip.assigned_to_asset = asset
                    new_managed_ip.save()
                
                # Save additional IPs formset
                additional_ip_formset.instance = asset
                additional_ip_formset.save()
                
                # Save accessories formset
                accessory_formset.instance = asset
                accessory_formset.save()
                
                # Handle file attachment if provided
                if 'attachment_file' in self.request.FILES:
                    from .services.attachment_service import AttachmentService
                    attachment_file = self.request.FILES['attachment_file']
                    try:
                        AttachmentService.upload_attachment(asset, attachment_file)
                        messages.success(self.request, f'Attachment "{attachment_file.name}" uploaded successfully.')
                    except ValidationError as e:
                        messages.warning(self.request, f'Asset created but attachment upload failed: {str(e)}')

                # Display success message
                messages.success(self.request, f'Asset {asset.asset_tag} created successfully.')

                return redirect(self.success_url)

        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))

            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating asset: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class AssetDetailView(LoginRequiredMixin, View):
    """Display asset details including all IP addresses."""
    template_name = 'assets/asset_detail.html'
    login_url = '/login/'

    def get(self, request, pk):
        """Display asset detail page with all IP addresses."""
        from django.shortcuts import get_object_or_404, render

        asset = get_object_or_404(Asset, pk=pk)
        primary_ip = asset.get_primary_ip()
        secondary_ips = asset.get_secondary_ips()
        # Add filtered additional IPs for the new section
        additional_ips = asset.asset_ip_addresses.filter(is_primary=False)

        context = {
            'asset': asset,
            'primary_ip': primary_ip,
            'secondary_ips': secondary_ips,
            'additional_ips': additional_ips,
        }
        return render(request, self.template_name, context)


class AssetUpdateView(AdminRequiredMixin, UpdateView):
    """Handle asset updates (admin only)."""
    model = Asset
    form_class = AssetForm
    template_name = 'assets/asset_form.html'
    success_url = reverse_lazy('asset_list')
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """Get the asset to update."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Asset, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_form_kwargs(self):
        """Pass the asset instance to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs

    def get_context_data(self, **kwargs):
        """Add formset with existing additional IPs to context."""
        from .forms.asset_forms import AdditionalIPFormSet, AccessoryFormSet
        
        # Ensure we have the object before calling super()
        if not hasattr(self, 'object') or self.object is None:
            self.object = self.get_object()
        
        context = super().get_context_data(**kwargs)
        
        if self.request.POST:
            # Pass queryset when creating formset with POST data to filter out primary IPs
            context['additional_ip_formset'] = AdditionalIPFormSet(
                self.request.POST,
                instance=self.object,
                queryset=self.object.asset_ip_addresses.filter(is_primary=False)
            )
            context['accessory_formset'] = AccessoryFormSet(
                self.request.POST,
                instance=self.object
            )
        else:
            # Filter to only non-primary IPs for the formset
            context['additional_ip_formset'] = AdditionalIPFormSet(
                instance=self.object,
                queryset=self.object.asset_ip_addresses.filter(is_primary=False)
            )
            context['accessory_formset'] = AccessoryFormSet(
                instance=self.object
            )
        
        return context

    def form_valid(self, form):
        """Process form submission using AssetService.update_asset() and handle formset."""
        from .forms.asset_forms import AdditionalIPFormSet, AccessoryFormSet
        from django.db import transaction
        from django.utils import timezone
        from django.contrib.auth import authenticate
        
        # Check if asset tag was changed
        asset = self.get_object()
        old_asset_tag = asset.asset_tag
        new_asset_tag = form.cleaned_data.get('asset_tag')
        asset_tag_changed = (old_asset_tag != new_asset_tag)
        
        # If asset tag changed, verify admin password
        if asset_tag_changed:
            admin_password = self.request.POST.get('admin_password_for_tag_change', '')
            
            if not admin_password:
                messages.error(self.request, 'Admin password is required to change the asset tag.')
                return self.form_invalid(form)
            
            # Verify admin password
            user = authenticate(username=self.request.user.username, password=admin_password)
            if not user or not user.is_staff:
                messages.error(self.request, 'Invalid admin password or you do not have admin privileges to change asset tags.')
                return self.form_invalid(form)
        
        # Get formset from context
        context = self.get_context_data()
        additional_ip_formset = context['additional_ip_formset']
        accessory_formset = context['accessory_formset']
        
        # Validate formset
        if not additional_ip_formset.is_valid():
            # Log formset errors for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error("=== FORMSET VALIDATION FAILED ===")
            logger.error(f"Asset: {asset.asset_tag}")
            logger.error(f"Formset errors: {additional_ip_formset.errors}")
            logger.error(f"Non-form errors: {additional_ip_formset.non_form_errors()}")
            logger.error("=== END FORMSET ERRORS ===")
            
            # Add formset errors to messages for user visibility
            messages.error(self.request, f'FORMSET VALIDATION FAILED for {asset.asset_tag}')
            
            for idx, form_errors in enumerate(additional_ip_formset.errors):
                if form_errors:
                    for field, errors in form_errors.items():
                        if isinstance(errors, list):
                            for error in errors:
                                messages.error(self.request, f'Additional IP #{idx + 1} - {field}: {error}')
                        else:
                            messages.error(self.request, f'Additional IP #{idx + 1} - {field}: {errors}')
            
            if additional_ip_formset.non_form_errors():
                for error in additional_ip_formset.non_form_errors():
                    messages.error(self.request, f'Additional IPs error: {error}')
            
            return self.form_invalid(form)
        
        # Validate accessory formset
        if not accessory_formset.is_valid():
            messages.error(self.request, 'Please correct the errors in accessories.')
            for idx, form_errors in enumerate(accessory_formset.errors):
                if form_errors:
                    for field, errors in form_errors.items():
                        if isinstance(errors, list):
                            for error in errors:
                                messages.error(self.request, f'Accessory #{idx + 1} - {field}: {error}')
            return self.form_invalid(form)
        
        try:
            # Wrap all operations in a transaction
            with transaction.atomic():
                asset = self.get_object()
                
                # Prepare data dictionary from cleaned form data
                data = {}
                
                # Asset tag (always required)
                data['asset_tag'] = form.cleaned_data['asset_tag']
                
                # System type (always required)
                data['system_type'] = form.cleaned_data['system_type']
                
                # Manufacturer (optional)
                if 'manufacturer' in form.cleaned_data:
                    data['manufacturer'] = form.cleaned_data.get('manufacturer', '')
                
                # Operating System - check manual entry first, then dropdown
                os_manual_entry = self.request.POST.get('os_manual_entry', '').strip()
                if os_manual_entry:
                    os_obj, created = OperatingSystem.objects.get_or_create(name=os_manual_entry)
                    data['operating_system'] = os_obj.id
                elif form.cleaned_data.get('operating_system'):
                    data['operating_system'] = form.cleaned_data['operating_system'].id
                
                # IP Address - check manual entry first, then dropdown
                ip_manual_entry = self.request.POST.get('ip_manual_entry', '').strip()
                if ip_manual_entry:
                    data['manual_ip'] = ip_manual_entry
                    data['ip_address'] = None
                elif form.cleaned_data.get('ip_address'):
                    data['ip_address'] = form.cleaned_data['ip_address'].id
                    data['manual_ip'] = None
                
                # Particulars (optional)
                if 'particulars' in form.cleaned_data:
                    data['particulars'] = form.cleaned_data.get('particulars', '')
                
                # Assigned to (optional)
                if 'assigned_to' in form.cleaned_data:
                    data['assigned_to'] = form.cleaned_data.get('assigned_to', '')
                
                # Employee code (optional)
                if 'employee_code' in form.cleaned_data:
                    data['employee_code'] = form.cleaned_data.get('employee_code', '')
                
                # Team (from hidden field set by form clean method)
                if form.cleaned_data.get('team'):
                    data['team'] = form.cleaned_data['team'].id
                
                # Branch (required)
                if form.cleaned_data.get('branch'):
                    data['branch'] = form.cleaned_data['branch'].id
                
                # Warranty expiration (optional)
                if 'warranty_expiration' in form.cleaned_data:
                    data['warranty_expiration'] = form.cleaned_data.get('warranty_expiration')
                
                # Hardware serial number (required for certain system types)
                if 'hardware_serial_number' in form.cleaned_data:
                    data['hardware_serial_number'] = form.cleaned_data.get('hardware_serial_number', '')

                # Update asset using service
                # Get checkbox value - skip notification if unchecked
                skip_notification = not form.cleaned_data.get('send_notification', True)
                updated_asset = AssetService.update_asset(asset, data, self.request.user, skip_notification)
                
                # Update primary IP in AssetIPAddress through-table
                from assets.models import AssetIPAddress as AssetIPModel
                
                primary_ip_type = form.cleaned_data.get('primary_ip_type', 'managed')
                ip_manual_entry = self.request.POST.get('ip_manual_entry', '').strip()
                new_managed_ip = form.cleaned_data.get('ip_address')
                
                # Get existing primary IP record
                old_primary = updated_asset.get_primary_ip()
                
                if ip_manual_entry:
                    # Switching to manual IP
                    if old_primary:
                        # Release old managed IP if it had one
                        if old_primary.ip_address:
                            old_primary.ip_address.is_assigned = False
                            old_primary.ip_address.assigned_to_asset = None
                            old_primary.ip_address.save()
                        old_primary.delete()
                    # Create new primary with manual IP
                    AssetIPModel.objects.create(
                        asset=updated_asset,
                        ip_address=None,
                        manual_ip=ip_manual_entry,
                        is_primary=True
                    )
                elif new_managed_ip:
                    # Using managed IP from dropdown
                    if old_primary:
                        if old_primary.ip_address != new_managed_ip:
                            # IP is changing - release old, assign new
                            if old_primary.ip_address:
                                old_primary.ip_address.is_assigned = False
                                old_primary.ip_address.assigned_to_asset = None
                                old_primary.ip_address.save()
                            old_primary.delete()
                            # Create new primary
                            AssetIPModel.objects.create(
                                asset=updated_asset,
                                ip_address=new_managed_ip,
                                manual_ip=None,
                                is_primary=True
                            )
                            # Mark new IP as assigned
                            new_managed_ip.is_assigned = True
                            new_managed_ip.assigned_to_asset = updated_asset
                            new_managed_ip.save()
                        # else: same IP, no change needed
                    else:
                        # No primary existed, create one
                        AssetIPModel.objects.create(
                            asset=updated_asset,
                            ip_address=new_managed_ip,
                            manual_ip=None,
                            is_primary=True
                        )
                        new_managed_ip.is_assigned = True
                        new_managed_ip.assigned_to_asset = updated_asset
                        new_managed_ip.save()
                
                # Release deleted managed IPs back to IP pool
                for deleted_form in additional_ip_formset.deleted_forms:
                    if deleted_form.instance.pk and deleted_form.instance.ip_address:
                        ip = deleted_form.instance.ip_address
                        ip.is_assigned = False
                        ip.assigned_to_asset = None
                        ip.freed_date = timezone.now()
                        ip.save()
                
                # Save formset (handles updates, deletions, and new entries automatically)
                additional_ip_formset.instance = updated_asset
                additional_ip_formset.save()
                
                # Save accessories formset
                accessory_formset.instance = updated_asset
                accessory_formset.save()
                
                # Handle file attachment if provided
                if 'attachment_file' in self.request.FILES:
                    from .services.attachment_service import AttachmentService
                    attachment_file = self.request.FILES['attachment_file']
                    try:
                        AttachmentService.upload_attachment(updated_asset, attachment_file)
                        messages.success(self.request, f'Attachment "{attachment_file.name}" uploaded successfully.')
                    except ValidationError as e:
                        messages.warning(self.request, f'Asset updated but attachment upload failed: {str(e)}')

                # Log asset tag change in history if it was changed
                if asset_tag_changed:
                    from assets.models import AssetHistory
                    AssetHistory.objects.create(
                        asset=updated_asset,
                        event_type='updated',
                        user=self.request.user.username,
                        changes={
                            'asset_tag': {
                                'old': old_asset_tag,
                                'new': new_asset_tag
                            }
                        },
                        notes=f'Asset tag changed from "{old_asset_tag}" to "{new_asset_tag}" with admin password verification.'
                    )
                    messages.success(self.request, f'Asset tag changed from "{old_asset_tag}" to "{new_asset_tag}" and logged in history.')
                else:
                    messages.success(self.request, f'Asset {updated_asset.asset_tag} updated successfully.')
                
                return redirect(self.success_url)

        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error updating asset: {str(e)}')
            return self.form_invalid(form)

    def form_invalid(self, form):
        """Handle form validation errors."""
        # Show detailed form errors for debugging
        error_details = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_details.append(f"Form error: {error}")
                else:
                    error_details.append(f"{field}: {error}")
        
        # Also check formset errors
        context = self.get_context_data(form=form)
        formset = context.get('additional_ip_formset')
        if formset and not formset.is_valid():
            for i, form_errors in enumerate(formset.errors):
                if form_errors:
                    for field, errors in form_errors.items():
                        for error in errors:
                            error_details.append(f"Additional IP #{i+1} - {field}: {error}")
            if formset.non_form_errors():
                for error in formset.non_form_errors():
                    error_details.append(f"Additional IPs: {error}")
        
        if error_details:
            messages.error(self.request, 'Errors: ' + ' | '.join(error_details))
        else:
            messages.error(self.request, 'Please correct the errors below.')
        
        return super().form_invalid(form)


class FreeSystemsView(LoginRequiredMixin, ListView):
    """Display all freed assets."""
    model = Asset
    template_name = 'assets/freed_systems.html'
    context_object_name = 'freed_assets'
    login_url = '/login/'

    def get_queryset(self):
        """Return only freed assets with filters applied."""
        from .forms.freed_system_filter_form import FreedSystemFilterForm
        
        queryset = Asset.objects.filter(status='freed').select_related(
            'operating_system', 'ip_address', 'branch'
        ).order_by('-freed_date')
        
        # Initialize filter form with GET parameters
        filter_form = FreedSystemFilterForm(self.request.GET)
        
        # Apply filters if form is valid
        if filter_form.is_valid():
            # Apply search filter
            search_query = filter_form.cleaned_data.get('search', '').strip()
            if search_query:
                queryset = queryset.filter(asset_tag__icontains=search_query)
            
            # Apply branch filter
            branch = filter_form.cleaned_data.get('branch')
            if branch:
                queryset = queryset.filter(branch=branch)
            
            # Apply system type filter
            system_type = filter_form.cleaned_data.get('system_type')
            if system_type:
                queryset = queryset.filter(system_type=system_type)
            
            # Apply health status filter
            health_status = filter_form.cleaned_data.get('health_status')
            if health_status:
                queryset = queryset.filter(health_status=health_status)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        from .forms.freed_system_filter_form import FreedSystemFilterForm
        
        context = super().get_context_data(**kwargs)
        
        # Initialize filter form with GET parameters to preserve filter values
        context['filter_form'] = FreedSystemFilterForm(self.request.GET)
        
        return context


class ScrappedItemsView(LoginRequiredMixin, ListView):
    """Display all scrapped assets ordered by scrapped_date descending."""
    model = Asset
    template_name = 'assets/scrapped_items.html'
    context_object_name = 'scrapped_assets'
    login_url = '/login/'

    def get_queryset(self):
        """Return only scrapped assets with optional search filter."""
        queryset = Asset.objects.filter(status='scrapped').select_related(
            'ip_address'
        ).order_by('-scrapped_date')
        
        # Apply search filter if provided
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(asset_tag__icontains=search_query)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add search query to context."""
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context


class ScrappedSystemCreateView(AdminRequiredMixin, CreateView):
    """Handle manual scrapped system creation (admin only)."""
    model = Asset
    template_name = 'assets/scrapped_system_create.html'
    success_url = reverse_lazy('scrapped_items')
    
    def get_form_class(self):
        from .forms.scrapped_system_forms import ScrappedSystemForm
        return ScrappedSystemForm
    
    def form_valid(self, form):
        """Process form submission using AssetService.create_scrapped_asset()."""
        try:
            asset = AssetService.create_scrapped_asset(
                form.cleaned_data,
                self.request.user
            )
            messages.success(
                self.request,
                f'Scrapped system {asset.asset_tag} created successfully.'
            )
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating scrapped system: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class FreeIPsView(LoginRequiredMixin, ListView):
    """Display all IP addresses grouped by range with free/occupied status."""
    model = Asset
    template_name = 'assets/free_ips.html'
    context_object_name = 'ip_ranges'
    login_url = '/login/'

    def get_queryset(self):
        """Return all IPs grouped by range using IPManagementService."""
        from .services.ip_management_service import IPManagementService
        return IPManagementService.get_all_ips_by_range_with_vms()

    def get_context_data(self, **kwargs):
        """Add grouped IPs dict to template context with VM relationship information."""
        from .services.ip_management_service import IPManagementService
        
        context = super().get_context_data(**kwargs)
        
        # Get IP ranges with VM relationship data (already optimized with bulk queries)
        ip_ranges = self.get_queryset()
        
        # Add VM range classification (no additional queries needed)
        for range_pattern, ip_data_list in ip_ranges.items():
            for ip_data in ip_data_list:
                ip = ip_data['ip']
                
                # Determine occupant type and name from already-loaded data
                # Check for guest assignment first
                if ip.guest_name:
                    ip.occupant_type = 'guest'
                    ip.occupant_name = ip.guest_name
                elif ip_data['is_vm'] and ip_data['vm']:
                    ip.occupant_type = 'vm'
                    ip.occupant_name = ip_data['vm'].name
                elif hasattr(ip, 'network_device') and ip.network_device:
                    ip.occupant_type = 'network_device'
                    ip.occupant_name = ip.network_device.device_name
                elif hasattr(ip, 'testing_device') and ip.testing_device:
                    ip.occupant_type = 'testing_device'
                    ip.occupant_name = f"{ip.testing_device.device_name} ({ip.testing_device.assigned_user or 'Unassigned'})"
                elif ip.manually_occupied:
                    ip.occupant_type = 'manually_occupied'
                    ip.occupant_name = f"Marked by: {ip.occupied_by}"
                elif ip.assigned_to_asset:
                    ip.occupant_type = 'asset'
                    base_name = ip.assigned_to_asset.assigned_to or 'Unassigned'
                    label = getattr(ip, 'ip_label_from_junction', None)
                    if label:
                        ip.occupant_name = base_name
                        ip.ip_usage_label = label
                    else:
                        ip.occupant_name = base_name
                        ip.ip_usage_label = None
                elif hasattr(ip, 'manual_assignment') and ip.manual_assignment:
                    # Handle manual assignments
                    if ip.manual_assigned_vm:
                        ip.occupant_type = 'vm'
                        ip.occupant_name = ip.manual_assigned_vm.name
                    elif ip.manual_assigned_network_device:
                        ip.occupant_type = 'network_device'
                        ip.occupant_name = ip.manual_assigned_network_device.device_name
                    elif hasattr(ip, 'manual_assigned_testing_device') and ip.manual_assigned_testing_device:
                        ip.occupant_type = 'testing_device'
                        ip.occupant_name = f"{ip.manual_assigned_testing_device.device_name} ({ip.manual_assigned_testing_device.assigned_user or 'Unassigned'})"
                    elif ip.manual_assigned_asset:
                        ip.occupant_type = 'asset'
                        base_name = ip.manual_assigned_asset.assigned_to or 'Unassigned'
                        # Check for label from junction table
                        assoc = None
                        from assets.models import AssetIPAddress
                        assoc = AssetIPAddress.objects.filter(
                            manual_ip=ip.address,
                            asset=ip.manual_assigned_asset
                        ).first()
                        ip.occupant_name = base_name
                        ip.ip_usage_label = assoc.ip_label if assoc else None
                    else:
                        ip.occupant_type = 'free'
                        ip.occupant_name = None
                else:
                    ip.occupant_type = 'free'
                    ip.occupant_name = None
                
                # Add VM range classification
                ip_data['is_common_vm_range'] = IPManagementService.is_common_vm_range(ip)
                ip_data['is_rare_vm_range'] = IPManagementService.is_rare_vm_range(ip)
        
        context['ip_ranges'] = ip_ranges
        
        return context


class AssetFreeView(AdminRequiredMixin, CreateView):
    """Handle freeing assets (admin only)."""
    model = Asset
    template_name = 'assets/asset_free_confirm.html'
    success_url = reverse_lazy('freed_systems')
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """Get the asset to free."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Asset, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        """Add asset to context for display in confirmation dialog."""
        context = super().get_context_data(**kwargs)
        context['asset'] = self.get_object()
        return context

    def get(self, request, *args, **kwargs):
        """Display confirmation dialog and password prompt."""
        from .forms.asset_forms import FreeAssetForm
        asset = self.get_object()
        form = FreeAssetForm()
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })

    def post(self, request, *args, **kwargs):
        """Process POST with password verification."""
        from .forms.asset_forms import FreeAssetForm
        from django.urls import reverse
        
        asset = self.get_object()
        form = FreeAssetForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data['password']
            
            try:
                # Call AssetService.free_asset() with password
                freed_asset = AssetService.free_asset(asset, request.user, password)
                
                # Display success message
                messages.success(request, f'Asset {freed_asset.asset_tag} has been freed successfully.')
                
                # Redirect to freed systems page on success using reverse() for absolute path
                return redirect(reverse('freed_systems'))
                
            except ValidationError as e:
                # Handle incorrect password errors
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            if field == 'password':
                                messages.error(request, error)
                            form.add_error(field, error)
                else:
                    messages.error(request, str(e))
                    form.add_error(None, str(e))
            except Exception as e:
                # Handle unexpected errors
                messages.error(request, f'Error freeing asset: {str(e)}')
                form.add_error(None, str(e))
        else:
            messages.error(request, 'Please correct the errors below.')

        # Re-render form with errors
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })


class AssetScrapView(AdminRequiredMixin, CreateView):
    """Handle scrapping freed assets (admin only)."""
    model = Asset
    template_name = 'assets/asset_scrap_confirm.html'
    success_url = reverse_lazy('scrapped_items')
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        """Get the asset to scrap."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Asset, pk=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):
        """Add asset to context for display in confirmation dialog."""
        context = super().get_context_data(**kwargs)
        context['asset'] = self.get_object()
        return context

    def get(self, request, *args, **kwargs):
        """Display confirmation dialog."""
        asset = self.get_object()
        return render(request, self.template_name, {
            'asset': asset
        })

    def post(self, request, *args, **kwargs):
        """Process POST to scrap the asset."""
        asset = self.get_object()

        try:
            # Get scrapping_reason from POST data
            scrapping_reason = request.POST.get('scrapping_reason', '').strip()
            
            # Verify asset is freed before scrapping
            if asset.status != 'freed':
                messages.error(request, 'Only freed assets can be scrapped.')
                return redirect('freed_systems')

            # Call AssetService.scrap_asset() with scrapping_reason
            scrapped_asset = AssetService.scrap_asset(asset, request.user, scrapping_reason)

            # Display success message
            messages.success(request, f'Asset {scrapped_asset.asset_tag} has been scrapped successfully.')

            # Redirect to scrapped items page on success
            return redirect(self.success_url)

        except ValidationError as e:
            # Handle validation errors
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, error)
            else:
                messages.error(request, str(e))
            return redirect('freed_systems')
        except Exception as e:
            # Handle unexpected errors
            messages.error(request, f'Error scrapping asset: {str(e)}')
            return redirect('freed_systems')


class WarrantyView(LoginRequiredMixin, ListView):
    """Display all assets with warranty information."""
    model = Asset
    template_name = 'assets/warranty.html'
    context_object_name = 'assets'
    login_url = '/login/'

    def get_queryset(self):
        """Return all assets with warranty dates ordered by warranty_expiration ascending."""
        return Asset.objects.filter(
            warranty_expiration__isnull=False
        ).select_related(
            'operating_system', 'ip_address', 'team', 'team__parent'
        ).order_by('warranty_expiration')

    def get_context_data(self, **kwargs):
        """Add expiring_soon assets to context using WarrantyService."""
        from .services.warranty_service import WarrantyService
        from django.utils import timezone
        
        context = super().get_context_data(**kwargs)
        
        # Get assets expiring within 7 days for highlighting
        context['expiring_soon'] = WarrantyService.check_expiring_warranties()
        
        # Add today's date for expired check
        context['today'] = timezone.now().date()
        
        return context


class AssetImportView(AdminRequiredMixin, View):
    """Handle Excel file import for bulk asset creation (admin only)."""
    template_name = 'assets/asset_import.html'
    results_template_name = 'assets/asset_import_results.html'
    
    def get(self, request):
        """Display the import form or download template."""
        # Check if template download is requested
        if request.GET.get('download_template'):
            from django.http import FileResponse
            import os
            from django.conf import settings
            
            # Path to the sample template
            template_path = os.path.join(settings.MEDIA_ROOT, 'templates', 'sample_import_template.xlsx')
            
            # Check if file exists
            if os.path.exists(template_path):
                response = FileResponse(
                    open(template_path, 'rb'),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename="sample_import_template.xlsx"'
                return response
            else:
                messages.error(request, "Sample template file not found.")
        
        # Display the import form
        form = AssetImportForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        """Process the uploaded Excel file and import assets."""
        form = AssetImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Get the uploaded file
            file = request.FILES['file']
            
            # Initialize ImportService and process the file
            import_service = ImportService()
            result = import_service.import_assets(file, request.user)
            
            # Display success message if any assets were created or updated
            if result['created_count'] > 0 or result['updated_count'] > 0:
                messages.success(
                    request,
                    f"{result['created_count']} asset(s) created, {result['updated_count']} asset(s) updated."
                )
            
            # Display warning message if there were errors
            if result['error_count'] > 0:
                messages.warning(
                    request,
                    f"{result['error_count']} row(s) had errors and were not imported."
                )
            
            # Store results in session for the results page
            request.session['import_results'] = {
                'created_count': result['created_count'],
                'updated_count': result['updated_count'],
                'error_count': result['error_count'],
                'errors': result['errors']
            }
            
            # Redirect to the results page
            return redirect('asset_import_results')
        
        # Form validation failed, re-display form with errors
        return render(request, self.template_name, {'form': form})


class AssetImportResultsView(AdminRequiredMixin, View):
    """Display import results from session."""
    template_name = 'assets/asset_import_results.html'
    
    def get(self, request):
        """Display the import results stored in session."""
        # Retrieve results from session
        import_results = request.session.get('import_results', None)
        
        # If no results in session, redirect to import page
        if import_results is None:
            messages.info(request, "No import results to display.")
            return redirect('asset_import')
        
        # Clear the results from session after retrieving
        del request.session['import_results']
        
        return render(request, self.template_name, {
            'created_count': import_results['created_count'],
            'updated_count': import_results['updated_count'],
            'error_count': import_results['error_count'],
            'errors': import_results['errors']
        })


class AssetExportActiveView(LoginRequiredMixin, View):
    """Export active assets to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with active assets."""
        export_service = ExportService()
        return export_service.export_active_assets()


class AssetExportFreedView(LoginRequiredMixin, View):
    """Export freed assets to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with freed assets."""
        export_service = ExportService()
        return export_service.export_freed_assets()


class AssetExportScrappedView(LoginRequiredMixin, View):
    """Export scrapped assets to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with scrapped assets."""
        export_service = ExportService()
        return export_service.export_scrapped_assets()


class FreeIPsExportView(LoginRequiredMixin, View):
    """Export free IP addresses to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with free IP addresses."""
        export_service = ExportService()
        return export_service.export_free_ips()


class NetworkDeviceExportView(LoginRequiredMixin, View):
    """Export network devices to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with network devices."""
        export_service = ExportService()
        return export_service.export_network_devices()


class HyperVVMExportView(LoginRequiredMixin, View):
    """Export Hyper-V VMs to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with Hyper-V VMs."""
        export_service = ExportService()
        return export_service.export_hyperv_vms()


class GetSubTeamsView(LoginRequiredMixin, View):
    """API endpoint to get sub-teams for a parent team."""
    login_url = '/login/'
    
    def get(self, request):
        """Return sub-teams as JSON for the given parent team ID."""
        from django.http import JsonResponse
        
        parent_id = request.GET.get('parent_id')
        
        if not parent_id:
            return JsonResponse({'sub_teams': []})
        
        try:
            parent_team = Team.objects.get(pk=parent_id)
            sub_teams = parent_team.sub_teams.all().order_by('name')
            
            sub_teams_data = [
                {'id': sub.id, 'name': sub.name}
                for sub in sub_teams
            ]
            
            return JsonResponse({
                'sub_teams': sub_teams_data,
                'has_sub_teams': len(sub_teams_data) > 0
            })
        except Team.DoesNotExist:
            return JsonResponse({'sub_teams': [], 'has_sub_teams': False})



class OperatingSystemListView(AdminRequiredMixin, ListView):
    """Display all operating systems with management options."""
    model = OperatingSystem
    template_name = 'assets/operating_systems.html'
    context_object_name = 'operating_systems'
    login_url = '/login/'
    
    def get_queryset(self):
        """Return all operating systems ordered by name."""
        from .models import OperatingSystem
        return OperatingSystem.objects.all().order_by('name')


class AddOperatingSystemView(AdminRequiredMixin, View):
    """Add a new operating system."""
    login_url = '/login/'
    
    def post(self, request):
        """Handle POST request to add new OS."""
        from .models import OperatingSystem
        
        os_name = request.POST.get('os_name', '').strip()
        
        if not os_name:
            messages.error(request, 'Operating system name is required.')
            return redirect('operating_systems')
        
        # Check if OS already exists
        if OperatingSystem.objects.filter(name=os_name).exists():
            messages.error(request, f'Operating system "{os_name}" already exists.')
            return redirect('operating_systems')
        
        # Create new OS
        OperatingSystem.objects.create(name=os_name)
        messages.success(request, f'Operating system "{os_name}" added successfully.')
        
        return redirect('operating_systems')


class EditOperatingSystemView(AdminRequiredMixin, View):
    """Edit an existing operating system."""
    login_url = '/login/'
    
    def post(self, request, pk):
        """Handle POST request to edit OS."""
        from .models import OperatingSystem
        from django.shortcuts import get_object_or_404
        
        os_obj = get_object_or_404(OperatingSystem, pk=pk)
        os_name = request.POST.get('os_name', '').strip()
        
        if not os_name:
            messages.error(request, 'Operating system name is required.')
            return redirect('operating_systems')
        
        # Check if new name already exists (excluding current OS)
        if OperatingSystem.objects.filter(name=os_name).exclude(pk=pk).exists():
            messages.error(request, f'Operating system "{os_name}" already exists.')
            return redirect('operating_systems')
        
        # Update OS name
        old_name = os_obj.name
        os_obj.name = os_name
        os_obj.save()
        
        messages.success(request, f'Operating system updated from "{old_name}" to "{os_name}".')
        
        return redirect('operating_systems')


class DeleteOperatingSystemView(AdminRequiredMixin, View):
    """Delete an operating system."""
    login_url = '/login/'
    
    def post(self, request, pk):
        """Handle POST request to delete OS."""
        from .models import OperatingSystem
        from django.shortcuts import get_object_or_404
        
        os_obj = get_object_or_404(OperatingSystem, pk=pk)
        
        # Check if OS is in use
        if os_obj.assets.exists():
            messages.error(request, f'Cannot delete "{os_obj.name}" - it is in use by {os_obj.assets.count()} asset(s).')
            return redirect('operating_systems')
        
        # Delete OS
        os_name = os_obj.name
        os_obj.delete()
        
        messages.success(request, f'Operating system "{os_name}" deleted successfully.')
        
        return redirect('operating_systems')



class FreedSystemCreateView(AdminRequiredMixin, CreateView):
    """Handle manual freed system creation (admin only)."""
    model = Asset
    template_name = 'assets/freed_system_create.html'
    success_url = reverse_lazy('freed_systems')
    
    def get_form_class(self):
        from .forms.freed_system_forms import FreedSystemForm
        return FreedSystemForm
    
    def form_valid(self, form):
        """Process form submission using AssetService.create_freed_asset()."""
        try:
            asset = AssetService.create_freed_asset(
                form.cleaned_data,
                self.request.user
            )
            messages.success(
                self.request,
                f'Freed system {asset.asset_tag} created successfully.'
            )
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating freed system: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class FreedSystemDeleteView(AdminRequiredMixin, View):
    """Handle freed system deletion with password confirmation (admin only)."""
    template_name = 'assets/freed_system_confirm_delete.html'
    
    def get(self, request, pk):
        """Display confirmation dialog with password prompt."""
        from django.shortcuts import get_object_or_404, render
        from .forms.team_forms import DeleteTeamForm  # Reuse the password form
        
        asset = get_object_or_404(Asset, pk=pk, status='freed')
        form = DeleteTeamForm()
        
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })
    
    def post(self, request, pk):
        """Process freed system deletion with password verification."""
        from django.shortcuts import get_object_or_404
        from django.contrib.auth.hashers import check_password
        from .forms.team_forms import DeleteTeamForm
        
        asset = get_object_or_404(Asset, pk=pk, status='freed')
        form = DeleteTeamForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            
            # Verify user password
            if not check_password(password, request.user.password):
                messages.error(request, 'Incorrect password.')
                return render(request, self.template_name, {
                    'asset': asset,
                    'form': form
                })
            
            # Release IP if assigned
            if asset.ip_address:
                from .services.ip_management_service import IPManagementService
                IPManagementService.release_ip(asset.ip_address)
            
            # Store asset tag for success message
            asset_tag = asset.asset_tag
            
            # Delete the asset
            asset.delete()
            
            messages.success(request, f'Freed system "{asset_tag}" deleted successfully.')
            return redirect('freed_systems')
        
        # Form validation failed
        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })


class FreedSystemEditView(AdminRequiredMixin, CreateView):
    """Handle freed system health status updates (admin only)."""
    model = Asset
    template_name = 'assets/freed_system_edit.html'
    success_url = reverse_lazy('freed_systems')
    pk_url_kwarg = 'pk'
    
    def get_form_class(self):
        from .forms.freed_system_forms import FreedSystemEditForm
        return FreedSystemEditForm
    
    def get_object(self, queryset=None):
        """Get the freed asset to edit."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Asset, pk=self.kwargs.get(self.pk_url_kwarg), status='freed')
    
    def get_form_kwargs(self):
        """Pass the asset instance to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add asset to context."""
        context = super().get_context_data(**kwargs)
        context['asset'] = self.get_object()
        return context
    
    def form_valid(self, form):
        """Process form submission using AssetService.update_freed_asset()."""
        try:
            asset = self.get_object()
            updated_asset = AssetService.update_freed_asset(
                asset,
                form.cleaned_data,
                self.request.user
            )
            messages.success(
                self.request,
                f'Freed system {updated_asset.asset_tag} updated successfully.'
            )
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error updating freed system: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class AssetReassignView(AdminRequiredMixin, View):
    """Handle reassignment of freed assets back to active status (admin only)."""
    template_name = 'assets/asset_reassign_form.html'
    success_url = reverse_lazy('asset_list')
    
    def get(self, request, pk):
        """Display reassignment form for freed asset."""
        from django.shortcuts import get_object_or_404
        from .forms.asset_forms import ReassignmentForm
        
        # Get the asset
        asset = get_object_or_404(Asset, pk=pk)
        
        # Verify asset is freed
        if asset.status != 'freed':
            messages.error(request, 'Only freed assets can be reassigned.')
            return redirect('freed_systems')
        
        # Verify asset is healthy
        if asset.health_status != 'healthy':
            messages.error(request, 'Only healthy freed assets can be reassigned.')
            return redirect('freed_systems')
        
        # Create form with asset data
        form = ReassignmentForm(asset=asset)
        
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })
    
    def post(self, request, pk):
        """Process reassignment submission."""
        from django.shortcuts import get_object_or_404
        from .forms.asset_forms import ReassignmentForm
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info(f"=== REASSIGNMENT POST REQUEST ===")
        logger.info(f"Asset PK: {pk}")
        logger.info(f"POST data: {request.POST}")
        
        # Get the asset
        asset = get_object_or_404(Asset, pk=pk)
        logger.info(f"Asset: {asset.asset_tag}, Status: {asset.status}, Health: {asset.health_status}")
        
        # Verify asset is freed
        if asset.status != 'freed':
            messages.error(request, 'Only freed assets can be reassigned.')
            logger.error(f"Asset {asset.asset_tag} is not freed (status={asset.status})")
            return redirect('freed_systems')
        
        # Verify asset is healthy
        if asset.health_status != 'healthy':
            messages.error(request, 'Only healthy freed assets can be reassigned.')
            logger.error(f"Asset {asset.asset_tag} is not healthy (health={asset.health_status})")
            return redirect('freed_systems')
        
        # Create form with POST data
        form = ReassignmentForm(request.POST, asset=asset)
        logger.info(f"Form is_valid: {form.is_valid()}")
        
        if not form.is_valid():
            logger.error(f"Form errors: {form.errors}")
            messages.error(request, 'Please correct the errors below.')
            return render(request, self.template_name, {
                'asset': asset,
                'form': form
            })
        
        try:
            # Check if manual OS entry was provided
            os_manual_entry = request.POST.get('os_manual_entry', '').strip()
            logger.info(f"OS manual entry: '{os_manual_entry}'")
            
            if os_manual_entry:
                os_obj, created = OperatingSystem.objects.get_or_create(name=os_manual_entry)
                operating_system_id = os_obj.id
                logger.info(f"Created/found OS: {os_obj.name} (id={os_obj.id})")
            else:
                operating_system_id = form.cleaned_data['operating_system'].id if form.cleaned_data.get('operating_system') else None
                logger.info(f"Using OS from dropdown: {operating_system_id}")
            
            # Prepare data dictionary (only manual_ip now, no dropdown)
            data = {
                'assigned_to': form.cleaned_data['assigned_to'],
                'team': form.cleaned_data['team'].id,
                'ip_address_id': None,  # No longer using dropdown
                'manual_ip': form.cleaned_data.get('manual_ip'),
                'operating_system': operating_system_id,
                'system_type': form.cleaned_data['system_type'],
                'manufacturer': form.cleaned_data.get('manufacturer', ''),
                'particulars': form.cleaned_data.get('particulars', ''),
                'warranty_expiration': form.cleaned_data.get('warranty_expiration'),
            }
            logger.info(f"Reassignment data: {data}")
            
            # Call service method
            reassigned_asset = AssetService.reassign_asset(asset, data, request.user)
            logger.info(f"Asset reassigned successfully: {reassigned_asset.asset_tag}")
            
            # Display success message
            messages.success(request, f'Asset {reassigned_asset.asset_tag} has been reassigned and is now active.')
            
            # Redirect to active assets page
            return redirect(self.success_url)
            
        except ValidationError as e:
            # Handle validation errors
            logger.error(f"ValidationError: {e}")
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                        logger.error(f"Field error - {field}: {error}")
            else:
                form.add_error(None, str(e))
                logger.error(f"General error: {str(e)}")
        except Exception as e:
            # Handle unexpected errors
            logger.exception(f"Unexpected error: {str(e)}")
            messages.error(request, f'Error reassigning asset: {str(e)}')
            form.add_error(None, str(e))
        
        # Re-render form with errors
        return render(request, self.template_name, {
            'asset': asset,
            'form': form
        })



class NetworkDeviceListView(AdminRequiredMixin, ListView):
    """Display all network devices."""
    template_name = 'assets/network_device_list.html'
    context_object_name = 'devices'
    login_url = '/login/'
    
    def get_queryset(self):
        from assets.models import NetworkDevice
        from .forms.network_device_filter_form import NetworkDeviceFilterForm
        from django.db.models import Q
        
        queryset = NetworkDevice.objects.select_related('ip_address').order_by('device_name')
        
        # Initialize filter form with GET parameters
        filter_form = NetworkDeviceFilterForm(self.request.GET)
        
        # Apply filters if form is valid
        if filter_form.is_valid():
            # Apply device name filter
            device_name = filter_form.cleaned_data.get('device_name', '').strip()
            if device_name:
                queryset = queryset.filter(device_name__icontains=device_name)
            
            # Apply IP address filter
            ip_address = filter_form.cleaned_data.get('ip_address', '').strip()
            if ip_address:
                queryset = queryset.filter(
                    Q(ip_address__address__icontains=ip_address) |
                    Q(manual_ip__icontains=ip_address)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        from .forms.network_device_filter_form import NetworkDeviceFilterForm
        
        context = super().get_context_data(**kwargs)
        
        # Initialize filter form with GET parameters to preserve filter values
        context['filter_form'] = NetworkDeviceFilterForm(self.request.GET)
        
        return context

class NetworkDeviceCreateView(AdminRequiredMixin, CreateView):
    """Create new network device."""
    template_name = 'assets/network_device_form.html'
    success_url = reverse_lazy('network_device_list')
    login_url = '/login/'
    
    def get_form_class(self):
        from assets.forms.asset_forms import NetworkDeviceForm
        return NetworkDeviceForm
    
    def form_valid(self, form):
        from assets.services.network_device_service import NetworkDeviceService
        
        try:
            data = {
                'device_type': form.cleaned_data['device_type'],
                'device_name': form.cleaned_data['device_name'],
                'ip_address_id': form.cleaned_data['ip_address'].id if form.cleaned_data.get('ip_address') else None,
                'manual_ip': form.cleaned_data.get('manual_ip')
            }
            device = NetworkDeviceService.create_network_device(data, self.request.user)
            messages.success(self.request, f'Network device {device.device_name} created successfully.')
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class NetworkDeviceUpdateView(AdminRequiredMixin, View):
    """Update existing network device."""
    template_name = 'assets/network_device_form.html'
    success_url = reverse_lazy('network_device_list')
    login_url = '/login/'
    
    def get_object(self, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import NetworkDevice
        return get_object_or_404(NetworkDevice, pk=pk)
    
    def get(self, request, pk):
        from assets.forms.asset_forms import NetworkDeviceForm
        device = self.get_object(pk)
        form = NetworkDeviceForm(instance=device)
        return render(request, self.template_name, {'form': form, 'device': device})
    
    def post(self, request, pk):
        from assets.forms.asset_forms import NetworkDeviceForm
        from assets.services.network_device_service import NetworkDeviceService
        
        device = self.get_object(pk)
        form = NetworkDeviceForm(request.POST, instance=device)
        
        if form.is_valid():
            try:
                data = {
                    'device_type': form.cleaned_data['device_type'],
                    'device_name': form.cleaned_data['device_name'],
                    'ip_address_id': form.cleaned_data['ip_address'].id if form.cleaned_data.get('ip_address') else None,
                    'manual_ip': form.cleaned_data.get('manual_ip')
                }
                updated_device = NetworkDeviceService.update_network_device(device, data, request.user)
                messages.success(request, f'Network device {updated_device.device_name} updated successfully.')
                return redirect(self.success_url)
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field, error)
                else:
                    form.add_error(None, str(e))
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, self.template_name, {'form': form, 'device': device})


class NetworkDeviceDeleteView(AdminRequiredMixin, View):
    """Delete network device with confirmation."""
    login_url = '/login/'
    
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import NetworkDevice
        device = get_object_or_404(NetworkDevice, pk=pk)
        return render(request, 'assets/network_device_confirm_delete.html', {'device': device})
    
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import NetworkDevice
        from assets.services.network_device_service import NetworkDeviceService
        
        device = get_object_or_404(NetworkDevice, pk=pk)
        device_name = device.device_name
        NetworkDeviceService.delete_network_device(device, request.user)
        messages.success(request, f'Network device {device_name} deleted successfully.')
        return redirect('network_device_list')


class NetworkDeviceExportView(LoginRequiredMixin, View):
    """Export network devices to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with network devices."""
        export_service = ExportService()
        return export_service.export_network_devices()


# Testing Device Views

class TestingDeviceListView(AdminRequiredMixin, ListView):
    """Display all testing devices."""
    template_name = 'assets/testing_device_list.html'
    context_object_name = 'devices'
    login_url = '/login/'
    
    def get_queryset(self):
        from assets.models import TestingDevice
        from .forms.testing_device_forms import TestingDeviceFilterForm
        from django.db.models import Q
        
        queryset = TestingDevice.objects.select_related('ip_address').order_by('device_name')
        
        # Initialize filter form with GET parameters
        filter_form = TestingDeviceFilterForm(self.request.GET)
        
        # Apply filters if form is valid
        if filter_form.is_valid():
            # Apply device name filter
            device_name = filter_form.cleaned_data.get('device_name', '').strip()
            if device_name:
                queryset = queryset.filter(device_name__icontains=device_name)
            
            # Apply assigned user filter
            assigned_user = filter_form.cleaned_data.get('assigned_user', '').strip()
            if assigned_user:
                queryset = queryset.filter(assigned_user__icontains=assigned_user)
            
            # Apply IP address filter
            ip_address = filter_form.cleaned_data.get('ip_address', '').strip()
            if ip_address:
                queryset = queryset.filter(
                    Q(ip_address__address__icontains=ip_address) |
                    Q(manual_ip__icontains=ip_address)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add filter form to context."""
        from .forms.testing_device_forms import TestingDeviceFilterForm
        
        context = super().get_context_data(**kwargs)
        
        # Initialize filter form with GET parameters to preserve filter values
        context['filter_form'] = TestingDeviceFilterForm(self.request.GET)
        
        return context


class TestingDeviceCreateView(AdminRequiredMixin, CreateView):
    """Create new testing device."""
    template_name = 'assets/testing_device_form.html'
    success_url = reverse_lazy('testing_device_list')
    
    def get_form_class(self):
        from .forms.testing_device_forms import TestingDeviceForm
        return TestingDeviceForm
    
    def form_valid(self, form):
        """Process form submission."""
        try:
            device = form.save(commit=False)
            
            # Handle manual IP entry
            ip_manual_entry = self.request.POST.get('ip_manual_entry', '').strip()
            if ip_manual_entry:
                device.manual_ip = ip_manual_entry
                device.ip_address = None
            elif device.ip_address:
                device.manual_ip = None
                # Mark IP as assigned
                device.ip_address.is_assigned = True
                device.ip_address.save()
            
            device.save()
            
            messages.success(self.request, f'Testing device "{device.device_name}" created successfully.')
            return redirect(self.success_url)
            
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Error creating testing device: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TestingDeviceUpdateView(AdminRequiredMixin, View):
    """Update existing testing device."""
    template_name = 'assets/testing_device_form.html'
    
    def get(self, request, pk):
        """Display update form."""
        from django.shortcuts import get_object_or_404, render
        from assets.models import TestingDevice
        from .forms.testing_device_forms import TestingDeviceForm
        
        device = get_object_or_404(TestingDevice, pk=pk)
        form = TestingDeviceForm(instance=device)
        
        return render(request, self.template_name, {
            'form': form,
            'device': device,
            'is_edit': True
        })
    
    def post(self, request, pk):
        """Process update form submission."""
        from django.shortcuts import get_object_or_404, render
        from assets.models import TestingDevice
        from .forms.testing_device_forms import TestingDeviceForm
        
        device = get_object_or_404(TestingDevice, pk=pk)
        form = TestingDeviceForm(request.POST, instance=device)
        
        if form.is_valid():
            try:
                old_ip = device.ip_address
                
                # Handle manual IP entry
                ip_manual_entry = request.POST.get('ip_manual_entry', '').strip()
                if ip_manual_entry:
                    device.manual_ip = ip_manual_entry
                    device.ip_address = None
                elif form.cleaned_data.get('ip_address'):
                    device.manual_ip = None
                    device.ip_address = form.cleaned_data['ip_address']
                    # Mark new IP as assigned
                    device.ip_address.is_assigned = True
                    device.ip_address.save()
                
                device.device_name = form.cleaned_data['device_name']
                device.assigned_user = form.cleaned_data.get('assigned_user', '')
                device.save()
                
                # Free old IP if changed
                if old_ip and old_ip != device.ip_address:
                    old_ip.is_assigned = False
                    old_ip.save()
                
                messages.success(request, f'Testing device "{device.device_name}" updated successfully.')
                return redirect('testing_device_list')
                
            except ValidationError as e:
                if hasattr(e, 'message_dict'):
                    for field, errors in e.message_dict.items():
                        for error in errors:
                            form.add_error(field, error)
                else:
                    form.add_error(None, str(e))
            except Exception as e:
                messages.error(request, f'Error updating testing device: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
        
        return render(request, self.template_name, {
            'form': form,
            'device': device,
            'is_edit': True
        })


class TestingDeviceDeleteView(AdminRequiredMixin, View):
    """Delete testing device with confirmation."""
    login_url = '/login/'
    
    def get(self, request, pk):
        """Display confirmation dialog."""
        from django.shortcuts import get_object_or_404, render
        from assets.models import TestingDevice
        
        device = get_object_or_404(TestingDevice, pk=pk)
        return render(request, 'assets/testing_device_confirm_delete.html', {'device': device})
    
    def post(self, request, pk):
        """Process deletion."""
        from django.shortcuts import get_object_or_404
        from assets.models import TestingDevice
        
        device = get_object_or_404(TestingDevice, pk=pk)
        device_name = device.device_name
        
        # Free the IP address if it was managed
        if device.ip_address:
            device.ip_address.is_assigned = False
            device.ip_address.save()
        
        device.delete()
        
        messages.success(request, f'Testing device "{device_name}" deleted successfully.')
        return redirect('testing_device_list')


class TestingDeviceExportView(LoginRequiredMixin, View):
    """Export testing devices to Excel file."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with testing devices."""
        from assets.models import TestingDevice
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from django.http import HttpResponse
        from datetime import datetime
        
        # Create workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Testing Devices'
        
        # Add headers
        headers = ['Device Name', 'Assigned User', 'IP Address']
        ws.append(headers)
        
        # Style headers
        for cell in ws[1]:
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Add data
        devices = TestingDevice.objects.select_related('ip_address').order_by('device_name')
        for device in devices:
            ws.append([
                device.device_name,
                device.assigned_user or '',
                device.get_ip_address() or ''
            ])
        
        # Adjust column widths
        ws.column_dimensions['A'].width = 30
        ws.column_dimensions['B'].width = 25
        ws.column_dimensions['C'].width = 20
        
        # Create response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f'testing_devices_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        wb.save(response)
        return response


# Hyper-V VM Views

class HyperVVMListView(LoginRequiredMixin, ListView):
    """Display all Hyper-V VMs."""
    model = HyperVVM
    template_name = 'assets/hyperv_vm_list.html'
    context_object_name = 'vms'
    login_url = '/login/'
    
    def get_queryset(self):
        """Return active VMs with related data."""
        from assets.models import HyperVVM
        queryset = HyperVVM.objects.filter(
            is_active=True
        ).select_related(
            'host_machine',
            'host_machine__ip_address',
            'ip_address'
        ).order_by('name')
        
        # Apply search filter
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        
        # Apply host filter
        host_filter = self.request.GET.get('host', '')
        if host_filter:
            queryset = queryset.filter(host_machine_id=host_filter)
        
        # Apply IP range filter
        range_filter = self.request.GET.get('range', '')
        if range_filter:
            queryset = queryset.filter(ip_address__ip_range__range_pattern=range_filter)
        
        # Apply IP address filter
        ip_filter = self.request.GET.get('ip', '')
        if ip_filter:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(ip_address__address__icontains=ip_filter) | 
                Q(manual_ip__icontains=ip_filter)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['filter_host'] = self.request.GET.get('host', '')
        context['filter_range'] = self.request.GET.get('range', '')
        context['filter_ip'] = self.request.GET.get('ip', '')
        context['vm_count'] = self.get_queryset().count()
        
        # Get available hosts for filter dropdown
        from assets.models import Asset
        context['available_hosts'] = Asset.objects.filter(
            status='active',
            hosted_vms__isnull=False
        ).distinct().select_related('ip_address')
        
        # Get available IP ranges for filter dropdown
        from assets.models import IPRange
        context['available_ranges'] = IPRange.objects.all()
        
        return context


class HyperVVMCreateView(AdminRequiredMixin, CreateView):
    """Handle VM creation (admin only)."""
    from assets.models import HyperVVM
    from assets.forms.hyperv_forms import HyperVVMForm
    
    model = HyperVVM
    form_class = HyperVVMForm
    template_name = 'assets/hyperv_vm_form.html'
    success_url = reverse_lazy('hyperv_vm_list')
    login_url = '/login/'
    
    def form_valid(self, form):
        from assets.services.hyperv_service import HyperVService
        try:
            vm = HyperVService.create_vm(
                form.cleaned_data,
                self.request.user
            )
            messages.success(
                self.request,
                f'VM {vm.name} created successfully.'
            )
            return redirect(self.success_url)
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    form.add_error(field, error)
            return self.form_invalid(form)


class HyperVVMUpdateView(AdminRequiredMixin, View):
    """Handle VM updates (admin only)."""
    login_url = '/login/'
    
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import HyperVVM
        from assets.forms.hyperv_forms import HyperVVMForm
        
        vm = get_object_or_404(HyperVVM, pk=pk)
        form = HyperVVMForm(instance=vm)
        return render(request, 'assets/hyperv_vm_form.html', {'form': form, 'vm': vm})
    
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import HyperVVM
        from assets.forms.hyperv_forms import HyperVVMForm
        from assets.services.hyperv_service import HyperVService
        
        vm = get_object_or_404(HyperVVM, pk=pk)
        form = HyperVVMForm(request.POST, instance=vm)
        
        if form.is_valid():
            try:
                updated_vm = HyperVService.update_vm(
                    vm,
                    form.cleaned_data,
                    request.user
                )
                messages.success(request, f'VM {updated_vm.name} updated successfully.')
                return redirect('hyperv_vm_list')
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
        
        return render(request, 'assets/hyperv_vm_form.html', {'form': form, 'vm': vm})


class HyperVVMDetailView(LoginRequiredMixin, View):
    """Display VM details with host machine information."""
    login_url = '/login/'
    
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import HyperVVM
        
        vm = get_object_or_404(
            HyperVVM.objects.select_related(
                'host_machine',
                'host_machine__ip_address',
                'ip_address'
            ),
            pk=pk
        )
        return render(request, 'assets/hyperv_vm_detail.html', {'vm': vm})


class HyperVVMDeleteView(AdminRequiredMixin, View):
    """Handle VM deletion (admin only)."""
    login_url = '/login/'
    
    def get(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import HyperVVM
        
        vm = get_object_or_404(HyperVVM, pk=pk)
        return render(request, 'assets/hyperv_vm_confirm_delete.html', {'vm': vm})
    
    def post(self, request, pk):
        from django.shortcuts import get_object_or_404
        from assets.models import HyperVVM
        from assets.services.hyperv_service import HyperVService
        
        vm = get_object_or_404(HyperVVM, pk=pk)
        vm_name = vm.name
        try:
            HyperVService.delete_vm(vm, request.user)
            messages.success(request, f'VM {vm_name} deleted successfully.')
        except Exception as e:
            messages.error(request, f'Error deleting VM: {str(e)}')
        
        return redirect('hyperv_vm_list')



class QuickVMCreateView(AdminRequiredMixin, View):
    """Handle quick VM creation from Free IP page via AJAX."""
    login_url = '/login/'
    
    def post(self, request):
        """
        Process VM creation request.
        
        Expected POST data:
        - vm_ip: str (IP address for the VM)
        - base_machine_ip: str (IP address of host machine)
        - vm_name: str (optional, auto-generated if empty)
        
        Returns:
        - JSON response with success/error status
        """
        try:
            # Extract POST data
            vm_ip = request.POST.get('vm_ip', '').strip()
            base_machine_ip = request.POST.get('base_machine_ip', '').strip()
            vm_name = request.POST.get('vm_name', '').strip()
            
            # Validate required fields
            if not vm_ip:
                return JsonResponse({
                    'success': False,
                    'error': 'VM IP address is required',
                    'field_errors': {'vm_ip': ['This field is required']}
                }, status=400)
            
            if not base_machine_ip:
                return JsonResponse({
                    'success': False,
                    'error': 'Base Machine IP address is required',
                    'field_errors': {'base_machine_ip': ['This field is required']}
                }, status=400)
            
            # Validate IPv4 format
            ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ipv4_pattern, vm_ip):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid VM IP address format',
                    'field_errors': {'vm_ip': ['Please enter a valid IPv4 address']}
                }, status=400)
            
            if not re.match(ipv4_pattern, base_machine_ip):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid Base Machine IP address format',
                    'field_errors': {'base_machine_ip': ['Please enter a valid IPv4 address']}
                }, status=400)
            
            # Look up base machine
            base_machine = self._lookup_base_machine(base_machine_ip)
            if not base_machine:
                return JsonResponse({
                    'success': False,
                    'error': 'No base machine found with that IP address',
                    'field_errors': {'base_machine_ip': ['No base machine found with this IP address']}
                }, status=400)
            
            # Determine VM IP type (managed or manual)
            is_managed, ip_obj = self._determine_vm_ip_type(vm_ip)
            
            # Generate default VM name if not provided
            if not vm_name:
                vm_name = self._generate_default_vm_name(base_machine, vm_ip)
            
            # Prepare data for HyperVService
            data = {
                'name': vm_name,
                'host_machine': base_machine,
                'notes': ''
            }
            
            if is_managed:
                data['ip_address'] = ip_obj
            else:
                data['manual_ip'] = vm_ip
            
            # Create VM using HyperVService
            vm = HyperVService.create_vm(data, request.user)
            
            return JsonResponse({
                'success': True,
                'message': 'VM created successfully',
                'vm_id': vm.pk,
                'vm_name': vm.name
            })
            
        except ValidationError as e:
            # Handle validation errors from service layer
            error_message = str(e)
            field_errors = {}
            
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    field_errors[field] = errors
                error_message = 'Validation error occurred'
            
            return JsonResponse({
                'success': False,
                'error': error_message,
                'field_errors': field_errors
            }, status=400)
            
        except Exception as e:
            # Handle unexpected errors
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)
    
    def _lookup_base_machine(self, ip_address_str):
        """
        Look up Asset by IP address.
        
        Search order:
        1. IPAddress.assigned_to_asset (managed IP in pool)
        2. Asset.manual_ip (old manual IP field)
        3. AssetIPAddress junction table (managed IP FK)
        4. AssetIPAddress junction table (manual IP text match)
        
        Returns:
            Asset instance or None
        """
        from assets.models import AssetIPAddress
        
        # Try managed IP from pool first
        try:
            ip_obj = IPAddress.objects.get(address=ip_address_str)
            if ip_obj.assigned_to_asset:
                return ip_obj.assigned_to_asset
        except IPAddress.DoesNotExist:
            pass
        
        # Try old manual IP field on Asset
        asset = Asset.objects.filter(
            manual_ip=ip_address_str,
            status='active'
        ).first()
        if asset:
            return asset
        
        # Try AssetIPAddress junction table (managed IP)
        try:
            ip_obj = IPAddress.objects.get(address=ip_address_str)
            assoc = AssetIPAddress.objects.filter(
                ip_address=ip_obj,
                asset__status='active'
            ).select_related('asset').first()
            if assoc:
                return assoc.asset
        except IPAddress.DoesNotExist:
            pass
        
        # Try AssetIPAddress junction table (manual IP)
        assoc = AssetIPAddress.objects.filter(
            manual_ip=ip_address_str,
            asset__status='active'
        ).select_related('asset').first()
        if assoc:
            return assoc.asset
        
        return None
    
    def _determine_vm_ip_type(self, vm_ip_str):
        """
        Determine if VM IP is managed or manual.
        
        Returns:
            tuple: (is_managed: bool, ip_obj: IPAddress or None)
        """
        try:
            ip_obj = IPAddress.objects.get(address=vm_ip_str)
            if ip_obj.is_assigned:
                # Check what it's assigned to for better error message
                from assets.models import NetworkDevice
                
                # Check if assigned to network device
                if hasattr(ip_obj, 'network_device') and ip_obj.network_device is not None:
                    raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to a network device']})
                
                # Check if assigned to asset
                if ip_obj.assigned_to_asset:
                    raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to an active asset']})
                
                # Check if assigned to VM
                vm_queryset = ip_obj.vm.all()
                if vm_queryset.exists():
                    raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to another VM']})
                
                # Generic fallback
                raise ValidationError({'vm_ip': ['This IP address is already assigned']})
            return (True, ip_obj)
        except IPAddress.DoesNotExist:
            # Manual IP - need to check if it's used elsewhere
            # Check if used by active asset
            if Asset.objects.filter(manual_ip=vm_ip_str, status='active').exists():
                raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to an active asset']})
            
            # Check if used by network device
            from assets.models import NetworkDevice
            if NetworkDevice.objects.filter(ip_address__address=vm_ip_str).exists():
                raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to a network device']})
            
            # Check if used by another VM
            if HyperVVM.objects.filter(manual_ip=vm_ip_str, is_active=True).exists():
                raise ValidationError({'vm_ip': ['IP conflict: This IP is already assigned to another VM']})
            
            return (False, None)
    
    def _generate_default_vm_name(self, base_machine, vm_ip):
        """
        Generate default VM name in format: VM-{asset_tag}-{vm_ip}
        
        Args:
            base_machine: Asset instance
            vm_ip: IP address string
        
        Returns:
            str: Generated VM name
        """
        return f"VM-{base_machine.asset_tag}-{vm_ip}"



class DeleteAttachmentView(AdminRequiredMixin, View):
    """Delete an attachment from an asset."""
    login_url = '/login/'
    
    def post(self, request, pk):
        """Handle POST request to delete attachment."""
        from django.shortcuts import get_object_or_404
        from .models import Attachment
        from .services.attachment_service import AttachmentService
        
        attachment = get_object_or_404(Attachment, pk=pk)
        asset = attachment.asset
        filename = attachment.filename
        
        # Delete attachment using service
        AttachmentService.delete_attachment(attachment)
        
        messages.success(request, f'Attachment "{filename}" deleted successfully.')
        
        # Redirect back to asset edit page
        return redirect('asset_update', pk=asset.pk)


# Asset History Views

class AssetHistoryView(LoginRequiredMixin, ListView):
    """Display asset history timeline with filtering and pagination."""
    model = Asset
    template_name = 'assets/asset_history.html'
    context_object_name = 'history_entries'
    login_url = '/login/'
    paginate_by = 50
    
    def get_asset(self):
        """Get the asset whose history is being viewed."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Asset, pk=self.kwargs.get('pk'))
    
    def get_queryset(self):
        """Return history entries for the asset with optional filtering."""
        from .services.history_service import HistoryService
        from .models import AssetHistory
        
        asset = self.get_asset()
        
        # Build filters dictionary from request parameters
        filters = {}
        
        event_type = self.request.GET.get('event_type', '').strip()
        if event_type:
            filters['event_type'] = event_type
        
        user = self.request.GET.get('user', '').strip()
        if user:
            filters['user'] = user
        
        date_from = self.request.GET.get('date_from', '').strip()
        if date_from:
            from datetime import datetime
            try:
                filters['date_from'] = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                pass
        
        date_to = self.request.GET.get('date_to', '').strip()
        if date_to:
            from datetime import datetime
            try:
                filters['date_to'] = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Get filtered history using HistoryService
        if filters:
            return HistoryService.get_asset_history(asset, filters)
        else:
            return HistoryService.get_asset_history(asset)
    
    def get_context_data(self, **kwargs):
        """Add asset, event types, and active filters to context."""
        from .models import AssetHistory
        
        context = super().get_context_data(**kwargs)
        
        # Add asset to context
        context['asset'] = self.get_asset()
        
        # Add event type choices for filter dropdown
        context['event_types'] = AssetHistory.EVENT_TYPE_CHOICES
        
        # Add active filters to context for form pre-population
        context['active_filters'] = {
            'event_type': self.request.GET.get('event_type', ''),
            'user': self.request.GET.get('user', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
        }
        
        return context


class AssetHistoryExportView(LoginRequiredMixin, View):
    """Export asset history to CSV file."""
    login_url = '/login/'
    
    def get(self, request, pk):
        """Generate and return CSV file with asset history."""
        from django.shortcuts import get_object_or_404
        from .services.history_service import HistoryService
        
        # Get the asset
        asset = get_object_or_404(Asset, pk=pk)
        
        # Build filters dictionary from request parameters
        filters = {}
        
        event_type = request.GET.get('event_type', '').strip()
        if event_type:
            filters['event_type'] = event_type
        
        user = request.GET.get('user', '').strip()
        if user:
            filters['user'] = user
        
        date_from = request.GET.get('date_from', '').strip()
        if date_from:
            from datetime import datetime
            try:
                filters['date_from'] = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                pass
        
        date_to = request.GET.get('date_to', '').strip()
        if date_to:
            from datetime import datetime
            try:
                filters['date_to'] = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                pass
        
        # Export history to CSV using HistoryService
        if filters:
            return HistoryService.export_history_to_csv(asset, filters)
        else:
            return HistoryService.export_history_to_csv(asset)



# API Endpoints for Branch-Team Coordination

class GetParentTeamsByBranchView(LoginRequiredMixin, View):
    """API endpoint to get parent teams filtered by branch."""
    login_url = '/login/'
    
    def get(self, request):
        """Return JSON list of parent teams for the specified branch."""
        from .models import Branch
        
        branch_id = request.GET.get('branch')
        
        if not branch_id:
            return JsonResponse({'teams': []})
        
        try:
            branch = Branch.objects.get(pk=branch_id)
            teams = Team.objects.get_parent_teams(branch=branch).values('id', 'name').order_by('name')
            return JsonResponse({'teams': list(teams)})
        except Branch.DoesNotExist:
            return JsonResponse({'teams': []})


class GetSubTeamsByParentAndBranchView(LoginRequiredMixin, View):
    """API endpoint to get sub-teams filtered by parent and branch."""
    login_url = '/login/'
    
    def get(self, request):
        """Return JSON list of sub-teams for the specified parent and branch."""
        from .models import Branch
        
        parent_id = request.GET.get('parent')
        branch_id = request.GET.get('branch')
        
        if not parent_id or not branch_id:
            return JsonResponse({'sub_teams': []})
        
        try:
            parent = Team.objects.get(pk=parent_id)
            branch = Branch.objects.get(pk=branch_id)
            
            # Verify parent belongs to the branch
            if parent.branch_id != branch.id:
                return JsonResponse({'sub_teams': []})
            
            sub_teams = parent.sub_teams.filter(branch=branch).values('id', 'name').order_by('name')
            return JsonResponse({'sub_teams': list(sub_teams)})
        except (Team.DoesNotExist, Branch.DoesNotExist):
            return JsonResponse({'sub_teams': []})



class TeamManagementView(AdminRequiredMixin, ListView):
    """Display all teams with asset counts for management."""
    model = Team
    template_name = 'assets/team_management.html'
    context_object_name = 'teams'
    
    def get_queryset(self):
        """Return all teams with asset counts, ordered by branch and hierarchy."""
        from django.db.models import Count
        
        queryset = Team.objects.select_related('branch', 'parent').annotate(
            asset_count=Count('assets')
        ).order_by('branch__name', 'parent__name', 'name')
        
        return queryset


class TeamCreateView(AdminRequiredMixin, CreateView):
    """Handle team creation (admin only)."""
    model = Team
    template_name = 'assets/team_form.html'
    success_url = reverse_lazy('team_management')
    
    def get_form_class(self):
        from .forms.team_forms import TeamForm
        return TeamForm
    
    def form_valid(self, form):
        """Process form submission."""
        try:
            team = form.save()
            messages.success(self.request, f'Team "{team.name}" created successfully.')
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TeamUpdateView(AdminRequiredMixin, CreateView):
    """Handle team updates (admin only)."""
    model = Team
    template_name = 'assets/team_form.html'
    success_url = reverse_lazy('team_management')
    pk_url_kwarg = 'pk'
    
    def get_form_class(self):
        from .forms.team_forms import TeamForm
        return TeamForm
    
    def get_object(self, queryset=None):
        """Get the team to update."""
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Team, pk=self.kwargs.get(self.pk_url_kwarg))
    
    def get_form_kwargs(self):
        """Pass the team instance to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Add team to context."""
        context = super().get_context_data(**kwargs)
        context['team'] = self.get_object()
        return context
    
    def form_valid(self, form):
        """Process form submission."""
        try:
            team = form.save()
            messages.success(self.request, f'Team "{team.name}" updated successfully.')
            return redirect(self.success_url)
        except ValidationError as e:
            if hasattr(e, 'message_dict'):
                for field, errors in e.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
            else:
                form.add_error(None, str(e))
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Handle form validation errors."""
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class TeamDeleteView(AdminRequiredMixin, View):
    """Handle team deletion with password confirmation (admin only)."""
    template_name = 'assets/team_confirm_delete.html'
    
    def get(self, request, pk):
        """Display confirmation dialog with password prompt."""
        from django.shortcuts import get_object_or_404, render
        from .forms.team_forms import DeleteTeamForm
        
        team = get_object_or_404(Team, pk=pk)
        form = DeleteTeamForm()
        
        return render(request, self.template_name, {
            'team': team,
            'form': form
        })
    
    def post(self, request, pk):
        """Process team deletion with password verification."""
        from django.shortcuts import get_object_or_404
        from django.contrib.auth.hashers import check_password
        from .forms.team_forms import DeleteTeamForm
        
        team = get_object_or_404(Team, pk=pk)
        form = DeleteTeamForm(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            
            # Verify user password
            if not check_password(password, request.user.password):
                messages.error(request, 'Incorrect password.')
                return render(request, self.template_name, {
                    'team': team,
                    'form': form
                })
            
            # Check if team has assets
            if team.assets.exists():
                messages.error(request, f'Cannot delete team "{team.name}" because it has {team.assets.count()} asset(s) assigned.')
                return redirect('team_management')
            
            # Check if team has sub-teams
            if team.sub_teams.exists():
                messages.error(request, f'Cannot delete team "{team.name}" because it has {team.sub_teams.count()} sub-team(s).')
                return redirect('team_management')
            
            team_name = team.name
            team.delete()
            messages.success(request, f'Team "{team_name}" deleted successfully.')
            return redirect('team_management')
        
        # Form validation failed
        messages.error(request, 'Please correct the errors below.')
        return render(request, self.template_name, {
            'team': team,
            'form': form
        })


class GetTeamsByBranchView(LoginRequiredMixin, View):
    """API endpoint to get teams by branch (for AJAX calls)."""
    
    def get(self, request, branch_id):
        """Return JSON list of teams for a given branch."""
        teams = Team.objects.filter(
            branch_id=branch_id,
            parent__isnull=True
        ).order_by('name').values('id', 'name')
        
        return JsonResponse({'teams': list(teams)})



# Guest IP Assignment Views

class GuestIPAssignView(AdminRequiredMixin, View):
    """Handle AJAX request to assign IP to guest."""
    
    def post(self, request):
        """Process guest IP assignment."""
        from .services.ip_management_service import IPManagementService
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            ip_address_str = request.POST.get('ip_address')
            guest_name = request.POST.get('guest_name', '').strip()
            
            logger.info(f"Guest IP assignment request - IP Address: {ip_address_str}, Guest: {guest_name}")
            
            # Validate inputs
            if not ip_address_str or not guest_name:
                return JsonResponse({
                    'success': False,
                    'error': 'IP address and guest name are required.'
                }, status=400)
            
            # Get IP address by address field
            try:
                ip_address = IPAddress.objects.get(address=ip_address_str)
            except IPAddress.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'IP address {ip_address_str} not found.'
                }, status=404)
            
            # Assign to guest using service
            IPManagementService.assign_ip_to_guest(
                ip_address,
                guest_name,
                request.user
            )
            
            logger.info(f"Successfully assigned IP {ip_address.address} to guest {guest_name}")
            
            return JsonResponse({
                'success': True,
                'message': f'IP {ip_address.address} assigned to {guest_name}',
                'ip_address': ip_address.address,
                'guest_name': guest_name
            })
            
        except ValidationError as e:
            logger.error(f"Validation error during guest IP assignment: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            logger.exception(f"Unexpected error during guest IP assignment: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error assigning IP: {str(e)}'
            }, status=500)


class GuestIPReleaseView(AdminRequiredMixin, View):
    """Handle AJAX request to release guest IP."""
    
    def post(self, request):
        """Process guest IP release."""
        from .services.ip_management_service import IPManagementService
        import logging
        
        logger = logging.getLogger(__name__)
        
        try:
            ip_id = request.POST.get('ip_id')
            
            logger.info(f"Guest IP release request - IP ID: {ip_id}")
            
            # Validate input
            if not ip_id:
                return JsonResponse({
                    'success': False,
                    'error': 'IP ID is required.'
                }, status=400)
            
            # Get IP address
            try:
                ip_address = IPAddress.objects.get(id=ip_id)
            except IPAddress.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'IP address not found.'
                }, status=404)
            
            # Store guest name for response
            guest_name = ip_address.guest_name
            ip_addr_str = ip_address.address
            
            # Release using service
            IPManagementService.release_guest_ip(
                ip_address,
                request.user
            )
            
            logger.info(f"Successfully released IP {ip_addr_str} from guest {guest_name}")
            
            return JsonResponse({
                'success': True,
                'message': f'IP {ip_addr_str} released from {guest_name}',
                'ip_address': ip_addr_str
            })
            
        except ValidationError as e:
            logger.error(f"Validation error during guest IP release: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
        except Exception as e:
            logger.exception(f"Unexpected error during guest IP release: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error releasing IP: {str(e)}'
            }, status=500)


class MarkIPOccupiedView(AdminRequiredMixin, View):
    """Handle AJAX request to mark an IP as manually occupied."""
    login_url = '/login/'

    def post(self, request):
        """Process mark-as-occupied request with password verification."""
        from django.contrib.auth.hashers import check_password

        try:
            # Extract POST data
            ip_address_str = request.POST.get('ip_address', '').strip()
            password = request.POST.get('password', '').strip()

            # Validate required inputs
            if not ip_address_str:
                return JsonResponse({
                    'success': False,
                    'error': 'IP address is required.'
                }, status=400)

            if not password:
                return JsonResponse({
                    'success': False,
                    'error': 'Password is required.'
                }, status=400)

            # Verify admin password
            if not check_password(password, request.user.password):
                return JsonResponse({
                    'success': False,
                    'error': 'Incorrect password.'
                }, status=403)

            # Look up IP address
            try:
                ip_obj = IPAddress.objects.get(address=ip_address_str)
            except IPAddress.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': f'IP address {ip_address_str} not found.'
                }, status=404)

            # Mark as occupied using service
            from .services.ip_management_service import IPManagementService
            particulars = request.POST.get('particulars', '').strip()
            IPManagementService.mark_ip_occupied(ip_obj, request.user, particulars=particulars)

            return JsonResponse({
                'success': True,
                'message': f'IP {ip_address_str} marked as occupied.',
                'ip_address': ip_address_str,
                'occupied_by': request.user.username
            })

        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e.message) if hasattr(e, 'message') else str(e)
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error marking IP: {str(e)}'
            }, status=500)


class ReleaseOccupiedIPView(AdminRequiredMixin, View):
    """Handle AJAX request to release a manually-occupied IP."""
    login_url = '/login/'
    
    def post(self, request):
        """Process release request with password verification."""
        from django.contrib.auth.hashers import check_password
        
        try:
            ip_address_str = request.POST.get('ip_address', '').strip()
            password = request.POST.get('password', '').strip()
            
            if not ip_address_str:
                return JsonResponse({'success': False, 'error': 'IP address is required.'}, status=400)
            
            if not password:
                return JsonResponse({'success': False, 'error': 'Password is required.'}, status=400)
            
            if not check_password(password, request.user.password):
                return JsonResponse({'success': False, 'error': 'Incorrect password.'}, status=403)
            
            try:
                ip_obj = IPAddress.objects.get(address=ip_address_str)
            except IPAddress.DoesNotExist:
                return JsonResponse({'success': False, 'error': f'IP address {ip_address_str} not found.'}, status=404)
            
            from .services.ip_management_service import IPManagementService
            IPManagementService.release_occupied_ip(ip_obj, request.user)
            
            return JsonResponse({
                'success': True,
                'message': f'IP {ip_address_str} released successfully.',
                'ip_address': ip_address_str
            })
            
        except ValidationError as e:
            return JsonResponse({'success': False, 'error': str(e.message) if hasattr(e, 'message') else str(e)}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error releasing IP: {str(e)}'}, status=500)



class EmployeeSearchView(LoginRequiredMixin, View):
    """Search assets and accessories by employee code."""
    template_name = 'assets/employee_search.html'
    login_url = '/login/'
    
    def get(self, request):
        """Display search form."""
        employee_code = request.GET.get('employee_code', '').strip()
        
        context = {
            'employee_code': employee_code,
            'assets': None,
        }
        
        if employee_code:
            # Search for assets with this employee code
            assets = Asset.objects.filter(
                employee_code__iexact=employee_code
            ).select_related(
                'operating_system',
                'ip_address',
                'team',
                'branch'
            ).prefetch_related(
                'accessories',
                'asset_ip_addresses',
                'asset_ip_addresses__ip_address'
            ).order_by('-created_at')
            
            context['assets'] = assets
        
        return render(request, self.template_name, context)


class EmployeeAssetsExportView(LoginRequiredMixin, View):
    """Export employee assets and accessories to Excel."""
    login_url = '/login/'
    
    def get(self, request):
        """Generate and return Excel file with employee assets and accessories."""
        employee_code = request.GET.get('employee_code', '').strip()
        
        if not employee_code:
            # Redirect back to employee search if no code provided
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, 'Please provide an employee code.')
            return redirect('employee_search')
        
        # Use export service to generate Excel file
        export_service = ExportService()
        return export_service.export_employee_assets(employee_code)


class ChangeAssetTagView(LoginRequiredMixin, View):
    """Allow changing asset tag with admin password verification."""
    login_url = '/login/'
    
    def post(self, request, pk):
        """Change asset tag after verifying admin password."""
        from django.shortcuts import get_object_or_404, redirect
        from django.contrib.auth import authenticate
        from django.contrib import messages
        from assets.models import AssetHistory
        
        asset = get_object_or_404(Asset, pk=pk)
        
        # Get form data
        new_asset_tag = request.POST.get('new_asset_tag', '').strip()
        admin_password = request.POST.get('admin_password', '')
        
        # Validate inputs
        if not new_asset_tag:
            messages.error(request, 'New asset tag is required.')
            return redirect('asset_detail', pk=pk)
        
        if not admin_password:
            messages.error(request, 'Admin password is required.')
            return redirect('asset_detail', pk=pk)
        
        # Check if new asset tag already exists
        if Asset.objects.filter(asset_tag=new_asset_tag).exclude(pk=pk).exists():
            messages.error(request, f'Asset tag "{new_asset_tag}" already exists. Please use a different tag.')
            return redirect('asset_detail', pk=pk)
        
        # Verify admin password
        user = authenticate(username=request.user.username, password=admin_password)
        if not user or not user.is_staff:
            messages.error(request, 'Invalid admin password or you do not have admin privileges.')
            return redirect('asset_detail', pk=pk)
        
        # Store old asset tag
        old_asset_tag = asset.asset_tag
        
        # Update asset tag
        asset.asset_tag = new_asset_tag
        asset.save()
        
        # Create history entry
        AssetHistory.objects.create(
            asset=asset,
            event_type='updated',
            user=request.user.username,
            changes={
                'asset_tag': {
                    'old': old_asset_tag,
                    'new': new_asset_tag
                }
            },
            notes=f'Asset tag changed from "{old_asset_tag}" to "{new_asset_tag}" by admin verification.'
        )
        
        messages.success(request, f'Asset tag successfully changed from "{old_asset_tag}" to "{new_asset_tag}".')
        return redirect('asset_detail', pk=pk)

