"""Attachment model for storing file attachments for assets."""
from django.db import models


class Attachment(models.Model):
    """Model for storing file attachments for assets."""
    asset = models.ForeignKey('Asset', on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='asset_attachments/')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.filename} - {self.asset.asset_tag}"
