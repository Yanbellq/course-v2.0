# apps/crm/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Повертає результат множення value * arg.
    Використання в шаблоні:
        {{ product.unit_price|multiply:product.quantity }}
    """
    try:
        result = float(value) * float(arg)
        # Форматуємо до 2 знаків після коми
        return round(result, 2)
    except (ValueError, TypeError):
        return 0
