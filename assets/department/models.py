from django.db import models
from django.utils import timezone
from accounts.models import Company  # 👈 Import the Company model

class Department(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=[('Active', 'Active'), ('Inactive', 'Inactive')],
        default='Active'
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'department'
        unique_together = ('company', 'name')  # 👈 Enforce unique department name per company
        # ✅ Optional alternative for newer Django (>=3.2)
        # constraints = [
        #     models.UniqueConstraint(fields=['company', 'name'], name='unique_department_per_company')
        # ]

    def __str__(self):
        return self.name
