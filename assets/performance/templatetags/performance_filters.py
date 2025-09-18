# myapp/templatetags/custom_filters.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_field(form, field_name):
    return form[field_name]

@register.filter
def performance_status_class(status):
    return 'success' if status.lower() == 'active' else 'secondary'
