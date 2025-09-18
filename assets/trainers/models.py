from django.db import models
from accounts.models import Company  # Adjust the import path to your actual Company model

class Trainer(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
        ('Terminated', 'Terminated'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='trainers')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    trainer_role = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')
    profile_photo = models.ImageField(upload_to='trainer_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
