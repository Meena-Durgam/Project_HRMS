import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils import timezone
from django.forms.widgets import DateInput, PasswordInput, EmailInput, TextInput, Select, Textarea
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.auth.password_validation import validate_password

from .models import (
    Employee, EmployeeProfile, EmergencyContact,
    Education, Experience, BankDetails, SalaryAndStatutory
)
from designation.models import Designation
from accounts.models import CustomUser

from django import forms
from django.core.exceptions import ValidationError
from django.forms import TextInput, EmailInput, PasswordInput, DateInput, Select
from django.utils import timezone
import re
from django.contrib.auth.password_validation import validate_password

from .models import Employee, Designation, CustomUser


class EmployeeForm(forms.ModelForm):
    password = forms.CharField(
        widget=PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Password'
        }),
        required=True  # required only on create
    )
    email = forms.EmailField(
        widget=EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Email'
        }),
        required=True
    )

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'email', 'password',
            'department', 'designation', 'joining_date', 'status'
        ]
        widgets = {
            'first_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter First Name'
            }),
            'last_name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Last Name'
            }),
            'department': Select(attrs={'class': 'form-control select-arrow-spacing'}),
            'designation': Select(attrs={
                'class': 'form-control select-arrow-spacing',
            }),
            'joining_date': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'status': Select(attrs={'class': 'form-control select-arrow-spacing'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Optional fields
        self.fields['last_name'].required = False
        self.fields['designation'].queryset = Designation.objects.none()

        # Filter departments by company
        if self.company:
            self.fields['department'].queryset = self.company.departments.filter(status='Active')

        # Populate designation based on department
        if 'department' in self.data:
            try:
                dept_id = int(self.data.get('department'))
                self.fields['designation'].queryset = Designation.objects.filter(
                    department_id=dept_id, status='Active'
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.department:
            self.fields['designation'].queryset = Designation.objects.filter(
                department=self.instance.department, status='Active'
            )

        # Empty labels
        self.fields['department'].empty_label = "Select Department"
        self.fields['designation'].empty_label = "Select Designation"
        status_choices = list(self.fields['status'].choices)
        if status_choices and status_choices[0][0] == '':
            status_choices.pop(0)
        self.fields['status'].choices = [('', 'Select Status')] + status_choices

        # Create vs Edit mode
        if self.instance.pk:
            # Editing existing employee
            self.fields['joining_date'].widget.attrs['readonly'] = True  # make readonly
            self.fields['joining_date'].required = False
            self.fields['password'].required = False
            self.fields['password'].widget.attrs['placeholder'] = "Leave blank to keep current password"
        else:
            # Creating new employee
            today = timezone.now().date()
            self.fields['joining_date'].widget.attrs.update({
                'min': today.isoformat(),
            })
            self.fields['joining_date'].initial = today   # pre-fill with today
            self.fields['joining_date'].required = True
            self.fields['password'].required = True

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not self.instance.pk and CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        if self.instance.pk and CustomUser.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError("This email is already registered by another user.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.instance.pk:
            if password:
                self._validate_password_strength(password)
            return password
        else:
            if not password:
                raise ValidationError("Password is required.")
            self._validate_password_strength(password)
            return password

    def _validate_password_strength(self, password):
        """Custom password strength validation"""
        first_name = self.cleaned_data.get('first_name', '')
        last_name = self.cleaned_data.get('last_name', '')
        email = self.cleaned_data.get('email', '')
        email_user = email.split('@')[0].lower() if email else ''

        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[\W_]', password):
            raise ValidationError("Password must contain at least one special character.")

        lowered = password.lower()
        if first_name and first_name.lower() in lowered:
            raise ValidationError("Password should not contain your first name.")
        if last_name and last_name.lower() in lowered:
            raise ValidationError("Password should not contain your last name.")
        if email_user and email_user in lowered:
            raise ValidationError("Password should not contain part of your email.")

        validate_password(password)

    def save(self, commit=True):
        instance = super().save(commit=False)
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        password = self.cleaned_data.get('password')

        if not instance.user_id:
            # Create new user
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                role='employee',
                company=self.company,
                first_name=first_name
            )
            instance.user = user
        else:
            # Update existing user
            user = instance.user
            user.email = email
            user.first_name = first_name
            if password:
                user.set_password(password)
            user.save()

        # Sync employee details
        instance.email = email
        instance.company = self.company

        if commit:
            instance.save()

        return instance




import requests
import re
from django import forms
from django.utils.html import format_html
from django.forms import DateInput, Select
from django.core.exceptions import ValidationError
from .models import EmployeeProfile

aadhaar_validator = re.compile(r'^\d{12}$')

# API for country dropdown
def get_country_choices():
    # Fallback list with country and nationality
    fallback = [
        ('India', 'Indian'),
        ('United States', 'American'),
        ('United Kingdom', 'British'),
        ('Canada', 'Canadian'),
        ('Germany', 'German'),
        ('France', 'French'),
        ('China', 'Chinese'),
        ('Japan', 'Japanese'),
        ('Brazil', 'Brazilian'),
        ('South Africa', 'South African')
    ]

    try:
        response = requests.get("https://restcountries.com/v3.1/all", timeout=5)
        response.raise_for_status()
        countries = response.json()
        # Build a list of (Country Name, Country Name) from the API
        dynamic_countries = sorted([
            (c['name']['common'], c['name']['common']) 
            for c in countries if 'name' in c and 'common' in c['name']
        ])
        return dynamic_countries
    except Exception:
        # Use fallback list with common nationalities
        return fallback

from django import forms
from django.forms import DateInput, Textarea, Select
from django.core.exceptions import ValidationError
import re
from .models import EmployeeProfile

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        exclude = ['is_completed', 'completed_at', 'is_approved', 'employee']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={
                'accept': '.jpg, .jpeg, .png',
                'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter 10-digit phone number',
                'class': 'form-control'
            }),
            'birthday': DateInput(attrs={
                'type': 'date',
                'class': 'form-control text-uppercase',
                'placeholder': 'DD/MM/YYYY',
                'autocomplete': 'off'
            }),
            'address': Textarea(attrs={
                'rows': 1,
                'style': 'resize: none;',
                'class': 'form-control',
                'placeholder': 'Enter Address'
            }),
            'gender': Select(attrs={'class': 'form-control select-arrow-spacing'}),
            'nationality': Select(attrs={'class': 'form-control select-arrow-spacing'}),
            'religion': Select(attrs={'class': 'form-control select-arrow-spacing'}),
            'marital_status': Select(attrs={'class': 'form-control select-arrow-spacing'}),
            'aadhaar_number': forms.TextInput(attrs={
                'placeholder': 'XXXX XXXX XXXX',
                'class': 'form-control'
            }),
            'passport_no': forms.TextInput(attrs={
    'placeholder': 'Enter Passport Number',
    'class': 'form-control',
    'pattern': '[0-9]*',        # Only digits
    'inputmode': 'numeric',     # Mobile-friendly numeric keyboard
    'oninput': "this.value = this.value.replace(/[^0-9]/g, '')"  # Live filtering
}),

            'passport_expiry': DateInput(attrs={
                'type': 'date',
                'class': 'form-control text-uppercase',
                'placeholder': 'DD/MM/YYYY',
                'autocomplete': 'off'
            }),
            'number_of_children': forms.NumberInput(attrs={
                'min': 0,
                'placeholder': 'Enter number of children',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.profile_picture_uploaded = bool(self.instance and self.instance.profile_picture)

        # Set choices from model directly
        self.fields['gender'].choices = [('', 'Select Gender')] + list(EmployeeProfile.GENDER_CHOICES)
        self.fields['religion'].choices = [('', 'Select Religion')] + list(EmployeeProfile.RELIGION_CHOICES)
        self.fields['marital_status'].choices = [('', 'Select Marital Status')] + list(EmployeeProfile.MARITAL_CHOICES)
        self.fields['nationality'].choices=[('','Select Nationality')]+ list(EmployeeProfile.Nationality_choices)
        # Optional Fields
        optional_fields = ['passport_no', 'passport_expiry', 'number_of_children']
        for name, field in self.fields.items():
            self.label_suffix = ""
            field.widget.attrs.setdefault('class', 'form-control')
            field.required = name not in optional_fields

            label = (field.label or name.replace('_', ' ').capitalize()).rstrip(':')
            if field.required:
                field.label = format_html('{} <span class="text-danger">*</span>', label)
            else:
                field.label = label

        self.fields['number_of_children'].initial = 0

        if self.instance and hasattr(self.instance, 'employee'):
            employee = self.instance.employee
            self.email_display = employee.email or getattr(employee.user, 'email', '')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not re.fullmatch(r'\d{10}', phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_aadhaar_number(self):
        aadhaar = self.cleaned_data.get('aadhaar_number')
        if aadhaar and not re.fullmatch(r'\d{12}', aadhaar):
            raise ValidationError("Please enter a valid 12-digit Aadhaar Number.")
        return aadhaar

    def clean_profile_picture(self):
        image = self.cleaned_data.get('profile_picture')
        if image:
            if hasattr(image, 'content_type') and image.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
                raise ValidationError("Only JPG, JPEG, and PNG files are allowed.")
        return image

    def clean(self):
        cleaned_data = super().clean()

        marital_status = cleaned_data.get('marital_status')
        number_of_children = cleaned_data.get('number_of_children')

        if marital_status == 'Married':
            if number_of_children in [None, '']:
                self.add_error('number_of_children', 'This field is required for married employees.')
            elif int(number_of_children) < 0:
                self.add_error('number_of_children', 'Number of children cannot be negative.')
        else:
            cleaned_data['number_of_children'] = 0

        default_map = {
            'phone': 'N/A',
            'email': 'N/A',
            'address': 'N/A',
            'birthday': '2000-01-01',
            'gender': 'Male',
            'nationality': 'Indian',
            'religion': 'Hindu',
            'marital_status': 'Unmarried',
            'aadhaar_number': '000000000000',
        }

        for field, default in default_map.items():
            if not cleaned_data.get(field):
                cleaned_data[field] = default

        return cleaned_data


    
from django import forms
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import EmergencyContact
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import EmergencyContact

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html
from .models import EmergencyContact

from django import forms
from django.utils.html import format_html
from django.forms import modelformset_factory
from .models import EmergencyContact


from django import forms
from django.utils.html import format_html
from .models import EmergencyContact

from django import forms
from django.forms import modelformset_factory, HiddenInput
from django.utils.html import format_html
from .models import EmergencyContact

from django import forms
from django.forms import HiddenInput, modelformset_factory
from django.utils.html import format_html
from django import forms
from django.forms import TextInput
from .models import EmergencyContact

from django import forms
from django.core.exceptions import ValidationError
from .models import EmergencyContact
import re

class EmergencyContactForm(forms.ModelForm):
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Full Name',
                'required': True,
            }),
            'relationship': forms.Select(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit Phone Number',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)

        # If it's a ForeignKey field -> override empty_label
        if hasattr(self.fields['relationship'], 'empty_label'):
            self.fields['relationship'].empty_label = "Select Relationship"

        # If it's a ChoiceField (with predefined choices in model)
        if self.fields['relationship'].choices:
            self.fields['relationship'].choices = [("", "Select Relationship")] + list(self.fields['relationship'].choices)[1:]

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        if not phone.isdigit():
            raise ValidationError("Phone number must contain only digits.")
        if len(phone) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")

        return phone

    def clean(self):
        cleaned_data = super().clean()

        if self.employee and not self.instance.pk:
            existing_count = EmergencyContact.objects.filter(employee=self.employee).count()
            if existing_count >= 2:
                raise ValidationError("You can only add up to 2 emergency contacts.")

        return cleaned_data



# =========================
# ✅ Emergency Contact FormSet Factory
# =========================
EmergencyContactFormSet = modelformset_factory(
    EmergencyContact,
    form=EmergencyContactForm,
    extra=1,          # You can change this to 0 if you don’t want blank form initially
    max_num=2,
    validate_max=True,
    can_delete=True   # Allow delete checkbox in template
)

from django import forms
from django.core.exceptions import ValidationError
from .models import BankDetails
import re

# Validators
account_validator = re.compile(r'^\d{9,}$')  # Only integers, min 9 digits
ifsc_validator = re.compile(r'^[A-Za-z]{4}\d{7}$')  # 4 letters + 7 digits

import re
from django import forms
from django.core.exceptions import ValidationError
from .models import BankDetails

# Define your validators (adjust if not defined elsewhere)
# ✅ Updated Validators
import re
from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import format_html

account_validator = re.compile(r'^\d{9,}$')  # At least 9 digits
ifsc_validator = re.compile(r'^[A-Z]{4}[A-Z0-9]{7}$')  # Removed fixed 5th char '0'

account_validator = re.compile(r'^\d{9,}$')  # At least 9 digits
ifsc_validator = re.compile(r'^[A-Z]{4}0[A-Z0-9]{6}$', re.IGNORECASE)  # Standard IFSC format

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.safestring import mark_safe
from .models import Education  # Adjust import as needed
from django import forms
from datetime import datetime
from .models import Education

from django import forms
from datetime import datetime
from .models import Education

class SSLCForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution_name', 'from_year', 'to_year']

        widgets = {
            'institution_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School Name',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Year choices (1970 - current year)
        year_choices = [(str(year), str(year)) for year in range(1970, datetime.now().year + 1)]
        year_choices.insert(0, ('', 'Select Year'))

        # Override fields as ChoiceField
        self.fields['from_year'] = forms.ChoiceField(
            choices=year_choices,
            widget=forms.Select(attrs={'class': 'form-control select-arrow-spacing', 'required': True}),
            label="From Year"
        )
        self.fields['to_year'] = forms.ChoiceField(
            choices=year_choices,
            widget=forms.Select(attrs={'class': 'form-control select-arrow-spacing', 'required': True}),
            label="To Year"
        )
        self.fields['institution_name'].label = "School Name"

    def clean(self):
        cleaned_data = super().clean()
        institution_name = cleaned_data.get('institution_name')
        from_year = cleaned_data.get('from_year')
        to_year = cleaned_data.get('to_year')

        # Required validations
        if not institution_name:
            self.add_error('institution_name', 'School name is required.')
        if not from_year:
            self.add_error('from_year', 'From Year is required.')
        if not to_year:
            self.add_error('to_year', 'To Year is required.')

        # Year order validation
        if from_year and to_year:
            try:
                if int(to_year) < int(from_year):
                    self.add_error('to_year', 'To Year cannot be before From Year.')
            except ValueError:
                self.add_error('to_year', 'Invalid year selection.')

        return cleaned_data

from datetime import datetime

# Generate year choices (from 1980 to current year + 5)
current_year = datetime.now().year
YEAR_CHOICES = [(str(y), str(y)) for y in range(1980, current_year + 6)]

from django import forms
from datetime import datetime
from .models import Education  # Make sure your Education model is correctly imported

# Year choices (1980 to current year + 5)
current_year = datetime.now().year
YEAR_CHOICES = [(str(y), str(y)) for y in range(1980, current_year + 6)]

from django import forms
from datetime import datetime
from .models import Education

# Year dropdown: 1980 to current year + 5
current_year = datetime.now().year
YEAR_CHOICES = [(str(y), str(y)) for y in range(1980, current_year + 6)]
from django import forms
from datetime import datetime
from .models import Education

# ✅ Generate year choices (1970 - current year)
YEAR_CHOICES = [(str(year), str(year)) for year in range(1970, datetime.now().year + 1)]
YEAR_CHOICES.insert(0, ('', 'Select Year'))


class EducationForm(forms.ModelForm):
    degree_type = forms.ChoiceField(
        choices=Education.DEGREE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select-arrow-spacing', 'required': True}),
        required=True,
        label="Degree Type"
    )

    institution_name = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Institution Full Name',
        }),
        label="Institution Name"
    )

    program = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Program',
        }),
        label="Program"
    )

    stream = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Stream',
        }),
        label="Stream"
    )

    from_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select-arrow-spacing', 'required': True}),
        required=True,
        label="From Year"
    )

    to_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control select-arrow-spacing', 'required': True}),
        required=True,
        label="To Year"
    )

    class Meta:
        model = Education
        fields = ['degree_type', 'institution_name', 'program', 'stream', 'from_year', 'to_year']

    def __init__(self, *args, **kwargs):
        exclude_degree_type = kwargs.pop('exclude_degree_type', None)
        super().__init__(*args, **kwargs)

        # ✅ Add "Select" option for dropdowns
        self.fields['degree_type'].choices = [('', 'Select Degree Type')] + list(Education.DEGREE_CHOICES)
        self.fields['from_year'].choices = YEAR_CHOICES
        self.fields['to_year'].choices = YEAR_CHOICES

        # ✅ Force required attribute in HTML for extra safety
        for field_name in ['degree_type', 'institution_name', 'program', 'stream', 'from_year', 'to_year']:
            self.fields[field_name].widget.attrs['required'] = 'required'

        # ✅ Exclude specific degree types if passed from view
        if exclude_degree_type:
            self.fields['degree_type'].choices = [
                (value, label) for value, label in self.fields['degree_type'].choices
                if value not in exclude_degree_type
            ]

    def clean(self):
        cleaned_data = super().clean()
        from_year = cleaned_data.get('from_year')
        to_year = cleaned_data.get('to_year')

        # Required validation (extra layer, in case browser bypasses "required")
        if not from_year:
            self.add_error('from_year', 'From Year is required.')
        if not to_year:
            self.add_error('to_year', 'To Year is required.')

        # Logical year validation
        if from_year and to_year:
            try:
                if int(from_year) > int(to_year):
                    self.add_error('to_year', 'To Year must be greater than or equal to From Year.')
            except ValueError:
                self.add_error('to_year', 'Invalid year format.')

        return cleaned_data

