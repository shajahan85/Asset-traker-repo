"""Accessory model for tracking accessories provided with assets."""
from django.db import models


class Accessory(models.Model):
    """Model for tracking accessories provided with assets."""
    
    asset = models.ForeignKey(
        'Asset',
        on_delete=models.CASCADE,
        related_name='accessories',
        help_text="Asset to which this accessory is assigned"
    )
    
    accessory_name = models.CharField(
        max_length=200,
        help_text="Name/type of the accessory (e.g., Mouse, Keyboard, Monitor)"
    )
    
    accessory_details = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Additional details about the accessory (e.g., brand, model, serial number)"
    )
    
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Number of this accessory provided"
    )
    
    provided_date = models.DateField(
        auto_now_add=True,
        help_text="Date when the accessory was provided"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name_plural = 'Accessories'
    
    def __str__(self):
        return f"{self.accessory_name} for {self.asset.asset_tag}"
