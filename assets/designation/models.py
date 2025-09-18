from django.db import models
from django.utils import timezone
from department.models import Department
from accounts.models import Company

class Designation(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='designations'
    )
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='designations'
    )
    name = models.CharField(max_length=100)
    
    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')]
    )
    
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'designation'
        unique_together = ('company', 'department', 'name')  # Ensures uniqueness across company & department

    def __str__(self):
        return self.name
