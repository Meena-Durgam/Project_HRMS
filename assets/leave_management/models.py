from django.db import models
from django.utils import timezone
from accounts.models import Company, CustomUser
from employee.models import Employee  # Ensure this path is correct

class LeaveType(models.Model):
    ELIGIBILITY_CHOICES = [
        ('', 'Select Employees'),
        ('all', 'All Employees'),
        ('male', 'Male Employees'),
        ('female', 'Female Employees'),
    ]

    YES_NO_CHOICES = [
        ('', 'Select Option'), 
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    name = models.CharField(max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_types')
    default_days = models.PositiveIntegerField(default=1)

    eligibility = models.CharField(
        max_length=10,
        choices=ELIGIBILITY_CHOICES,
        blank=False,
        null=True
        
    )
    monthly_accrual = models.CharField(max_length=50, null=True, blank=True)
    carry_forward = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        blank=False,
        null=True
        
    )

    encashment = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        blank=False,
        null=True
        
    )

    class Meta:
        db_table = 'leave_type'
        unique_together = ('name', 'company')

    def __str__(self):
        return f"{self.name}"

    
class LeaveRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        CustomUser,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'company_owner'},
        related_name='reviewed_leaves'
    )

    class Meta:
        db_table = 'leave_request'
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} ({self.start_date} to {self.end_date})"

    def get_duration_days(self):
        return (self.end_date - self.start_date).days + 1


class LeaveBalance(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )

    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.CASCADE,
        related_name='leave_balances'
    )

    used_days = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'leave_balance'
        unique_together = ('company', 'employee', 'leave_type')

    def remaining_days(self):
        return self.leave_type.default_days - self.used_days

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} (Used: {self.used_days})"

