from django import template

register = template.Library()

@register.filter
def dict_get(dictionary, key):
    return dictionary.get(key, '')

@register.filter
def dict_get(dict_obj, key):
    if isinstance(dict_obj, dict):
        return dict_obj.get(key)
    return None

