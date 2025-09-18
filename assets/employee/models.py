from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, EmailValidator, MinValueValidator, MaxValueValidator
from accounts.models import Company, CustomUser
from department.models import Department
from designation.models import Designation

# Validators
phone_validator = RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid phone number.")
pan_validator = RegexValidator(regex=r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', message="Enter a valid PAN number.")
IFSC_CODE_VALIDATOR = RegexValidator(
    regex=r'^[A-Z]{4}[A-Z0-9]{7}$',
    message='Enter a valid IFSC code (e.g., HDFC0001234)'
)
aadhaar_validator = RegexValidator(regex=r'^\d{12}$', message="Enter a valid 12-digit Aadhaar number.")

class Employee(models.Model):
    STATUS_CHOICES = [('Active', 'Active'), ('Inactive', 'Inactive'), ('Pending', 'Pending Approval')]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='employees')
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_account')

    first_name = models.CharField(max_length=100,verbose_name='First Name')
    last_name = models.CharField(max_length=100,verbose_name='Last Name')
    email = models.EmailField(unique=True, null=True, blank=True, validators=[EmailValidator()],verbose_name='Email')
    employee_id = models.CharField(max_length=10, blank=True)

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, limit_choices_to={'status': 'Active'})
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, limit_choices_to={'status': 'Active'})

    joining_date = models.DateField(verbose_name='Joining Date')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'employee'
        unique_together = ('company', 'employee_id')

    def save(self, *args, **kwargs):
        if self.user:
            self.user.role = 'employee'
            self.user.first_name = self.first_name
            if self.email:
                self.user.email = self.email
            self.user.save()

        if not self.employee_id:
            current_year = timezone.now().year
            prefix = str(current_year)
            last_emp = Employee.objects.filter(company=self.company, employee_id__startswith=prefix).order_by('-id').first()
            next_num = int(last_emp.employee_id[-2:]) + 1 if last_emp and last_emp.employee_id[-2:].isdigit() else 1
            self.employee_id = f"{prefix}{next_num:02d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"


from django.db import models
from django.core.validators import EmailValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import re

def phone_validator(value):
    if not re.fullmatch(r'\d{10}', value):
        raise ValidationError("Phone number must be exactly 10 digits.")

class EmployeeProfile(models.Model):
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    MARITAL_CHOICES = [('Married', 'Married'), ('Unmarried', 'Unmarried')]
    RELIGION_CHOICES = [('Hindu', 'Hindu'),('Muslim', 'Muslim'),('Buddhist', 'Buddhist'),('Sikh', 'Sikh'),('Jain', 'Jain'),('Christian','Christian'),]
    Nationality_choices = [
    ('India', 'Indian'),
    ('United States', 'American'),
    ('United Kingdom', 'British'),
    ('Canada', 'Canadian'),
    ('Germany', 'German'),
    ('France', 'French'),
    ('China', 'Chinese'),
    ('Japan', 'Japanese'),
    ('Brazil', 'Brazilian'),
    ('South Africa', 'South African'),
]

    employee = models.OneToOneField(
        'Employee', on_delete=models.CASCADE,
        related_name='profile', verbose_name='Employee'
    )

    profile_picture = models.ImageField(
        upload_to='employee/profile_pictures/', blank=True, null=True,
        verbose_name='Profile Picture'
    )
    phone = models.CharField(
        max_length=20, validators=[phone_validator],
        blank=True, null=True, verbose_name='Phone Number'
    )
    
    birthday = models.DateField(
        blank=True, null=True, verbose_name='Birthday'
    )
    address = models.TextField(
        blank=True, null=True, verbose_name='Address'
    )
    gender = models.CharField(
        max_length=10, choices=GENDER_CHOICES,
        blank=True, null=True, verbose_name='Gender'
    )
    nationality = models.CharField(
        max_length=50, blank=True,choices=Nationality_choices, null=True, verbose_name='Nationality'
    )
    religion = models.CharField(
        max_length=50, blank=True, null=True,choices=RELIGION_CHOICES ,verbose_name='Religion'
    )
    marital_status = models.CharField(
        max_length=20, choices=MARITAL_CHOICES,
        blank=True, null=True, verbose_name='Marital Status'
    )
    aadhaar_number = models.CharField(
        max_length=12, blank=True, null=True, verbose_name='Aadhaar Number'
    )

    passport_no = models.CharField(
        max_length=50, blank=True, null=True, verbose_name='Passport Number'
    )
    passport_expiry = models.DateField(
        blank=True, null=True, verbose_name='Passport Expiry'
    )
    number_of_children = models.PositiveIntegerField(
        blank=True, null=True, validators=[MinValueValidator(0)],
        verbose_name='Number Of Children'
    )

    is_completed = models.BooleanField(default=False, verbose_name='Is Completed')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Completed At')
    is_approved = models.BooleanField(default=False, verbose_name='Is Approved')

    class Meta:
        db_table = 'employee_profile'
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"

    def __str__(self):
        return f"Profile: {self.employee}"

    def check_profile_completion(self):
        emp = self.employee

        # Check essential fields in EmployeeProfile
        profile_fields_complete = all([
            self.phone,
            self.address,
            self.gender
        ])

        # Check related models (except experience & salaryandstatutory)
        related_data_complete = (
            emp.emergency_contacts.exists() and
            emp.education.exists() and
            hasattr(emp, 'bankdetails')  # bank details is mandatory
            # ✅ salaryandstatutory and experiences are excluded from required list
        )

        if profile_fields_complete and related_data_complete:
            if not self.is_completed:
                self.is_completed = True
                self.completed_at = timezone.now()
                self.save(update_fields=['is_completed', 'completed_at'])
        else:
            # Optional: mark as not completed if any of them becomes invalid again
            if self.is_completed:
                self.is_completed = False
                self.completed_at = None
                self.save(update_fields=['is_completed', 'completed_at'])


