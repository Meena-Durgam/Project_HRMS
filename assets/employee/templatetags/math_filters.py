# templatetags/math_filters.py
from django import template

register = template.Library()
@register.filter
def div(value, arg):
    try:
        return (float(value) / float(arg)) * 100
    except (ValueError, ZeroDivisionError):
        return 0
