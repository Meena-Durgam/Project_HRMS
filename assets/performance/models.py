from django.db import models
from django.conf import settings
from accounts.models import Company
from department.models import Department
from designation.models import Designation
from employee.models import Employee

# Rating options
RATING_CHOICES = [
    ('Advanced', 'Advanced'),
    ('Intermediate', 'Intermediate'),
    ('Average', 'Average'),
    ('Poor', 'Poor'),
]

RATING_CHOICES_FULL = [
    ('None', 'None'),
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
    ('Expert/Leader', 'Expert/Leader')
]

ORG_RATING_CHOICES = [
    ('None', 'None'),
    ('Beginner', 'Beginner'),
    ('Intermediate', 'Intermediate'),
    ('Advanced', 'Advanced'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
]

# ✅ Performance Indicator Model
class PerformanceIndicator(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Multiple company support
    
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='performance_indicator', null=True, blank=True
    )

    # Technical Skills
    customer_experience = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    marketing = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    management = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    administration = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    presentation_skill = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    quality_of_work = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')

    # Organizational Skills
    efficiency = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    integrity = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    professionalism = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    teamwork = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    critical_thinking = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    conflict_management = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')

    # Behavioural Skills
    attendance = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    punctuality = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    dependability = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    communication = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')
    decision_making = models.CharField(max_length=20, choices=RATING_CHOICES, default='Average')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.designation} ({self.status})"

# ✅ Performance Appraisal Model
class PerformanceAppraisal(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # Multiple company support
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE,
        related_name='performance_appraisals'
    )
    appraiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()

    # === Technical Competencies ===
    customer_experience = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    marketing = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    management = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    administration = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    presentation_skill = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    quality_of_work = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')
    efficiency = models.CharField(max_length=20, choices=RATING_CHOICES_FULL, default='None')

    # === Organizational Competencies ===
    integrity = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    professionalism = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    team_work = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    critical_thinking = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    conflict_management = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    attendance = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')
    ability_to_meet_deadline = models.CharField(max_length=20, choices=ORG_RATING_CHOICES, default='None')

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appraisal for {self.employee} on {self.date}"





