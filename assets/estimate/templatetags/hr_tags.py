from django import template

register = template.Library()

@register.filter
def indian_currency(value):
    try:
        value = float(value)
        return "₹{:,.2f}".format(value).replace(",", "X").replace("X", ",", 1)
    except (ValueError, TypeError):
        return value