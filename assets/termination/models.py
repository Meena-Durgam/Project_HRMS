from django.db import models

# Create your models here.
# termination/models.py
from django.db import models
from django.utils import timezone
from accounts.models import Company  # ✅ Assumes you have a Company model
from employee.models import Employee  # ✅ Corrected import

class Termination(models.Model):
    TERMINATION_TYPES = (
        ('Misconduct', 'Misconduct'),
        ('Layoff', 'Layoff'),
        ('Performance', 'Performance'),
        ('Other', 'Other'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='terminations')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    termination_type = models.CharField(max_length=50, choices=TERMINATION_TYPES)
    termination_date = models.DateField()
    reason = models.TextField()
    notice_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.employee:
            return f"{self.employee.first_name} {self.employee.last_name} - {self.termination_type}"
        return f"Unknown Employee - {self.termination_type}"
