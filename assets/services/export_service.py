"""
Export service for generating Excel files from asset data.

This service handles creating Excel workbooks from querysets
and generating downloadable files for various asset views.
"""

from typing import List, Callable, Any
import openpyxl
from openpyxl import Workbook
from django.http import HttpResponse
from django.db.models import QuerySet


class ExportService:
    """Service for exporting assets to Excel files."""
    
    def __init__(self):
        """Initialize the export service."""
        pass
    
    def _create_workbook(self, queryset: QuerySet, columns: List[str], title: str, 
                         row_extractor: Callable[[Any], List[Any]] = None) -> Workbook:
        """
        Create Excel workbook from queryset.
        
        Args:
            queryset: Django QuerySet containing data to export
            columns: List of column names for headers
            title: Title for the worksheet
            row_extractor: Optional function to extract row data from each queryset item.
                          If not provided, items are used as-is (for list of lists).
            
        Returns:
            openpyxl Workbook object with headers, data, and formatted columns
        """
        # Create new workbook and set title
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = title
        
        # Write headers to first row
        sheet.append(columns)
        
        # Loop through queryset and write data rows
        for item in queryset:
            if row_extractor:
                row_data = row_extractor(item)
            else:
                # If no extractor provided, assume item is already a list/tuple
                row_data = item if isinstance(item, (list, tuple)) else [item]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        return workbook
    
    def export_active_assets(self) -> HttpResponse:
        """
        Export all active assets to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import Asset
        
        # Query active assets with related data, ordered by asset_tag
        queryset = Asset.objects.filter(status='active').select_related(
            'operating_system', 'team', 'ip_address'
        ).order_by('asset_tag')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'Asset Tag',
            'System Type',
            'OS',
            'IP Address',
            'Assigned To',
            'Team',
            'Warranty Expiration'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Active Assets'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, asset in enumerate(queryset, start=1):
            row_data = [
                index,  # Sequential row number starting from 1
                asset.asset_tag,
                asset.system_type,
                asset.operating_system.name,
                asset.ip_address.address if asset.ip_address else (asset.manual_ip or ''),
                asset.assigned_to or '',
                asset.team.name if asset.team else '',
                asset.warranty_expiration.strftime('%Y-%m-%d') if asset.warranty_expiration else ''
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=active_assets.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response
    
    def export_freed_assets(self) -> HttpResponse:
        """
        Export all freed assets to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import Asset
        
        # Query freed assets with related data, ordered by freed_date descending
        queryset = Asset.objects.filter(status='freed').select_related(
            'operating_system', 'ip_address'
        ).order_by('-freed_date')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'Asset Tag',
            'System Type',
            'OS',
            'IP Address',
            'Freed Date'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Freed Assets'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, asset in enumerate(queryset, start=1):
            row_data = [
                index,  # Sequential row number starting from 1
                asset.asset_tag,
                asset.system_type,
                asset.operating_system.name,
                asset.ip_address.address if asset.ip_address else (asset.manual_ip or ''),
                asset.freed_date.strftime('%Y-%m-%d %H:%M:%S') if asset.freed_date else ''
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=freed_assets.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response
    
    def export_scrapped_assets(self) -> HttpResponse:
        """
        Export all scrapped assets to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import Asset
        
        # Query scrapped assets with related data, ordered by scrapped_date descending
        queryset = Asset.objects.filter(status='scrapped').select_related(
            'operating_system', 'ip_address'
        ).order_by('-scrapped_date')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'Asset Tag',
            'System Type',
            'OS',
            'IP Address',
            'Scrapped Date'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Scrapped Assets'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, asset in enumerate(queryset, start=1):
            row_data = [
                index,  # Sequential row number starting from 1
                asset.asset_tag,
                asset.system_type,
                asset.operating_system.name,
                asset.ip_address.address if asset.ip_address else (asset.manual_ip or ''),
                asset.scrapped_date.strftime('%Y-%m-%d %H:%M:%S') if asset.scrapped_date else ''
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=scrapped_assets.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response
    
    def export_free_ips(self) -> HttpResponse:
        """
        Export all free IP addresses to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import IPAddress
        
        # Query free IP addresses with related ip_range, ordered by ip_range then by address
        queryset = IPAddress.objects.filter(is_assigned=False).select_related(
            'ip_range'
        ).order_by('ip_range__range_pattern', 'address')
        
        # Define columns for export
        columns = [
            'IP Address',
            'IP Range'
        ]
        
        # Define row extractor function
        def extract_row(ip):
            return [
                ip.address,
                ip.ip_range.range_pattern
            ]
        
        # Create workbook
        workbook = self._create_workbook(queryset, columns, 'Free IPs', extract_row)
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=free_ips.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response

    def export_network_devices(self) -> HttpResponse:
        """
        Export all network devices to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import NetworkDevice
        
        # Query network devices with related data, ordered by device_name
        queryset = NetworkDevice.objects.select_related('ip_address').order_by('device_name')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'Device Type',
            'Device Name',
            'IP Address'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Network Devices'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, device in enumerate(queryset, start=1):
            row_data = [
                index,  # Sequential row number starting from 1
                device.device_type,
                device.device_name,
                device.get_ip_address()
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=network_devices.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response

    def export_hyperv_vms(self) -> HttpResponse:
        """
        Export all Hyper-V VMs to Excel file.
        
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import HyperVVM
        
        # Query VMs with related data, ordered by name
        queryset = HyperVVM.objects.filter(is_active=True).select_related(
            'host_machine', 'host_machine__ip_address', 'ip_address'
        ).order_by('name')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'VM Name',
            'Host Machine',
            'Host IP',
            'VM IP Address',
            'Power Status',
            'Notes'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Hyper-V VMs'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, vm in enumerate(queryset, start=1):
            # Get host machine IP
            host_ip = ''
            if vm.host_machine:
                if vm.host_machine.ip_address:
                    host_ip = vm.host_machine.ip_address.address
                elif vm.host_machine.manual_ip:
                    host_ip = vm.host_machine.manual_ip
            
            # Get VM IP
            vm_ip = vm.get_display_ip()
            
            row_data = [
                index,  # Sequential row number starting from 1
                vm.name,
                vm.host_machine.asset_tag if vm.host_machine else 'N/A',
                host_ip or 'N/A',
                vm_ip or 'N/A',
                vm.get_power_status_display(),
                vm.notes or ''
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = 'attachment; filename=hyperv_vms.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response

    def export_employee_assets(self, employee_code: str) -> HttpResponse:
        """
        Export all assets and accessories for a specific employee to Excel file.
        
        Args:
            employee_code: Employee code to filter assets
            
        Returns:
            HttpResponse with Excel file attachment
        """
        from assets.models import Asset
        
        # Query assets for the employee with related data, ordered by asset_tag
        queryset = Asset.objects.filter(
            employee_code__iexact=employee_code,
            status='active'
        ).select_related(
            'operating_system', 'team', 'branch', 'ip_address'
        ).prefetch_related('accessories').order_by('asset_tag')
        
        # Define columns for export
        columns = [
            'Serial Number',
            'Asset Tag',
            'System Type',
            'OS',
            'IP Address',
            'Assigned To',
            'Employee Code',
            'Team',
            'Branch',
            'Warranty Expiration',
            'Accessories'
        ]
        
        # Create workbook manually to add row numbers
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = f'Assets - {employee_code}'
        
        # Write headers
        sheet.append(columns)
        
        # Write data rows with sequential numbering
        for index, asset in enumerate(queryset, start=1):
            # Get IP address
            primary_ip = asset.get_primary_ip()
            if primary_ip:
                ip_address = primary_ip.get_ip_display()
            elif asset.ip_address:
                ip_address = asset.ip_address.address
            elif asset.manual_ip:
                ip_address = asset.manual_ip
            else:
                ip_address = ''
            
            # Get accessories list
            accessories_list = []
            for acc in asset.accessories.all():
                acc_text = f"{acc.accessory_name}"
                if acc.quantity:
                    acc_text += f" (Qty: {acc.quantity})"
                if acc.accessory_details:
                    acc_text += f" - {acc.accessory_details}"
                accessories_list.append(acc_text)
            
            accessories_str = '; '.join(accessories_list) if accessories_list else 'No accessories'
            
            row_data = [
                index,  # Sequential row number starting from 1
                asset.asset_tag,
                asset.system_type,
                asset.operating_system.name if asset.operating_system else '',
                ip_address,
                asset.assigned_to or '',
                asset.employee_code or '',
                asset.team.name if asset.team else '',
                asset.branch.name if asset.branch else '',
                asset.warranty_expiration.strftime('%Y-%m-%d') if asset.warranty_expiration else '',
                accessories_str
            ]
            sheet.append(row_data)
        
        # Format columns with appropriate widths
        for column_cells in sheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            
            for cell in column_cells:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            
            # Set column width with some padding (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Create HttpResponse with Excel content type
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # Set Content-Disposition header with filename
        response['Content-Disposition'] = f'attachment; filename=employee_assets_{employee_code}.xlsx'
        
        # Save workbook to response
        workbook.save(response)
        
        return response
