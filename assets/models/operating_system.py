"""OperatingSystem model."""
from django.db import models


class OperatingSystem(models.Model):
    """Model for storing available operating systems."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
