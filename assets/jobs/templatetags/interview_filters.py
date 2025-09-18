# templatetags/interview_filters.py

from django import template

register = template.Library()

@register.filter
def get_round_status(interview_rounds, round_number):
    try:
        return interview_rounds.get(round_number=round_number)
    except:
        return None
