from django import forms
from django.utils.safestring import mark_safe
from .models import LeaveType,LeaveBalance,LeaveRequest

class LeaveTypeForm(forms.ModelForm):
    class Meta:
        model = LeaveType
        fields = ['name', 'eligibility', 'monthly_accrual', 'carry_forward', 'encashment', 'default_days']
        labels = {
            'name': 'Leave Type Name',
            'carry_forward': 'Carry Forward',
            'default_days': 'Default Days',
            'monthly_accrual': 'Monthly Accrual',
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave Type Name',
                'required': True,
            }),
            'default_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of default leave days',
                'required': True,
            }),
            'monthly_accrual': forms.NumberInput(attrs={
    'class': 'form-control',
    'placeholder': 'Monthly Accrual',
    'required': True,
    'min': 0  # optional
}),

            'eligibility': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': True,
            }),
            'carry_forward': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': True,
            }),
            'encashment': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.label_suffix = ''  # remove default colon
        for field_name, field in self.fields.items():
            field.required = True
            if field.label:
                # Append red asterisk
                label_text = field.label.rstrip(':')
                field.label = mark_safe(f'{label_text} <span style="color:red">*</span>')

        self.fields['eligibility'].empty_label = "Select Eligibility"
        self.fields['carry_forward'].empty_label = "Select Carry Forward"
        self.fields['encashment'].empty_label = "Select Encashment"


from datetime import date, timedelta
from django import forms
from datetime import date, timedelta
from .models import LeaveRequest

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'reason']
        widgets = {
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-uppercase'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control text-uppercase'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set empty label for leave_type dropdown
        self.fields['leave_type'].empty_label = "Select Leave Type"

        # Make all fields required and append red *
        for field_name, field in self.fields.items():
            field.required = True
            if field.required:
                field.label = f"{field.label} <span style='color: red;'>*</span>"
                field.label_suffix = ''  # Prevent Django from adding ":" after label

        # Set min date to tomorrow dynamically
        min_date = (date.today() + timedelta(days=1)).isoformat()
        self.fields['start_date'].widget.attrs['min'] = min_date
        self.fields['end_date'].widget.attrs['min'] = min_date


    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        tomorrow = date.today() + timedelta(days=1)

        if start_date and start_date < tomorrow:
            self.add_error('start_date', 'Start date must be a future date (from tomorrow).')

        if end_date and end_date < tomorrow:
            self.add_error('end_date', 'End date must be a future date (from tomorrow).')

        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date cannot be earlier than start date.')

        return cleaned_data

