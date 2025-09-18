from django.db import models
from employee.models import Employee
from department.models import Department
from accounts.models import Company  # Adjust if path differs
from ckeditor.fields import RichTextField
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Internship', 'Internship'),
    ]

    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Cancelled', 'Cancelled'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs', null=True, blank=True)
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    location = models.CharField(max_length=200)
    vacancies = models.IntegerField()
    experience = models.CharField(max_length=100)
    salary_from = models.DecimalField(max_digits=10, decimal_places=2)
    salary_to = models.DecimalField(max_digits=10, decimal_places=2)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    start_date = models.DateField()
    expired_date = models.DateField()
    description = RichTextField()

    def __str__(self):
        return self.title


class JobApplicant(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('hired', 'Hired'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='job_applicants', null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applicants')
    jobseeker_profile = models.ForeignKey(
        'jobseeker.JobSeekerProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    apply_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_mode = models.CharField(max_length=20, choices=[('Online', 'Online'), ('Offline', 'Offline')], null=True, blank=True)
    interview_message = models.TextField(null=True, blank=True)
    is_internal = models.BooleanField(default=False)
    meeting_link = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('hired', 'Hired'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('rejected', 'Rejected'),
    ]

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name='job_applications',
        null=True, blank=True  # Null for jobseeker applications
    )
    applicant = models.ForeignKey(
        JobApplicant, on_delete=models.CASCADE,
        related_name='applications', null=True, blank=True
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE,
        null=True, blank=True
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def __str__(self):
        if self.employee:
            return f"{self.employee.first_name} {self.employee.last_name} - {self.job.title} ({self.status})"
        elif self.applicant:
            return f"{self.applicant.name} - {self.job.title} ({self.status})"
        return f"Unknown Applicant - {self.job.title} ({self.status})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.applicant and not self.employee:
            raise ValidationError("Either applicant or employee must be provided.")
        if self.applicant and self.employee:
            raise ValidationError("Only one of applicant or employee should be provided.")
        if self.employee and not self.company:
            raise ValidationError("Company must be provided for employee applications.")

from django.contrib.auth import get_user_model


from django.db import models
from django.contrib.auth import get_user_model
from jobs.models import Job, JobApplication

class InterviewRound(models.Model):
    STATUS_CHOICES = [
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    ]

    application = models.ForeignKey(
        JobApplication,
        on_delete=models.CASCADE,
        related_name='interview_rounds'
    )

    round_number = models.PositiveIntegerField()  # ✅ Now free input — not limited to choices
    round_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional: HR Round, Technical Round, etc."
    )

    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)

    interview_mode = models.CharField(
        max_length=20,
        choices=[('Online', 'Online'), ('Offline', 'Offline')],
        null=True,
        blank=True
    )
    meeting_link = models.URLField(null=True, blank=True)
    venue_details = models.TextField(null=True, blank=True)

    feedback = models.TextField(null=True, blank=True)
    interviewed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    feedback_given_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('application', 'round_number')  # Prevents duplicate rounds
        ordering = ['round_number']

    def __str__(self):
        return f"Round {self.round_number} ({self.round_type}) - {self.application}"

    
from django.db import models
from django.utils import timezone

class OfferLetter(models.Model):
    application = models.OneToOneField("JobApplication", on_delete=models.CASCADE, related_name='offer_letter')
    applicant_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=200)
    company_name = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    offer_date = models.DateField(default=timezone.now)
    pdf = models.FileField(upload_to='offer_letters/', null=True, blank=True)
    

    def __str__(self):
        return f"Offer Letter for {self.applicant_name} - {self.job_title}"
