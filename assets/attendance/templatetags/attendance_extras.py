from django import template
import calendar

register = template.Library()

@register.filter
def to_months(value):
    return [(i, calendar.month_name[i]) for i in range(1, 13)]

@register.simple_tag
def get_days_in_month(month, year):
    """Returns list of day numbers in a given month/year."""
    _, num_days = calendar.monthrange(year, month)
    return range(1, num_days + 1)

@register.filter
def get_attendance(attendance_dict, day):
    return attendance_dict.get(day)

@register.filter
def get_leave(leave_dict, day):
    return leave_dict.get(day)