from django import forms
from django.core.exceptions import ValidationError
from .models import Experience

from django import forms
from django.forms import modelformset_factory
from .models import Experience


class DateInput(forms.DateInput):
    input_type = 'date'


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'company', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Job Title'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Company Name'
            }),
            'start_date': DateInput(attrs={
                'class': 'form-control text-uppercase'
            }),
            'end_date': DateInput(attrs={
                'class': 'form-control text-uppercase'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Field requirements
        self.fields['title'].required = True
        self.fields['company'].required = True
        self.fields['start_date'].required = True
        self.fields['end_date'].required = False


ExperienceFormSet = modelformset_factory(
    Experience,
    form=ExperienceForm,
    extra=0,
    can_delete=True
)


class SalaryAndStatutoryForm(forms.ModelForm):
    class Meta:
        model = SalaryAndStatutory
        fields = [
            'salary_basis', 'salary_amount', 'payment_type',
            'pf_contribution', 'pf_number', 'employee_pf_rate', 'additional_pf_rate', 'total_pf_rate',
            'esi_contribution', 'esi_number', 'employee_esi_rate', 'additional_esi_rate', 'total_esi_rate',
            'is_approved',
        ]
        widgets = {
            'salary_basis': Select(attrs={'class': 'form-control'}),
            'salary_amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_type': Select(attrs={'class': 'form-control'}),
            'pf_contribution': Select(attrs={'class': 'form-control'}),
            'pf_number': TextInput(attrs={'class': 'form-control'}),
            'employee_pf_rate': Select(attrs={'class': 'form-control'}),
            'additional_pf_rate': Select(attrs={'class': 'form-control'}),
            'total_pf_rate': TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'esi_contribution': Select(attrs={'class': 'form-control'}),
            'esi_number': TextInput(attrs={'class': 'form-control'}),
            'employee_esi_rate': Select(attrs={'class': 'form-control'}),
            'additional_esi_rate': Select(attrs={'class': 'form-control'}),
            'total_esi_rate': TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'is_approved': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        def extract_percent(value):
            try:
                return int(str(value).strip('%'))
            except:
                return 0

        pf1 = extract_percent(cleaned_data.get('employee_pf_rate'))
        pf2 = extract_percent(cleaned_data.get('additional_pf_rate'))
        cleaned_data['total_pf_rate'] = f"{pf1 + pf2}%"

        esi1 = extract_percent(cleaned_data.get('employee_esi_rate'))
        esi2 = extract_percent(cleaned_data.get('additional_esi_rate'))
        cleaned_data['total_esi_rate'] = f"{esi1 + esi2}%"

        return cleaned_data
    
from django import forms
from django.core.validators import RegexValidator
from .models import BankDetails, FamilyMember

class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = BankDetails
        fields = ['bank_name', 'account_no', 'ifsc_code']
        widgets = {
            'bank_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Bank Name',
                'required': True
            }),
'account_no': forms.TextInput(attrs={
    'class': 'form-control',
    'placeholder': 'Enter Account Number',
    'required': True,
    'pattern': r'^\d+$',
    'inputmode': 'numeric',
    'title': 'Only numbers are allowed'
}),

            'ifsc_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter IFSC Code',
                'required': True,
                'style': 'text-transform: none;'  # 👈 prevents uppercase
            }),
        }

    def clean_account_no(self):
        account_no = self.cleaned_data.get('account_no')
        if not account_no:
            raise forms.ValidationError("Account number is required.")
        if not account_no.isdigit():
            raise forms.ValidationError("Account number must contain only digits.")
        if len(account_no) < 9 or len(account_no) > 18:
            raise forms.ValidationError("Account number must be between 9 to 18 digits.")
        return account_no


