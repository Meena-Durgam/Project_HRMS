from django.db import models
from django.utils import timezone
from employee.models import Employee
from accounts.models import Company  # Assuming this is your Company model

STATUS_CHOICES = (
    ('Present', 'Present'),
    ('Absent', 'Absent'),
    ('Leave', 'Leave'),
)

class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)  # 🔹 Multi-company support

    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    location = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='attendance_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # ✅ Check-in and Check-out Time
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)

    production_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    break_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('employee', 'date')  # Prevent duplicate entries per day
        db_table = 'attendance'

    def __str__(self):
        return f"{self.employee} - {self.date} - {self.status}"

    def total_worked_hours(self):
        """
        Returns total worked hours (check_out - check_in) in float.
        """
        if self.check_in_time and self.check_out_time:
            in_dt = timezone.make_aware(timezone.datetime.combine(self.date, self.check_in_time))
            out_dt = timezone.make_aware(timezone.datetime.combine(self.date, self.check_out_time))
            duration = out_dt - in_dt
            return round(duration.total_seconds() / 3600, 2)
        return 0.0


class BreakTime(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='breaks')
    break_start = models.DateTimeField()
    break_end = models.DateTimeField(null=True, blank=True)

    def duration_minutes(self):
        if self.break_end:
            return (self.break_end - self.break_start).total_seconds() / 60
        return 0

    class Meta:
        db_table = 'break_time'

    def __str__(self):
        return f"Break for {self.attendance.employee} on {self.attendance.date}"
