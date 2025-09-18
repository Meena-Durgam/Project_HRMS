from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Company  # Adjust import based on your app name

User = get_user_model()

class Overtime(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Link to company
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.PositiveIntegerField()
    ot_type = models.CharField(max_length=100, default='Normal day OT 1.5x')
    
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_overtimes')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.get_full_name() or self.employee.username} - {self.date}"
