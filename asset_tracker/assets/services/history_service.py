"""Service for managing asset history tracking."""
from django.utils import timezone
from assets.models import AssetHistory


class HistoryService:
    """Business logic for asset history tracking."""
    
    # Fields to track in history
    TRACKED_FIELDS = [
        'asset_tag',
        'system_type',
        'operating_system',
        'assigned_to',
        'team',
        'status',
        'ip_address',
        'manual_ip',
        'manufacturer',
        'hardware_serial_number',
        'warranty_expiration',
        'particulars',
        'health_status',
        'issues_description',
        'scrapping_reason'
    ]
    
    # Human-readable field labels
    FIELD_LABELS = {
        'asset_tag': 'Asset Tag',
        'system_type': 'System Type',
        'operating_system': 'Operating System',
        'assigned_to': 'Assigned To',
        'team': 'Team',
        'status': 'Status',
        'ip_address': 'IP Address',
        'manual_ip': 'Manual IP',
        'manufacturer': 'Manufacturer',
        'hardware_serial_number': 'Hardware Serial Number',
        'warranty_expiration': 'Warranty Expiration',
        'particulars': 'Particulars',
        'health_status': 'Health Status',
        'issues_description': 'Issues Description',
        'scrapping_reason': 'Scrapping Reason',
    }
    
    @staticmethod
    def _get_field_value(asset, field_name):
        """
        Get field value from asset, handling foreign keys and date types.
        
        Args:
            asset: Asset instance
            field_name: Name of the field to extract
            
        Returns:
            Field value with appropriate formatting for JSON serialization
        """
        import datetime
        
        value = getattr(asset, field_name, None)
        
        # Handle foreign key fields
        if field_name == 'operating_system' and value:
            return str(value)
        elif field_name == 'team' and value:
            return str(value)
        elif field_name == 'ip_address' and value:
            return value.address
        
        # Handle date/datetime objects for JSON serialization
        if isinstance(value, (datetime.date, datetime.datetime)):
            return value.isoformat()
        
        return value
    
    @staticmethod
    def record_creation(asset, user):
        """Record asset creation event."""
        changes = {}
        for field in HistoryService.TRACKED_FIELDS:
            value = HistoryService._get_field_value(asset, field)
            if value is not None and value != '':
                changes[field] = {'old': None, 'new': value}
        
        AssetHistory.objects.create(
            asset=asset,
            event_type='created',
            user=user.username,
            changes=changes
        )
    
    @staticmethod
    def record_update(asset, old_values, user):
        """Record asset update event."""
        changes = {}
        for field in HistoryService.TRACKED_FIELDS:
            old_value = old_values.get(field)
            new_value = HistoryService._get_field_value(asset, field)
            
            if old_value != new_value:
                changes[field] = {'old': old_value, 'new': new_value}
        
        if changes:
            AssetHistory.objects.create(
                asset=asset,
                event_type='updated',
                user=user.username,
                changes=changes
            )
    
    @staticmethod
    def record_status_change(asset, event_type, user, notes=None, old_assigned_to=None, old_team=None, old_ip_address=None):
        """
        Record status transition event (freed, scrapped, reassigned).
        
        Args:
            asset: Asset instance
            event_type: Type of status change (freed, scrapped, reassigned)
            user: User performing the action
            notes: Optional notes for the history entry
            old_assigned_to: Previous assigned_to value (for freed event)
            old_team: Previous team value (for freed event)
            old_ip_address: Previous IP address (for freed event)
        """
        changes = {}
        
        # Record relevant field changes based on event type
        if event_type == 'freed':
            changes = {
                'status': {'old': 'active', 'new': 'freed'},
            }
            # Record who it was assigned to before freeing
            if old_assigned_to:
                changes['assigned_to'] = {'old': old_assigned_to, 'new': None}
            if old_team:
                changes['team'] = {'old': str(old_team), 'new': None}
            if old_ip_address:
                changes['ip_address'] = {'old': old_ip_address.address if hasattr(old_ip_address, 'address') else str(old_ip_address), 'new': None}
                
        elif event_type == 'scrapped':
            changes = {
                'status': {'old': 'freed', 'new': 'scrapped'},
            }
        elif event_type == 'reassigned':
            changes = {
                'status': {'old': 'freed', 'new': 'active'},
            }
            # Record new assignment details
            if asset.assigned_to:
                changes['assigned_to'] = {'old': None, 'new': asset.assigned_to}
            if asset.team:
                changes['team'] = {'old': None, 'new': str(asset.team)}
            if asset.ip_address:
                changes['ip_address'] = {'old': None, 'new': asset.ip_address.address}
            elif asset.manual_ip:
                changes['manual_ip'] = {'old': None, 'new': asset.manual_ip}
        
        AssetHistory.objects.create(
            asset=asset,
            event_type=event_type,
            user=user.username,
            changes=changes,
            notes=notes
        )
    
    @staticmethod
    def record_health_status_update(asset, old_health_status, user, old_issues_description=None):
        """
        Record health status change for freed assets.
        
        Args:
            asset: Asset instance with updated health status
            old_health_status: Previous health_status value
            user: User who made the change
            old_issues_description: Previous issues_description value (optional)
        """
        changes = {
            'health_status': {
                'old': old_health_status,
                'new': asset.health_status
            }
        }
        
        # If health status changed to "defective", record issues_description
        if asset.health_status == 'defective' and asset.issues_description:
            changes['issues_description'] = {
                'old': old_issues_description,
                'new': asset.issues_description
            }
        
        # If health status changed from "defective" to "healthy", record clearing of issues_description
        if old_health_status == 'defective' and asset.health_status == 'healthy':
            changes['issues_description'] = {
                'old': old_issues_description,
                'new': None
            }
        
        AssetHistory.objects.create(
            asset=asset,
            event_type='health_status_updated',
            user=user.username,
            changes=changes
        )
    
    @staticmethod
    def get_asset_history(asset, filters=None):
        """Get history entries for an asset with optional filtering."""
        queryset = AssetHistory.objects.filter(asset=asset)
        
        if filters:
            if filters.get('event_type'):
                queryset = queryset.filter(event_type=filters['event_type'])
            if filters.get('user'):
                queryset = queryset.filter(user__icontains=filters['user'])
            if filters.get('date_from'):
                queryset = queryset.filter(timestamp__gte=filters['date_from'])
            if filters.get('date_to'):
                queryset = queryset.filter(timestamp__lte=filters['date_to'])
        
        return queryset.order_by('-timestamp')
    
    @staticmethod
    def format_changes_for_display(changes, asset):
        """Format changes dictionary for human-readable display."""
        formatted = []
        
        for field_name, values in changes.items():
            field_label = HistoryService.FIELD_LABELS.get(field_name, field_name)
            old_value = HistoryService._format_value_for_display(values.get('old'), field_name)
            new_value = HistoryService._format_value_for_display(values.get('new'), field_name)
            
            formatted.append({
                'field': field_label,
                'old_value': old_value,
                'new_value': new_value
            })
        
        return formatted
    
    @staticmethod
    def _format_value_for_display(value, field_name):
        """Format value for human-readable display."""
        if value is None or value == '':
            return 'Not set'
        
        # Format dates
        if field_name == 'warranty_expiration' and value:
            from django.utils.dateformat import format as date_format
            try:
                return date_format(value, 'Y-m-d')
            except:
                return str(value)
        
        return str(value)
    
    @staticmethod
    def _format_value_for_export(value):
        """
        Format value for CSV export.
        
        Args:
            value: Value to format for CSV export
            
        Returns:
            CSV-safe string representation of the value
        """
        if value is None or value == '':
            return 'Not set'
        return str(value)
    
    @staticmethod
    def export_history_to_csv(asset, filters=None):
        """
        Export asset history to CSV format.
        
        Args:
            asset: Asset instance
            filters: Optional filters dict (event_type, user, date_from, date_to)
        
        Returns:
            HttpResponse: CSV file response with appropriate headers
        """
        import csv
        from django.http import HttpResponse
        
        # Create HTTP response with CSV content type
        response = HttpResponse(content_type='text/csv')
        
        # Generate filename with asset_tag and timestamp
        filename = f'asset_history_{asset.asset_tag}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create CSV writer
        writer = csv.writer(response)
        
        # Write header row
        writer.writerow(['Timestamp', 'Event Type', 'User', 'Field', 'Previous Value', 'New Value', 'Notes'])
        
        # Get filtered history entries
        history_entries = HistoryService.get_asset_history(asset, filters)
        
        # Write data rows
        for entry in history_entries:
            if entry.changes:
                # Write a row for each field change
                for field_name, values in entry.changes.items():
                    field_label = HistoryService.FIELD_LABELS.get(field_name, field_name)
                    old_value = HistoryService._format_value_for_export(values.get('old'))
                    new_value = HistoryService._format_value_for_export(values.get('new'))
                    
                    writer.writerow([
                        entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        entry.get_event_type_display(),
                        entry.user,
                        field_label,
                        old_value,
                        new_value,
                        entry.notes or ''
                    ])
            else:
                # Write a single row for entries without field changes
                writer.writerow([
                    entry.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                    entry.get_event_type_display(),
                    entry.user,
                    '',
                    '',
                    '',
                    entry.notes or ''
                ])
        
        return response