class EmergencyContact(models.Model):
    RELATIONSHIP_CHOICES = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('guardian', 'Guardian'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)  # Dropdown list
    phone = models.CharField(max_length=50, validators=[phone_validator])

    class Meta:
        db_table = 'emergency_contact'


from datetime import datetime

def get_current_year():
    return str(datetime.now().year)

class Education(models.Model):
    DEGREE_CHOICES = [
        ('SSLC', 'SSLC (10th)'),
        ('PUC', 'PUC (12th)'),
        ('Diploma', 'Diploma'),
        ('UG', 'Under Graduate'),
        ('PG', 'Post Graduate'),
    ]

    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='education')
    degree_type = models.CharField(max_length=10, choices=DEGREE_CHOICES)
    institution_name = models.CharField(max_length=255, null=True)
    program = models.CharField(max_length=100, blank=True)
    stream = models.CharField(max_length=100, blank=True)
    from_year = models.CharField(max_length=10)
    to_year = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.degree_type} - {self.institution_name}"

    class Meta:
        unique_together = ('employee', 'degree_type')  # 🔒 Ensures no duplicate degree per employee

from dateutil.relativedelta import relativedelta

class Experience(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=150)
    start_date = models.DateField(null=True, blank=True, verbose_name="Start Date")
    end_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True)


    def save(self, *args, **kwargs):
        if self.start_date and self.end_date:
            from dateutil.relativedelta import relativedelta
            delta = relativedelta(self.end_date, self.start_date)
            years = delta.years
            months = delta.months
            parts = []
            if years:
                parts.append(f"{years} year{'s' if years > 1 else ''}")
            if months:
                parts.append(f"{months} month{'s' if months > 1 else ''}")
            self.duration = ' '.join(parts) if parts else 'Less than a month'
        else:
            self.duration = ''
        super().save(*args, **kwargs)

    class Meta:
        db_table ='experience'


class BankDetails(models.Model):
    employee = models.OneToOneField('Employee', on_delete=models.CASCADE, verbose_name="Employee")

    bank_name = models.CharField(
        max_length=100,
        verbose_name="Bank Name"
    )

    account_no = models.CharField(
        max_length=50,
        validators=[RegexValidator(regex=r'^\d{9,18}$', message='Enter a valid account number')],
        verbose_name="Account Number"
    )

    ifsc_code = models.CharField(
    max_length=20,
    verbose_name='IFSC Code'
)

    class Meta:
        verbose_name = "Bank Detail"
        verbose_name_plural = "Bank Details"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee} - {self.bank_name}"


