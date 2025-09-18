from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def trainer_status_choices():
    return ['Active', 'Inactive', 'On Leave', 'Terminated']
