from django.db import models
from django.conf import settings
from django.utils import timezone


class Resignation(models.Model):
    MODE_OF_EXIT_CHOICES = [
        ('resignation', 'Resignation'),
        ('retirement', 'Retirement'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    employee = models.ForeignKey('employee.Employee', on_delete=models.CASCADE)
    resignation_date = models.DateField(blank=True, null=True)
    last_working_day = models.DateField(blank=True, null=True)
    notice_period = models.PositiveIntegerField(blank=True, null=True)
    mode_of_exit = models.CharField(max_length=20, choices=MODE_OF_EXIT_CHOICES,blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    resignation_letter = models.FileField(upload_to='resignation_letters/',blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending',blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.employee} - {self.mode_of_exit}"
