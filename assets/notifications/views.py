from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Notification

def notifications_view(request):
    # Get the user's role (assuming it's stored in a profile model)
    user_role = request.user.profile.role  # You might store the role in the Profile model
    notifications = Notification.objects.filter(role=user_role).order_by('-created_at')  # Fetch notifications for the user's role

    # Mark notifications as read (optional)
    for notification in notifications:
        if not notification.is_read:
            notification.is_read = True
            notification.save()

    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def clear_notifications(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/'))