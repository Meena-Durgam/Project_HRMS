from django.db import models
from accounts.models import Company, CustomUser
from department.models import Department
from designation.models import Designation
from employee.models import Employee  # ✅ Correct import


class Promotion(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='promotions'
    )

    # ✅ Do not use to_field — use default PK
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='promotions'
    )

    old_department = models.ForeignKey(
        Department,
        related_name='promotions_old',
        on_delete=models.CASCADE
    )
    old_designation = models.ForeignKey(
        Designation,
        related_name='promotions_old',
        on_delete=models.CASCADE
    )
    new_department = models.ForeignKey(
        Department,
        related_name='promotions_new',
        on_delete=models.CASCADE
    )
    new_designation = models.ForeignKey(
        Designation,
        related_name='promotions_new',
        on_delete=models.CASCADE
    )

    promotion_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_promotions'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "promotion"
        ordering = ['-promotion_date']

    def __str__(self):
        return f"Promotion of {self.employee} from {self.old_designation} to {self.new_designation}"
