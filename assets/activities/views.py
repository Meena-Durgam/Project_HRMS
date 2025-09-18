from django.shortcuts import render, get_object_or_404
from notifications.models import Notification  # Import your Notification model
from .models import Activity

def activities(request):
    # Get all activities
    all_activities = Activity.objects.all().order_by('-created_at')
    
    # Get all notifications for the logged-in user (or any filter you want)
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Get notification ID from query parameter for highlighting
    highlight_id = request.GET.get('highlight')
    
    # Mark the notification as read if it is highlighted
    if highlight_id:
        notification = get_object_or_404(Notification, id=highlight_id)
        notification.is_read = True
        notification.save()

    context = {
        'activities': all_activities,
        'highlight_id': int(highlight_id) if highlight_id else None,
        'notifications': notifications,  # Pass notifications to the template
    }
    return render(request, 'activities.html', context)
