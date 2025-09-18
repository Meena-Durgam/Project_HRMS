from django import forms
from .models import PayItem, Payroll
from employee.models import Employee
import datetime
from django.utils.safestring import mark_safe


from django.utils.safestring import mark_safe

class PayItemForm(forms.ModelForm):
    class Meta:
        model = PayItem
        fields = ['title', 'item_type', 'amount', 'assign_to', 'specific_employees']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'item_type': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'assign_to': forms.Select(attrs={'class': 'form-control'}),
            'specific_employees': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super(PayItemForm, self).__init__(*args, **kwargs)

        self.fields['specific_employees'].queryset = Employee.objects.none()
        if company:
            self.fields['specific_employees'].queryset = Employee.objects.filter(company=company)

        self.fields['specific_employees'].required = False  # Optional field

        # Capitalized (Title Case) labels + Red Asterisk for required
        for field_name, field in self.fields.items():
            base_label = field.label or field_name.replace('_', ' ')
            base_label = base_label.title()  # Properly capitalized: "Specific Employees"
            if field.required:
                field.label = mark_safe(f"{base_label} <span style='color: red;'>*</span>")
            else:
                field.label = base_label


from django import forms
from .models import Payroll
from employee.models import Employee
import datetime
from django.utils.safestring import mark_safe


class PayrollForm(forms.ModelForm):
    class Meta:
        model = Payroll
        fields = ['employee', 'payroll_date', 'status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)
        super(PayrollForm, self).__init__(*args, **kwargs)

        # Filter employees by company
        self.fields['employee'].queryset = Employee.objects.none()
        if company:
            self.fields['employee'].queryset = Employee.objects.filter(company=company)

        # Set form-control class
        self.fields['employee'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-control'})

        # Set payroll_date widget
        today = datetime.date.today().isoformat()
        self.fields['payroll_date'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'min': today,
            }
        )

        # Capitalized labels with red asterisk
        for field_name, field in self.fields.items():
            # Convert field name to title case label (e.g., payroll_date -> Payroll Date)
            label = field.label or field_name.replace('_', ' ')
            label = label.title()
            if field.required:
                field.label = mark_safe(f"{label} <span style='color: red;'>*</span>")
            else:
                field.label = label