# --- FAMILY MEMBER FORM ---
from django import forms
from .models import FamilyMember

YES_NO_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'date_of_birth', 'occupation', 'address', 'dependent']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Full Name',
                'required': 'required'
            }),
            'relationship': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),  # assuming RELATIONSHIP_CHOICES in model
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control text-uppercase',
                'placeholder': 'YYYY-MM-DD',
                'type': 'date',
                'required': 'required'
            }),
            'occupation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Occupation',
                'required': 'required'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter Address',
                'required': 'required'
            }),
            'dependent': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super(FamilyMemberForm, self).__init__(*args, **kwargs)
        self.fields['date_of_birth'].label = 'DOB'
        choices = self.fields['relationship'].choices
        choices = [choice for choice in choices if choice[0] != '']

    # Add your custom placeholder at the top
        self.fields['relationship'].choices = [('', 'Select Relationship')] + choices
         # 🔹 Add custom empty label for dependent
        dep_choices = self.fields['dependent'].choices
        dep_choices = [choice for choice in dep_choices if choice[0] != '']
        self.fields['dependent'].choices = [('', 'Select Dependent')] + dep_choices

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_relationship(self):
        rel = self.cleaned_data.get('relationship')
        if not rel:
            raise forms.ValidationError("Relationship is required.")
        return rel

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            raise forms.ValidationError("Date of Birth is required.")
        return dob

    def clean_dependent(self):
        dep = self.cleaned_data.get('dependent')
        if dep not in ['yes', 'no']:
            raise forms.ValidationError("Please select if the member is dependent.")
        return dep


