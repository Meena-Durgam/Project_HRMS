from django.db import models
from accounts.models import Company  # ✅ import your Company model
from trainers.models import Trainer
from employee.models import Employee  # ✅ use the updated Employee model


# ✅ Training Type Model
class TrainingType(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='training_types'
    )

    type_name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    class Meta:
        unique_together = ('company', 'type_name')  # ✅ unique within company

    def __str__(self):
        return self.type_name


# ✅ Training Model
class Training(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='trainings'
    )

    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    training_cost = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Scheduled')

    def __str__(self):
        return f"{self.training_type.type_name} - {self.employee.first_name} {self.employee.last_name}"
