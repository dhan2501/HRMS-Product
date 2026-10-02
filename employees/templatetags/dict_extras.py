from django import template

register = template.Library()


@register.filter
def get_item(mapping, key):
    """
    Look up `key` in a dict from a template, where the key is itself a
    template variable (e.g. a loop day number). Used by the birthday
    calendar grid: {{ birthdays_by_day|get_item:day }}
    """
    if not mapping:
        return None
    return mapping.get(key)