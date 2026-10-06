"""
Notification service for sending email notifications about asset lifecycle events.
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class NotificationService:
    """Service class for sending email notifications."""
    
    # Email recipients for asset notifications
    NOTIFICATION_RECIPIENTS = [
        'anoop@benzyinfotech.com',
        'Shajahan.t@benzyinfotech.com',
        'desktopsupport@benzyinfotech.com',
        'sreeshob@benzyinfotech.com'
    ]
    
    @staticmethod
    def send_asset_created_notification(asset, user, skip_notification=False):
        """
        Send email notification when a new asset is created.
        
        Args:
            asset: Asset instance that was created
            user: User who created the asset
            skip_notification: If True, skip sending email
        """
        subject = f'New Asset Created: {asset.asset_tag}'
        
        context = {
            'asset': asset,
            'user': user,
            'action': 'created',
            'ip_address': asset.ip_address.address if asset.ip_address else asset.manual_ip or 'Not assigned'
        }
        
        message = f"""
New Asset Created

Asset Tag: {asset.asset_tag}
System Type: {asset.system_type}
Manufacturer: {asset.manufacturer or 'N/A'}
Operating System: {asset.operating_system.name if asset.operating_system else 'N/A'}
IP Address: {context['ip_address']}
Assigned To: {asset.assigned_to or 'Unassigned'}
Employee Code: {asset.employee_code or 'N/A'}
Team: {asset.team.name if asset.team else 'N/A'}
Created By: {user.username}

Particulars: {asset.particulars or 'N/A'}
"""
        
        NotificationService._send_email(subject, message, skip_notification)
    
    @staticmethod
    def send_asset_updated_notification(asset, user, changes=None, skip_notification=False):
        """
        Send email notification when an asset is updated.
        
        Args:
            asset: Asset instance that was updated
            user: User who updated the asset
            changes: Optional dict of changes made
            skip_notification: If True, skip sending email
        """
        subject = f'Asset Updated: {asset.asset_tag}'
        
        context = {
            'asset': asset,
            'user': user,
            'action': 'updated',
            'ip_address': asset.ip_address.address if asset.ip_address else asset.manual_ip or 'Not assigned'
        }
        
        message = f"""
Asset Updated

Asset Tag: {asset.asset_tag}
System Type: {asset.system_type}
Manufacturer: {asset.manufacturer or 'N/A'}
Operating System: {asset.operating_system.name if asset.operating_system else 'N/A'}
IP Address: {context['ip_address']}
Assigned To: {asset.assigned_to or 'Unassigned'}
Employee Code: {asset.employee_code or 'N/A'}
Team: {asset.team.name if asset.team else 'N/A'}
Updated By: {user.username}

Particulars: {asset.particulars or 'N/A'}
"""
        
        NotificationService._send_email(subject, message, skip_notification)
    
    @staticmethod
    def send_asset_freed_notification(asset, user, skip_notification=False):
        """
        Send email notification when an asset is freed.
        
        Args:
            asset: Asset instance that was freed
            user: User who freed the asset
            skip_notification: If True, skip sending email
        """
        subject = f'Asset Freed: {asset.asset_tag}'
        
        message = f"""
Asset Freed

Asset Tag: {asset.asset_tag}
System Type: {asset.system_type}
Manufacturer: {asset.manufacturer or 'N/A'}
Operating System: {asset.operating_system.name if asset.operating_system else 'N/A'}
Previously Assigned To: {asset.assigned_to or 'Unassigned'}
Employee Code: {asset.employee_code or 'N/A'}
Freed By: {user.username}
Freed Date: {asset.freed_date.strftime('%Y-%m-%d %H:%M') if asset.freed_date else 'N/A'}

Health Status: {asset.get_health_status_display() if asset.health_status else 'Not specified'}
Issues: {asset.issues_description or 'None'}
"""
        
        NotificationService._send_email(subject, message, skip_notification)
    
    @staticmethod
    def send_asset_scrapped_notification(asset, user, skip_notification=False):
        """
        Send email notification when an asset is scrapped.
        
        Args:
            asset: Asset instance that was scrapped
            user: User who scrapped the asset
            skip_notification: If True, skip sending email
        """
        subject = f'Asset Scrapped: {asset.asset_tag}'
        
        message = f"""
Asset Scrapped

Asset Tag: {asset.asset_tag}
System Type: {asset.system_type}
Manufacturer: {asset.manufacturer or 'N/A'}
Operating System: {asset.operating_system.name if asset.operating_system else 'N/A'}
Previously Assigned To: {asset.assigned_to or 'Unassigned'}
Employee Code: {asset.employee_code or 'N/A'}
Scrapped By: {user.username}
Scrapped Date: {asset.scrapped_date.strftime('%Y-%m-%d %H:%M') if asset.scrapped_date else 'N/A'}

Scrapping Reason: {asset.scrapping_reason or 'Not specified'}
"""
        
        NotificationService._send_email(subject, message, skip_notification)
    
    @staticmethod
    def send_asset_reassigned_notification(asset, user, skip_notification=False):
        """
        Send email notification when a freed asset is reassigned.
        
        Args:
            asset: Asset instance that was reassigned
            user: User who reassigned the asset
            skip_notification: If True, skip sending email
        """
        subject = f'Asset Reassigned: {asset.asset_tag}'
        
        context = {
            'asset': asset,
            'user': user,
            'action': 'reassigned',
            'ip_address': asset.ip_address.address if asset.ip_address else asset.manual_ip or 'Not assigned'
        }
        
        message = f"""
Asset Reassigned (Back to Active)

Asset Tag: {asset.asset_tag}
System Type: {asset.system_type}
Manufacturer: {asset.manufacturer or 'N/A'}
Operating System: {asset.operating_system.name if asset.operating_system else 'N/A'}
IP Address: {context['ip_address']}
Assigned To: {asset.assigned_to or 'Unassigned'}
Employee Code: {asset.employee_code or 'N/A'}
Team: {asset.team.name if asset.team else 'N/A'}
Reassigned By: {user.username}

Particulars: {asset.particulars or 'N/A'}
"""
        
        NotificationService._send_email(subject, message, skip_notification)
    
    @staticmethod
    def _send_email(subject, message, skip_notification=False):
        """
        Internal method to send email.
        
        Args:
            subject: Email subject
            message: Email message body
            skip_notification: If True, skip sending email (for bulk updates)
        """
        # Check if notification should be skipped
        if skip_notification:
            return
        
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=NotificationService.NOTIFICATION_RECIPIENTS,
                fail_silently=True,  # Changed to True to prevent blocking on errors
            )
        except Exception as e:
            # Log the error but don't fail the operation
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send email notification: {str(e)}")
