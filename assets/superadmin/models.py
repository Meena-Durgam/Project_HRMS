from django.db import models
from dateutil.relativedelta import relativedelta

# models.py

class Package(models.Model):
    PLAN_TYPE_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
    ]

    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES)
    number_of_users = models.PositiveIntegerField()
    number_of_projects = models.PositiveIntegerField()
    storage_space = models.PositiveIntegerField(help_text="In GB")
    description = models.TextField(blank=True)
    status = models.BooleanField(default=True)  # Active / Inactive
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(null=True, blank=True, help_text="End date of the package")
    module_list = models.TextField(blank=True, null=True)
    
    def save(self, *args, **kwargs):
        # Set modified_date based on plan_type if not already set
        if not self.modified_date and self.created_date:
            if self.plan_type == 'Monthly':
                self.modified_date = self.created_date + relativedelta(months=1)
            elif self.plan_type == 'Yearly':
                self.modified_date = self.created_date + relativedelta(years=1)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name 