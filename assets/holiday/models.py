from django.db import models
from datetime import datetime
from django.utils import timezone
from accounts.models import Company  # Adjust this import based on your project structure

class Holiday(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='holidays', null=True, blank=True)

    name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    day = models.CharField(max_length=9, blank=True, editable=False)  # Removed default

    def save(self, *args, **kwargs):
        # If date is provided as a string, convert it to a date object
        if isinstance(self.date, str):
            self.date = datetime.strptime(self.date, '%Y-%m-%d').date()
        
        # Calculate and set the day of the week
        self.day = self.date.strftime('%A')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.date} - {self.day})"
