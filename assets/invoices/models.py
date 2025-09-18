from django.db import models
from django.utils import timezone
from decimal import Decimal
from django.db.models import Sum

from accounts.models import Company
from clients.models import Client
from projects.models import Project
from tax.models import Tax
from estimate.models import Estimate


class Invoice(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Paid', 'Paid'),
        ('Unpaid', 'Unpaid'),
        ('Overdue', 'Overdue'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, editable=False)
    estimate = models.ForeignKey(Estimate, on_delete=models.SET_NULL, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)

    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField()

    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    tax = models.ForeignKey(Tax, on_delete=models.SET_NULL, null=True, blank=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))  # % value
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'invoice_number')

    def generate_invoice_number(self):
        last = Invoice.objects.filter(company=self.company).order_by('id').last()
        if not last or not last.invoice_number:
            return "INV-001"
        try:
            invoice_int = int(last.invoice_number.split('-')[-1])
        except ValueError:
            invoice_int = 0
        return f"INV-{invoice_int + 1:03d}"

    def calculate_totals(self):
        self.total_amount = self.items.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Apply discount first
        discount_amount = (self.discount / Decimal('100.00')) * self.total_amount
        discounted_total = self.total_amount - discount_amount

        # Apply tax on discounted amount
        tax_rate = Decimal('0.00')
        if self.tax and getattr(self.tax, 'status', '') == 'Active':
            tax_rate = self.tax.percentage / Decimal('100.00')

        self.tax_amount = discounted_total * tax_rate

        # Final total
        self.grand_total = discounted_total + self.tax_amount

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = self.generate_invoice_number()

        # First save to get invoice ID for item relationships
        super().save(*args, **kwargs)

        # Calculate and update totals
        self.calculate_totals()

        # Save only the calculated fields
        super().save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

    def __str__(self):
        return f"Invoice #{self.invoice_number} - {self.client.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), editable=False)

    def save(self, *args, **kwargs):
        self.amount = self.unit_cost * self.quantity
        super().save(*args, **kwargs)

        # Recalculate invoice totals after saving item
        self.invoice.calculate_totals()
        self.invoice.save(update_fields=['total_amount', 'tax_amount', 'grand_total'])

    def __str__(self):
        return f"{self.item_name} - {self.invoice.invoice_number}"
