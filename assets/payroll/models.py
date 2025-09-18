from django.db import models
from accounts.models import Company
from employee.models import Employee  # Custom Employee model
from django.db import models
from decimal import Decimal
from employee.models import Employee, SalaryAndStatutory
from django.core.exceptions import ValidationError
class PayItem(models.Model):
    ITEM_TYPES = (
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    )

    ASSIGN_CHOICES = (
        ('all', 'All Employees'),
        ('specific', 'Specific Employees'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    assign_to = models.CharField(max_length=10, choices=ASSIGN_CHOICES)
    specific_employees = models.ManyToManyField(Employee, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.title} - ₹{self.amount} ({self.get_assign_to_display()})"
 
from django.utils import timezone
from django.utils import timezone
import datetime

def default_payroll_date():
    today = timezone.now().date()
    return today.replace(day=1)  # First day of the current month

class Payroll(models.Model):
    STATUS_CHOICES = (
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    payroll_date = models.DateField(default=default_payroll_date)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')

    def __str__(self):
        if self.employee and hasattr(self.employee, 'user'):
            return f"{self.employee.user.get_full_name()} - {self.payroll_date.strftime('%B %Y')}"
        return f"Payroll - {self.payroll_date.strftime('%B %Y')}"

    def clean(self):
        year = self.payroll_date.year
        month = self.payroll_date.month
        existing = Payroll.objects.filter(
            employee=self.employee,
            payroll_date__year=year,
            payroll_date__month=month
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError("Payroll already exists for this employee in the selected month.")

    def calculate_totals(self):
        earnings = Decimal('0.00')
        deductions = Decimal('0.00')

        try:
            salary_statutory = SalaryAndStatutory.objects.get(employee=self.employee)
            base_salary = salary_statutory.salary_amount or Decimal('0.00')
            earnings += base_salary

            if salary_statutory.pf_contribution == 'yes' and salary_statutory.employee_pf_rate:
                pf_percent = Decimal(salary_statutory.employee_pf_rate.strip('%'))
                deductions += (base_salary * pf_percent) / 100

            if salary_statutory.esi_contribution == 'yes' and salary_statutory.employee_esi_rate:
                esi_percent = Decimal(salary_statutory.employee_esi_rate.strip('%'))
                deductions += (base_salary * esi_percent) / 100

        except SalaryAndStatutory.DoesNotExist:
            pass

        pay_items = PayItem.objects.filter(company=self.company)
        for item in pay_items:
            if item.assign_to == 'all' or (item.assign_to == 'specific' and self.employee in item.specific_employees.all()):
                if item.item_type == 'earning':
                    earnings += item.amount
                elif item.item_type == 'deduction':
                    deductions += item.amount

        self.total_earnings = earnings
        self.total_deductions = deductions
        self.net_salary = earnings - deductions
        self.save()
