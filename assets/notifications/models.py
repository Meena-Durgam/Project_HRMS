from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_notifications')  # 👈 Add this
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, default='employee_admin')
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)  # ✅ Required for notify_roles
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # models.py
    target_url = models.URLField(max_length=500, null=True, blank=True)


    def __str__(self):
        return self.message
