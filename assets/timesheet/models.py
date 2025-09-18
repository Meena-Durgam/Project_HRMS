from django.db import models
from django.db.models import Sum
from employee.models import Employee  # Corrected import based on your actual structure
from projects.models import Project
from accounts.models import Company


class Timesheet(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    date = models.DateField()
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Remaining project hours
    task_description = models.TextField()
    task_file = models.FileField(upload_to='task_files/', null=True, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - {self.project.name} - {self.status}"

    def save(self, *args, **kwargs):
        # Step 1: Calculate hours from clock_in and clock_out
        actual_hours = 0
        if self.clock_in and self.clock_out:
            delta = self.clock_out - self.clock_in
            actual_hours = round(delta.total_seconds() / 3600, 2)
            self.total_hours = actual_hours

        # Step 2: Save this Timesheet instance first
        super().save(*args, **kwargs)

        # Step 3: Ensure multi-company consistency
        if self.employee.company != self.project.company:
            raise ValueError("Employee and Project must belong to the same company.")

        # Step 4: Sum all logged hours for this project under the same company
        total_logged = Timesheet.objects.filter(
            project=self.project,
            employee__company=self.employee.company
        ).aggregate(total=Sum('total_hours'))['total'] or 0

