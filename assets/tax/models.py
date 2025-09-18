from django.db import models
from accounts.models import Company  # Adjust import based on your app structure

class Tax(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='taxes')
    name = models.CharField(max_length=100)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('company', 'name', 'percentage')
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.percentage}%)"
