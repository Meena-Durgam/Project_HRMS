import re
from django import forms
from .models import JobSeekerProfile, Experience, Internship, Education
from .models import SavedJob
from .models import Certificate
from django_select2.forms import ModelSelect2MultipleWidget


from django import forms
from .models import JobSeekerProfile
import os
from django import forms
from .models import JobSeekerProfile

class JobSeekerProfileForm(forms.ModelForm):
    LOCATION_CHOICES = [
        ("Bengaluru", "Bengaluru"),
        ("Pune", "Pune"),
        ("Hyderabad", "Hyderabad"),
        ("Chennai", "Chennai"),
        ("Mumbai", "Mumbai"),
        ("Ahmedabad", "Ahmedabad"),
        ("Kolkata", "Kolkata"),
        ("Surat", "Surat"),
        ("Navi Mumbai", "Navi Mumbai"),
        ("Chandigarh", "Chandigarh"),
        ("Kochi", "Kochi"),
        ("Coimbatore", "Coimbatore"),
        ("Indore", "Indore"),
        ("Gurugram", "Gurugram"),
        ("Delhi", "Delhi"),
        ("Jaipur", "Jaipur"),
        ("Visakhapatnam", "Visakhapatnam"),
        ("Ranchi", "Ranchi"),
        ("Vijayawada", "Vijayawada"),
        ("Nagpur", "Nagpur"),
        ("Vadodara", "Vadodara"),
        ("Lucknow", "Lucknow"),
        ("Mysuru", "Mysuru"),
        ("Thiruvananthapuram", "Thiruvananthapuram"),
        ("Bhubaneswar", "Bhubaneswar"),
        ("Madurai", "Madurai"),
        ("Nashik", "Nashik"),
        ("Raipur", "Raipur"),
        ("Rajkot", "Rajkot"),
        ("Agra", "Agra"),
    ]

    preferred_location = forms.MultipleChoiceField(
        choices=LOCATION_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = JobSeekerProfile
        exclude = ['user', 'skills', 'other_skill', 'work_experience', 'certificate']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'oninput': "this.value=this.value.replace(/[^0-9]/g,'')",
                'pattern': '[0-9]{10,15}',
                'title': 'Enter only numbers (10-15 digits)'
            }),
            'hometown': forms.TextInput(attrs={'class': 'form-control'}),
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': True}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'current_location': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_domain': forms.TextInput(attrs={'class': 'form-control'}),
            'salary_expectation': forms.NumberInput(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'  # Frontend restriction
            }),
            'profile_picture': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.jpg,.jpeg,.png'  # Frontend restriction
            }),
        }

    def clean_contact_number(self):
        contact = self.cleaned_data.get('contact_number')
        if contact:
            if not contact.isdigit():
                raise forms.ValidationError("Contact number must contain digits only.")
            if len(contact) < 10 or len(contact) > 15:
                raise forms.ValidationError("Contact number must be between 10 and 15 digits.")
        return contact

    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if not dob:
            raise forms.ValidationError("Date of Birth is required.")
        return dob

    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            ext = os.path.splitext(resume.name)[1].lower()
            if ext != '.pdf':
                raise forms.ValidationError("Only PDF files are allowed for resumes.")
        return resume

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            ext = os.path.splitext(picture.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png']:
                raise forms.ValidationError("Only JPG, JPEG, or PNG images are allowed for profile pictures.")
        return picture

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Convert list of locations into a comma-separated string
        locations = self.cleaned_data.get('preferred_location', [])
        instance.preferred_location = ",".join(locations)
        if commit:
            instance.save()
        return instance
    

# SKILLS FORM (only skills)
class SkillsForm(forms.ModelForm):
    other_skill = forms.CharField(
        required=False,
        label="Other Skill (if not listed)",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter other skill"})
    )

    class Meta:
        model = JobSeekerProfile
        fields = ['skills', 'other_skill']
        widgets = {
            'skills': forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned_data = super().clean()
        selected_skills = cleaned_data.get('skills') or []
        other_skill = cleaned_data.get('other_skill', '').strip()

        if 'Others' in selected_skills and not other_skill:
            self.add_error('other_skill', "Please specify the 'Other' skill.")

        if other_skill:
            if isinstance(selected_skills, list):
                selected_skills.append(other_skill)
            elif isinstance(selected_skills, str):
                selected_skills = [selected_skills, other_skill]
            else:
                selected_skills = list(selected_skills) + [other_skill]

            cleaned_data['skills'] = selected_skills

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        skills = self.cleaned_data.get('skills')
        if isinstance(skills, list):
            instance.skills = ",".join(skills)
        if commit:
            instance.save()
        return instance


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ['profile']
        widgets = {
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['company'].required = True
        self.fields['job_title'].required = True

    def clean_company(self):
        company = self.cleaned_data.get('company', '').strip()
        if not company:
            raise forms.ValidationError("Company Name is required.")
        return company

    def clean_job_title(self):
        job_title = self.cleaned_data.get('job_title', '').strip()
        if not job_title:
            raise forms.ValidationError("Job Position is required.")
        return job_title
from django.forms import modelformset_factory, DateInput

class InternshipForm(forms.ModelForm):
    class Meta:
        model = Internship
        exclude = ['profile']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def _init_(self, *args, **kwargs):
        super()._init_(*args, **kwargs)
        self.fields['company'].required = True
        self.fields['title'].required = True

    def clean_company(self):
        company = self.cleaned_data.get('company', '').strip()
        if not company:
            raise forms.ValidationError("Company Name is required.")
        return company

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Internship Title is required.")
        return title


# Internship formset (multiple forms)
InternshipFormSet = modelformset_factory(
    Internship,
    form=InternshipForm,
    extra=2,             # Show 2 blank forms by default
    can_delete=True      # Allow deleting entries
)

# Education Form
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['degree', 'institution', 'start_year', 'end_year']
        widgets = {
            'degree': forms.Select(attrs={'class': 'form-select'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'start_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'end_year': forms.NumberInput(attrs={'class': 'form-control'}),
        
        }

        
from django.forms import modelformset_factory
from .models import Education

EducationFormSet = modelformset_factory(
    Education,
    form=EducationForm,
    extra=2,          # Number of empty forms to show
    can_delete=True   # Allow deletion of education entries
)

# ✅ Certificate Form (missing one that caused ImportError)
from django import forms
from django.forms import modelformset_factory
from .models import Certificate


class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'application/pdf'
            }),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.lower().endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if file.content_type != 'application/pdf':
                raise forms.ValidationError("Invalid file type. Only PDF is allowed.")
        return file


CertificateFormSet = modelformset_factory(
    Certificate,
    form=CertificateForm,
    extra=2,
    can_delete=True
)

class SaveJobForm(forms.ModelForm):
    class Meta:
        model = SavedJob
        fields = ['job']  # Only the job is selected, user is auto-added in view
        widgets = {
            'job': forms.HiddenInput()
}
        

from django import forms
from .models import JobSeekerApplication

class JobSeekerApplicationForm(forms.ModelForm):
    class Meta:
        model = JobSeekerApplication
        fields = ['job','resume']
        widgets = {
            'job': forms.Select(attrs={'class': 'form-control'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def init(self, *args, **kwargs):
        # Initialize with any initial data passed in the kwargs
        jobseeker_profile = kwargs.get('jobseeker_profile', None)
        
        # If the jobseeker_profile is passed, add relevant initial values
        if jobseeker_profile:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}

            kwargs['initial']['cover_letter'] = f"Dear Hiring Manager, I am applying for the position of {kwargs.get('instance').job.title}."
            kwargs['initial']['resume'] = jobseeker_profile.resume  # Set the resume from their profile

        super().init(*args, **kwargs)


class InterviewScheduleForm(forms.Form):
    interview_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    interview_time = forms.TimeField(widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}))
    interview_mode = forms.ChoiceField(choices=[('Online', 'Online'), ('Offline', 'Offline')], widget=forms.Select(attrs={'class': 'form-control'}))