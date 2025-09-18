from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() 

# Model for Activity
class Activity(models.Model):
    User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message}"