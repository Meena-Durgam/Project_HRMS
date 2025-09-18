from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum
from clients.models import Client
from projects.models import Project
from tax.models import Tax
from accounts.models import Company

class Estimate(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='estimates')  # 👈 Company scope
    estimate_number = models.CharField(max_length=100, editable=False)  # Removed unique=True for per-company control

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, blank=True, null=True)
    

    estimate_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    billing_address = models.TextField(blank=True, null=True)
    other_information = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'estimate_number')  # ✅ Ensure uniqueness per company

    def generate_estimate_number(self):
        last_estimate = Estimate.objects.filter(company=self.company).order_by('id').last()
        if not last_estimate or not last_estimate.estimate_number:
            return "EST-00001"

        try:
            last_number = int(last_estimate.estimate_number.split('-')[-1])
            next_number = last_number + 1
        except (IndexError, ValueError):
            next_number = 1

        return f"EST-{next_number:05d}"

    def calculate_totals(self):
        total = self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        
        # Apply discount first
        discount_percent = self.discount or Decimal('0.00')
        discount_amount = (discount_percent / Decimal('100.00')) * total
        discounted_total = total - discount_amount

        # Then apply tax on discounted total
        tax_rate = Decimal('0.00')
        if self.tax and self.tax.status == 'Active':
            tax_rate = self.tax.percentage / Decimal('100.00')

        tax_amount = discounted_total * tax_rate
        grand_total = discounted_total + tax_amount

        # Save computed values
        self.total_amount = total  # Before discount
        self.tax_amount = tax_amount
        self.grand_total = grand_total


    def save(self, *args, **kwargs):
        if not self.estimate_number:
            self.estimate_number = self.generate_estimate_number()

        super().save(*args, **kwargs)  # Save first so that related items exist
        self.calculate_totals()
        super().save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

    def __str__(self):
        return f"Estimate #{self.estimate_number} - {self.client.client_name}"


class EstimateItem(models.Model):
    estimate = models.ForeignKey(Estimate, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    def save(self, *args, **kwargs):
        self.amount = self.unit_cost * self.quantity
        super().save(*args, **kwargs)
        self.estimate.calculate_totals()
        self.estimate.save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

    def __str__(self):
        return f"{self.item_name} - {self.estimate.estimate_number}"