FamilyMemberFormSet = modelformset_factory(
    FamilyMember,
    form=FamilyMemberForm,
    extra=1,           # Number of blank forms to show by default
    can_delete=True    # Allow deletion of existing entries
)


from django import forms
from .models import EducationDocument, GovernmentDocument

# --- Education Document Form ---
from django import forms
from .models import EducationDocument

from django import forms
from django.core.exceptions import ValidationError
import os
from .models import EducationDocument, GovernmentDocument

# --- Education Document Form ---
class EducationDocumentForm(forms.ModelForm):
    class Meta:
        model = EducationDocument
        fields = ['document_type', 'other_document_type', 'document_file']

    def __init__(self, *args, **kwargs):
        exclude_degree_type = kwargs.pop('exclude_degree_type', False)
        super().__init__(*args, **kwargs)

        # Remove any blank/dash choices and add your own placeholder
        choices = self.fields['document_type'].choices
        choices = [choice for choice in choices if choice[0] != '']
        self.fields['document_type'].choices = [('', 'Select Document Type')] + choices

        # Always optional unless specifically required below
        self.fields['other_document_type'].required = False

        # Exclude "Degree" from choices if specified
        if exclude_degree_type:
            self.fields['document_type'].queryset = self.fields['document_type'].queryset.exclude(name='Degree')

        # Get selected value safely from form data or initial
        selected_type = self.data.get('document_type') or self.initial.get('document_type')

        # Adjust field requirements based on selection
        if selected_type == '10th Certificate':
            self.fields['document_file'].required = True

        if selected_type == 'Other':
            self.fields['other_document_type'].required = True

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')
        doc_type = self.cleaned_data.get('document_type')

        # Apply restriction only for specific types
        if file and doc_type in ['10th Certificate', 'Degree', 'Other']:
            valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
            valid_content_types = ['application/pdf', 'image/png', 'image/jpeg']

            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Only PDF, PNG, JPG files are allowed for Education Documents.")

            if file.content_type not in valid_content_types:
                raise ValidationError("Invalid file format. Allowed: PDF, PNG, JPG.")

        return file

    def clean(self):
        cleaned_data = super().clean()
        doc_type = cleaned_data.get('document_type')
        other_doc_type = cleaned_data.get('other_document_type')

        # Ensure other_doc_type is entered if "Other" selected
        if doc_type == 'Other' and not other_doc_type:
            self.add_error('other_document_type', "Please specify the document type.")

        return cleaned_data


