from .models import Notification

def unread_notifications(request):
    if hasattr(request, "user") and request.user.is_authenticated:
        unread = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')
        return {
            'unread_notifications': unread,
            'unread_notifications_count': unread.count(),
        }
    return {}