from django.db import models
from django.utils import timezone

class SalaryAndStatutory(models.Model):
    SALARY_BASIS_CHOICES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    PAYMENT_TYPE_CHOICES = [
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('cash', 'Cash'),
    ]

    YES_NO_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    RATE_CHOICES = [(f'{i}%', f'{i}%') for i in range(0, 11)]

    employee = models.OneToOneField("Employee", on_delete=models.CASCADE)

    # Basic Salary Info
    salary_basis = models.CharField(max_length=10, choices=SALARY_BASIS_CHOICES)
    salary_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, blank=True)

    # PF Info
    pf_contribution = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    pf_number = models.CharField(max_length=100, blank=True, null=True)
    employee_pf_rate = models.CharField(max_length=10, choices=RATE_CHOICES, blank=True)
    additional_pf_rate = models.CharField(max_length=10, choices=RATE_CHOICES, blank=True)
    total_pf_rate = models.CharField(max_length=10, blank=True)

    # ESI Info
    esi_contribution = models.CharField(max_length=3, choices=YES_NO_CHOICES)
    esi_number = models.CharField(max_length=100, blank=True, null=True)
    employee_esi_rate = models.CharField(max_length=10, choices=RATE_CHOICES, blank=True)
    additional_esi_rate = models.CharField(max_length=10, choices=RATE_CHOICES, blank=True)
    total_esi_rate = models.CharField(max_length=10, blank=True)

    # Approval
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'salary_and_statutory'

    def mark_approved(self, approved_by_user):
        if approved_by_user.role != 'company_owner':
            raise PermissionError("Only company owners can approve.")
        if not self.is_approved:
            self.is_approved = True
            self.approved_at = timezone.now()
            self.save(update_fields=['is_approved', 'approved_at'])

class FamilyMember(models.Model):
    RELATIONSHIP_CHOICES = [
        ('Father', 'Father'),
        ('Mother', 'Mother'),
        ('Son', 'Son'),
        ('Daughter', 'Daughter'),
        ('Sister', 'Sister'),
        ('Brother', 'Brother'),
        ('Guardian', 'Guardian'),
    ]
    YES_NO_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

    employee = models.ForeignKey(Employee, related_name='family_members', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="DOB")
    occupation = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    dependent = models.CharField(
    max_length=3,
    choices=YES_NO_CHOICES,
    verbose_name='Dependent?'
)


    def __str__(self):
        return f"{self.name} ({self.relationship})"
    


from django.db import models

# --- Education Document Section ---

EDUCATION_TYPE_CHOICES = [
    ('10th Certificate', '10th Certificate'),
    ('PUC', 'PUC'),
    ('Diploma', 'Diploma'),
    ('Degree', 'Degree'),
    ('Masters', 'Masters'),
    ('Other', 'Other'),
]

def upload_education_doc_path(instance, filename):
    return f"documents/education/{instance.employee.id}/{filename}"

class EducationDocument(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='education_documents')
    document_type = models.CharField(max_length=50, choices=EDUCATION_TYPE_CHOICES)
    other_document_type = models.CharField(max_length=100, blank=True, null=True)  # Manual input for 'Other'
    document_file = models.FileField(upload_to=upload_education_doc_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        doc_name = self.other_document_type if self.document_type == 'Other' else self.document_type
        return f"{doc_name} ({self.employee})"

# --- Government Document Section ---

GOVERNMENT_TYPE_CHOICES = [
    ('Aadhaar Card', 'Aadhaar Card'),
    ('PAN Card', 'PAN Card'),
    ('Passport', 'Passport'),
    ('Voter ID', 'Voter ID'),
    ('Driving License', 'Driving License'),
    ('Other', 'Other'),
]

def upload_government_doc_path(instance, filename):
    return f"documents/government/{instance.employee.id}/{filename}"

class GovernmentDocument(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='government_documents')
    document_type = models.CharField(max_length=50, choices=GOVERNMENT_TYPE_CHOICES)
    other_document_type = models.CharField(max_length=100, blank=True, null=True)  # Manual input for 'Other'
    document_file = models.FileField(upload_to=upload_government_doc_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        doc_name = self.other_document_type if self.document_type == 'Other' else self.document_type
        return f"{doc_name} ({self.employee})"