from django import forms
from django.core.exceptions import ValidationError
from .models import GovernmentDocument

class GovernmentDocumentForm(forms.ModelForm):
    class Meta:
        model = GovernmentDocument
        fields = ['document_type', 'other_document_type', 'document_file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hide 'other_document_type' unless 'Other' is selected
        self.fields['other_document_type'].required = False

        # Clean up choices & add placeholder
        choices = self.fields['document_type'].choices
        choices = [choice for choice in choices if choice[0] != '']
        self.fields['document_type'].choices = [('', 'Select Document Type')] + choices

        # Enforce Aadhaar and PAN card as required
        document_type = self.initial.get('document_type') or self.data.get('document_type')
        if document_type in ['Aadhaar Card', 'PAN Card']:
            self.fields['document_file'].required = True

    def clean_document_file(self):
        file = self.cleaned_data.get('document_file')
        doc_type = self.cleaned_data.get('document_type')

        if file and doc_type in ['Aadhaar Card', 'PAN Card']:
            valid_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
            valid_content_types = ['application/pdf', 'image/png', 'image/jpeg']

            # Extension check
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in valid_extensions:
                raise ValidationError("Only PDF, PNG, JPG files are allowed for Aadhaar and PAN Card.")

            # MIME type check
            if file.content_type not in valid_content_types:
                raise ValidationError("Invalid file format. Allowed: PDF, PNG, JPG.")
            return file