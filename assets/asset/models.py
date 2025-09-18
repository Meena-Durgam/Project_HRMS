from django.db import models
from django.utils import timezone
from employee.models import Employee  # Adjust if located elsewhere

ASSET_STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Approved', 'Approved'),
    ('Returned', 'Returned'),
]

class Asset(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='assets')
    name = models.CharField(max_length=100)
    asset_id = models.CharField(max_length=20, unique=True, blank=True)
    purchase_date = models.DateField(blank=True)
    warranty = models.PositiveIntegerField(default=12)

    warranty_end = models.DateField(blank=True, null=True)

    value = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=ASSET_STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.asset_id:
            current_year = timezone.now().year
            prefix = f"AST{current_year}"
            last_asset = Asset.objects.filter(asset_id__startswith=prefix).order_by('-id').first()
            next_id = int(last_asset.asset_id[-4:]) + 1 if last_asset and last_asset.asset_id[-4:].isdigit() else 1
            self.asset_id = f"{prefix}{next_id:04d}"
        if self.purchase_date and self.warranty:
            self.warranty_end = self.purchase_date + timezone.timedelta(days=30*self.warranty)
        super().save(*args, **kwargs)


    def _str_(self):
        return f"{self.name} ({self.asset_id})"