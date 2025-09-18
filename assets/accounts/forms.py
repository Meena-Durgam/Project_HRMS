from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Company
from django.contrib.auth.password_validation import password_validators_help_texts


class CompanyOwnerSignupForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Remove default colon from labels
        self.label_suffix = ''

        # Loop all fields to enforce required and add red *
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs.update({'required': 'required'})

            # Add red asterisk
            if field.label:
                field.label = f"{field.label} <span style='color:red;'>*</span>"

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'company_owner'
        if commit:
            user.save()
        return user

    def get_password_help_texts(self):
        return password_validators_help_texts()

from django import forms
from .models import Company

class CompanySettingsForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = [
            'name', 'email', 'phone', 'website', 'address',
            'size', 'industry', 'logo', 'is_active'
        ]
        labels = {
            'name': 'Company Name',
            'email': 'Company Email',
            'phone': 'Contact Number',
            'website': 'Official Website',
            'address': 'Office Address',
            'size': 'Company Size (No. of Employees)',
            'industry': 'Industry Type',
            'logo': 'Company Logo',
            'is_active': 'Is Company Active?',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter Company Name'}),
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
            'phone': forms.TextInput(attrs={'placeholder': '10-Digit Phone Number'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://company.com'}),
            'address': forms.TextInput(attrs={'placeholder': 'Enter Full Address'}),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        # Mark selected fields as required
        required_fields = ['name', 'phone', 'address', 'website', 'logo']
        for field_name in required_fields:
            self.fields[field_name].required = True

        # Set email as initial from logged-in user
        if self.request and self.request.user.is_authenticated:
            self.fields['email'].initial = self.request.user.email

        # Set empty/default option for size and industry
        if self.fields['size'].choices:
            self.fields['size'].choices = [('', 'Select Size')] + list(self.fields['size'].choices)[1:]
        if self.fields['industry'].choices:
            self.fields['industry'].choices = [('', 'Select Industry')] + list(self.fields['industry'].choices)[1:]

        # Make website optional
        self.fields['website'].required = False


from django.utils.safestring import mark_safe
class JobSeekerSignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=mark_safe('First Name <span style="color:red;">*</span>')
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=mark_safe('Last Name <span style="color:red;">*</span>')
    )
    email = forms.EmailField(
        required=True,
        label=mark_safe('Email-ID <span style="color:red;">*</span>')
    )
    password1 = forms.CharField(
        label=mark_safe('Password <span style="color:red;">*</span>'),
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label=mark_safe('Password Confirmation <span style="color:red;">*</span>'),
        strip=False,
        widget=forms.PasswordInput,
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
