from django import forms
from django.utils import timezone
from .models import Job, Department, JobApplicant

# forms.py

from ckeditor.widgets import CKEditorWidget

class JobForm(forms.ModelForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'max-height: 150px; overflow-y: auto;'
        }),
        empty_label="Select Department"
    )

    description = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Job
        fields = [
            'title', 'department', 'location', 'vacancies', 'experience',
            'salary_from', 'salary_to', 'job_type', 'status',
            'start_date', 'expired_date', 'description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control'}),
            'experience': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_from': forms.NumberInput(attrs={'class': 'form-control'}),
            'salary_to': forms.NumberInput(attrs={'class': 'form-control'}),
            'job_type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expired_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)
        if company:
            self.fields['department'].queryset = Department.objects.filter(company=company)



class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplicant
        fields = ['name', 'email', 'phone', 'resume']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your full name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone number'}),
            'resume': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.company:
            instance.company = self.company
        if commit:
            instance.save()
        return instance
