from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    """Retrieve a value from a dictionary by key."""
    if isinstance(dictionary, dict):
        return dictionary.get(key, [])
    return []
