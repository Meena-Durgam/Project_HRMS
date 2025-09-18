from django import forms
from .models import Timesheet
from employee.models import Employee
from projects.models import Project

class TimesheetForm(forms.ModelForm):
    class Meta:
        model = Timesheet
        fields = ['project', 'task_description', 'task_file']
        widgets = {
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        employee = kwargs.pop('employee', None)
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'width: 100%; height: 40px;'
            })

        self.fields['task_description'].widget.attrs.update({
            'rows': 3,
            'placeholder': 'Enter task details here...'
        })

        self.fields['task_file'].widget.attrs.update({'class': 'form-control'})

        if employee and employee.company:
            self.fields['project'].queryset = Project.objects.filter(team_members=employee, company=employee.company)
        else:
            self.fields['project'].queryset = Project.objects.none()

        self.fields['project'].empty_label = "Select a project"

    def clean(self):
        cleaned_data = super().clean()
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')

        if clock_in and clock_out and clock_in >= clock_out:
            raise forms.ValidationError("Clock-out time must be later than clock-in time.")

        return cleaned_data


class TimesheetFilterForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.none(),
        required=False,
        empty_label="Select a Project"
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        required=False,
        empty_label="All Employees"
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    status = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        required=False
    )

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'style': 'width: 100%; height: 40px; margin-bottom: 10px;'
            })

        if company:
            self.fields['project'].queryset = Project.objects.filter(company=company)
            self.fields['employee'].queryset = Employee.objects.filter(company=company)

        self.fields['project'].label = "Project"
        self.fields['employee'].label = "Employee"
        self.fields['date'].label = "Date"
        self.fields['status'].label = "Timesheet Status"
