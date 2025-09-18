from django import template

register = template.Library()

@register.filter
def status_color(status):
    return {
        'new': 'info',
        'interview_scheduled': 'warning',
        'hired': 'success',
        'rejected': 'danger',
    }.get(status, 'secondary')
