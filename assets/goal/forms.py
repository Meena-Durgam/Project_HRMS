from django import forms
from .models import GoalType, Goal

class GoalTypeForm(forms.ModelForm):
    class Meta:
        model = GoalType
        fields = ['name', 'description', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter goal type name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


from datetime import date
from django import forms
from .models import Goal, GoalType

class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            'goal_type',
            'subject',
            'target_achievement',
            'start_date',
            'end_date',
            'description',
            'status',
            'progress',
        ]
        widgets = {
            'goal_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter goal subject'}),
            'target_achievement': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat()
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'min': date.today().isoformat()
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'progress': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super().__init__(*args, **kwargs)

        if company:
            self.fields['goal_type'].queryset = GoalType.objects.filter(company=company, status='Active')

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
