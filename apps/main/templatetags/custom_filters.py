# apps/main/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def make_range(value):
    """Створює range від 1 до value"""
    try:
        return range(1, int(value) + 1)
    except (ValueError, TypeError):
        return range(1, 2)
