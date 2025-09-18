from django import forms
from .models import PerformanceIndicator, PerformanceAppraisal
from designation.models import Designation
from department.models import Department
from employee.models import Employee

class PerformanceIndicatorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company).order_by('first_name')
            
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        empty_label="Select Employee",
        widget=forms.Select(attrs={'class': 'form-control custom-select'})
    )
    
    class Meta:
        model = PerformanceIndicator
        exclude = ['company', 'added_by', 'created_at']
        widgets = {
            field: forms.Select(attrs={'class': 'form-control custom-select'})
            for field in [
                'customer_experience', 'marketing', 'management', 'administration', 'presentation_skill',
                'quality_of_work', 'efficiency', 'integrity', 'professionalism', 'teamwork',
                'critical_thinking', 'conflict_management', 'attendance', 'punctuality',
                'dependability', 'communication', 'decision_making', 'status',
            ]
        }


class PerformanceAppraisalForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company).order_by('first_name')

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.none(),
        empty_label="— Select Employee —",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PerformanceAppraisal
        exclude = ['company', 'appraiser', 'created_at']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-upercase'}),
            **{
                field: forms.Select(attrs={'class': 'form-control'}) for field in [
                    'customer_experience', 'marketing', 'management', 'administration', 'presentation_skill',
                    'quality_of_work', 'efficiency', 'integrity', 'professionalism', 'team_work',
                    'critical_thinking', 'conflict_management', 'attendance',
                    'ability_to_meet_deadline', 'status'
                ]
            }
        }












