from django import template
register = template.Library()

@register.filter
def get_range(value, arg):
    return range(value, arg + 1)


@register.filter
def format_break_time(value):
    try:
        total_seconds = int(float(value) * 3600)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        parts = []
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}min")
        if seconds and not hours and not minutes:
            parts.append(f"{seconds}sec")

        return ' '.join(parts) if parts else '0 sec'
    except Exception:
        return '0 sec'
