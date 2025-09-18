from django import template

register = template.Library()

@register.filter(name='add_required_label')
def add_required_label(field):
    if field.field.required:
        return field.label + ' <span class="text-danger">*</span>'
    return field.label
