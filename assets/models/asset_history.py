"""AssetHistory model for tracking all changes to assets."""
from django.db import models


class AssetHistory(models.Model):
    """Model for tracking all changes to assets."""
    
    EVENT_TYPE_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('freed', 'Freed'),
        ('scrapped', 'Scrapped'),
        ('reassigned', 'Reassigned'),
        ('health_status_updated', 'Health Status Updated'),
    ]
    
    id = models.AutoField(primary_key=True)
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='history_entries',
        db_index=True,
        help_text="Asset this history entry belongs to"
    )
    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of event that occurred"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this change occurred"
    )
    user = models.CharField(
        max_length=150,
        db_index=True,
        help_text="Username of user who made the change"
    )
    changes = models.JSONField(
        default=dict,
        help_text="Dictionary of field changes: {field_name: {'old': value, 'new': value}}"
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional context (e.g., scrapping reason)"
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Asset History'
        verbose_name_plural = 'Asset Histories'
        indexes = [
            models.Index(fields=['asset', '-timestamp']),
            models.Index(fields=['event_type', '-timestamp']),
            models.Index(fields=['user', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.asset.asset_tag} - {self.event_type} at {self.timestamp}"
    
    def get_formatted_changes(self):
        """Return human-readable formatted changes."""
        from assets.services.history_service import HistoryService
        return HistoryService.format_changes_for_display(self.changes, self.asset)
