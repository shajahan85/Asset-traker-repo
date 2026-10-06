"""Custom template filters for asset templates."""
from django import template

register = template.Library()


@register.filter(name='replace_underscore')
def replace_underscore(value):
    """Replace underscores with spaces in field names."""
    if isinstance(value, str):
        return value.replace('_', ' ')
    return value
