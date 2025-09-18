from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from django.db import models
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError

def validate_image_format(value):
    valid_mime_types = ['image/jpeg', 'image/png']
    file_mime_type = value.file.content_type
    if file_mime_type not in valid_mime_types:
        raise ValidationError('Only JPEG and PNG image formats are allowed.')

class Company(models.Model):
    COMPANY_SIZE_CHOICES = (
        ('small', 'Small (1–50)'),
        ('medium', 'Medium (51–250)'),
        ('large', 'Large (250+)'),
    )

    INDUSTRY_CHOICES = (
        ('it', 'Information Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('manufacturing', 'Manufacturing'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')]
    )
    address = models.TextField()

    size = models.CharField(max_length=10, choices=COMPANY_SIZE_CHOICES)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES)
    website = models.URLField(
    validators=[URLValidator()]
)
    logo = models.ImageField(
        upload_to='company_logos/',
        validators=[validate_image_format],
    )
    # Status flags
    is_active = models.BooleanField(default=True)
    complete_profile = models.BooleanField(default=False, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or "Unconfigured Company"

    def is_profile_complete(self):
        """Returns True only if all critical fields are filled."""
        required_fields = [
            self.name, self.email, self.phone, self.address,
            self.size, self.industry, self.logo,
        ]
        return all(bool(field) for field in required_fields)

    def save(self, *args, **kwargs):
        # Check if profile is complete
        self.complete_profile = self.is_profile_complete()

        # Auto-activate company only if profile is complete
        if self.complete_profile:
            self.is_active = True
        else:
            self.is_active = False  # Optional: auto-deactivate if profile becomes incomplete

        super().save(*args, **kwargs)




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email Field Must Be Set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'superadmin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # ✅ Disable username
    email = models.EmailField(('email address'), unique=True)

    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('company_owner', 'Company Owner'),
        ('employee', 'Employee'),
        ('jobseeker', 'Jobseeker'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'email'  # ✅ Use email as login
    REQUIRED_FIELDS = []

    objects = CustomUserManager()  # ✅ ADD THIS LINE

    def __str__(self):
        return self.email
