from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

def notify_roles(roles, message, url, sender=None):
    """
    Send notifications to specified roles.
    """
    for role in roles:
        users_with_role = User.objects.filter(role=role)
        for user in users_with_role:
            Notification.objects.create(
                sender=sender,
                user=user,
                role=role,
                message=message,
                url=url,         # ✅ Make sure this field exists in your Notification model
                is_read=False,
            )
