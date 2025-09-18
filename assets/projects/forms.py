from django import forms
from .models import Task, Project,TaskProgress
from employee.models import Employee

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 'project', 'assigned_to', 'status', 'priority',
            'start_date', 'due_date', 'description', 'attachment'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Task Title'
            }),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control '}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Accept user to filter data
        super().__init__(*args, **kwargs)

        # Make all fields required explicitly
        for field_name, field in self.fields.items():
            field.required = True

            # Add 'form-control' class to widget (preserve existing classes)
            existing_classes = field.widget.attrs.get('class', '')
            classes = existing_classes.split()
            if 'form-control' not in classes:
                classes.append('form-control')
            field.widget.attrs['class'] = ' '.join(classes)

        # Limit project queryset to projects led by this user
        if user and hasattr(user, 'employee_account'):
            employee = user.employee_account
            self.fields['project'].queryset = Project.objects.filter(team_leader=employee)
        else:
            self.fields['project'].queryset = Project.objects.none()

        # Determine selected project to filter assigned_to
        project = None
        if self.instance and self.instance.pk:
            project = self.instance.project
        elif 'project' in self.data:
            try:
                project_id = int(self.data.get('project'))
                project = Project.objects.get(id=project_id)
            except (ValueError, Project.DoesNotExist):
                project = None

        if project:
            self.fields['assigned_to'].queryset = project.team_members.all()
        else:
            self.fields['assigned_to'].queryset = Employee.objects.none()

    def save(self, commit=True):
        task = super().save(commit=False)
        task.clean()  # Enforce any custom model validation
        if commit:
            task.save()
            self.save_m2m()
        return task



from django import forms
from .models import TaskProgress

class TaskProgressForm(forms.ModelForm):
    class Meta:
        model = TaskProgress
        fields = ['progress_description', 'percentage_complete', 'attachment']
        widgets = {
            'progress_description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Describe your progress...'
            }),
            'percentage_complete': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 50'
            }),
            'attachment': forms.ClearableFileInput(attrs={
                'class': 'form-control-file'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields required & add asterisk in label
        for field_name, field in self.fields.items():
            field.required = True
            if field.label:  
                field.label = f'{field.label} <span style="color:red">*</span>'
                field.label = forms.utils.mark_safe(field.label)



from datetime import date

from django import forms
from .models import Project, Client, Employee
from datetime import date
from django.utils.safestring import mark_safe

from django import forms
from .models import Project
from datetime import date
from django.utils.safestring import mark_safe
from django.forms.widgets import DateInput
from django import forms
from .models import Project
from ckeditor.widgets import CKEditorWidget

from django import forms
from django.utils.safestring import mark_safe
from .models import Project
from .models import Department


from django.utils.safestring import mark_safe
from django import forms
from django.utils.safestring import mark_safe
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['company']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'height: 40px;',
                'placeholder': 'Enter Project Name'
            }),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date'
            }),
            'end_date': forms.TextInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date'
            }),
            'team_members': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'team_leader': forms.Select(attrs={'class': 'form-control'}),
            'file_upload': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf, image/*'  # ✅ Allow only PDF + images
            }),
            'description': forms.Textarea(attrs={
                'id': 'ckeditor5-description',
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # ✅ Make all fields required
        for name, field in self.fields.items():
            field.required = True

        # ❌ Except file_upload (optional)
        self.fields['file_upload'].required = False

        # ✅ Empty labels
        if 'client' in self.fields:
            self.fields['client'].empty_label = "Select Client"
        if 'team_leader' in self.fields:
            self.fields['team_leader'].empty_label = "Select Team Leader"
        if 'department' in self.fields:
            self.fields['department'].empty_label = "Select Department"

        # ✅ Priority choices fix
        if 'priority' in self.fields:
            choices = self.fields['priority'].choices
            self.fields['priority'].choices = [('', 'Select Priority')] + [
                choice for choice in choices if choice[0] != ''
            ]

        # ✅ Company-specific querysets
        if company:
            from clients.models import Client
            from employee.models import Employee
            from department.models import Department

            self.fields['client'].queryset = Client.objects.filter(company=company, status='Active')
            self.fields['team_leader'].queryset = Employee.objects.filter(company=company, status='Active')
            self.fields['team_members'].queryset = Employee.objects.filter(company=company, status='Active')
            self.fields['department'].queryset = Department.objects.filter(company=company, status='Active')

        # ✅ Add red * only for required fields
        for name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f"{field.label} <span style='color: red;'>*</span>")

    def clean_file_upload(self):
        file = self.cleaned_data.get("file_upload")

        if file:
            allowed_types = ["application/pdf", "image/jpeg", "image/png"]
            if file.content_type not in allowed_types:
                raise forms.ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")
            if file.size > 5 * 1024 * 1024:  # ✅ 5MB limit
                raise forms.ValidationError("File size must be less than 5 MB.")
        return file

