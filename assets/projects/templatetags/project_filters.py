from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='replace_underscore')
def replace_underscore(value):
    if not isinstance(value, str):
        return value
    return value.replace('_', ' ').title()  # or whatever you want
