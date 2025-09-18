from django.db import models
from django.conf import settings
from django.utils import timezone
from accounts.models import Company  # Make sure your Company model is correctly imported
from django.contrib.auth import get_user_model
from employee.models import Employee
from employee.models import Employee, Department  # make sure you import Department

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Travel', 'Travel'),
        ('Food', 'Food'),
        ('Accommodation', 'Accommodation'),
        ('Internet', 'Internet'),
        ('Office Supplies', 'Office Supplies'),
        ('Miscellaneous', 'Miscellaneous'),
    ]

    PAID_BY_CHOICES = [
        ('Self', 'Self'),
        ('Company Advance', 'Company Advance'),
        ('Credit Card', 'Credit Card'),
    ]

    EXPENSE_TYPE_CHOICES = [
        ('Reimbursable', 'Reimbursable'),
        ('Company Paid', 'Company Paid'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    expense_id = models.CharField(max_length=20, unique=True, editable=False)  # Auto-generated ID

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses')

    expense_title = models.CharField(max_length=100, null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, null=True, blank=True)

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='expenses', null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)

    expense_date = models.DateField(default=timezone.now, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    paid_by = models.CharField(max_length=50, choices=PAID_BY_CHOICES, null=True, blank=True)
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPE_CHOICES, null=True, blank=True)

    receipt_upload = models.FileField(upload_to='expense_receipts/', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.expense_id:
            last_expense = Expense.objects.all().order_by('id').last()
            if last_expense:
                last_id_num = int(last_expense.expense_id.split('-')[1])
                self.expense_id = f"EXP-{last_id_num + 1:04d}"
            else:
                self.expense_id = "EXP-0001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.expense_title} - ₹{self.amount}"



