from django import forms
from .models import Designation
from department.models import Department

class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['department', 'name', 'status']
        labels = {
            'department': 'Department',
            'name': 'Designation Name',
            'status': 'Status',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter designation name'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Filter department queryset by user's company
        if user and hasattr(user, 'company') and user.company:
            self.fields['department'].queryset = Department.objects.filter(company=user.company)

        # Add empty label for department
        self.fields['department'].empty_label = 'Select Department'

        # Override status choices with "Select Status"
        self.fields['status'].choices = [('', 'Select Status')] + list(self.fields['status'].choices)[1:]

        # Required fields
        self.fields['department'].required = True
        self.fields['name'].required = True
        self.fields['status'].required = True

        # Custom error messages
        self.fields['name'].error_messages = {'required': 'Please enter a designation name.'}
        self.fields['department'].error_messages = {'required': 'Please select a department.'}
        self.fields['status'].error_messages = {'required': 'Please select status.'}
