from django import template

register = template.Library()

@register.filter
def sort_experiences_by_date(queryset):
    return queryset.order_by('-start_date', '-end_date')
