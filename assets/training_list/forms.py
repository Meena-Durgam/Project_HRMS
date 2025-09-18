from django import forms
from .models import Training, TrainingType
from trainers.models import Trainer
from employee.models import Employee

from django import forms
from datetime import date
from .models import Training, TrainingType
from trainers.models import Trainer
from employee.models import Employee
from django.utils.safestring import mark_safe


class TrainingForm(forms.ModelForm):
    class Meta:
        model = Training
        exclude = ['company']  # ✅ company set in view
        widgets = {
            'training_type': forms.Select(attrs={'class': 'form-control'}),
            'trainer': forms.Select(attrs={'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'training_cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        # Custom employee label
        self.fields['employee'].label_from_instance = lambda obj: f"{obj.employee_id} - {obj.first_name} {obj.last_name}"

        # Restrict dropdowns by company
        if company:
            self.fields['training_type'].queryset = TrainingType.objects.filter(company=company, status='Active')
            self.fields['trainer'].queryset = Trainer.objects.filter(company=company, status='Active')
            self.fields['employee'].queryset = Employee.objects.filter(company=company, status='Active')

        # Restrict past date selection in widgets
        today_str = date.today().isoformat()
        self.fields['start_date'].widget.attrs['min'] = today_str
        self.fields['end_date'].widget.attrs['min'] = today_str

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if start_date and start_date < date.today():
            raise forms.ValidationError("Start date cannot be in the past.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        if end_date and end_date < date.today():
            raise forms.ValidationError("End date cannot be in the past.")
        return end_date


class TrainingTypeForm(forms.ModelForm):
    class Meta:
        model = TrainingType
        exclude = ['company']  # company is set in the view
        widgets = {
            'type_name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(TrainingTypeForm, self).__init__(*args, **kwargs)
        
        self.label_suffix = ''  # ✅ Removes the default colon (:) from labels

        for field_name, field in self.fields.items():
            label = field.label or field_name.replace('_', ' ')
            label = label.title()  # Capitalize to title case

            # ✅ Add red asterisk (*) for required fields
            if field.required:
                field.label = mark_safe(f"{label} <span style='color:red;'>*</span>")
            else:
                field.label = label