from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Company  # Adjust if Company model is in another app

User = get_user_model()

# 🔸 Goal Type Model (e.g., KPI, Milestone)
class GoalType(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='goal_types'
    )

    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    class Meta:
        db_table = "goal_type"
        unique_together = ('company', 'name')  # Prevent duplicate goal types per company
        ordering = ['name']


# 🔸 Goal Model (Employee/Company Goals)
class Goal(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='goals'
    )

    goal_type = models.ForeignKey(
        GoalType, on_delete=models.CASCADE,
        limit_choices_to={'status': 'Active'}
    )

    subject = models.CharField(max_length=200)
    target_achievement = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    progress = models.PositiveIntegerField(default=0)  # Progress in %

    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_goals'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} ({self.company.name})"

    class Meta:
        db_table = "goal"
        ordering = ['-created_at']
