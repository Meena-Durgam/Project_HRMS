from django import forms
from datetime import date
from .models import Termination
from employee.models import Employee
from django.forms import DateInput


class TerminationForm(forms.ModelForm):
    class Meta:
        model = Termination
        fields = ['employee', 'termination_type', 'notice_date', 'termination_date', 'reason']
        widgets = {
            'notice_date': DateInput(attrs={'class': 'form-control text-uppercase', 'type': 'date'}),
            'termination_date': DateInput(attrs={'class': 'form-control text-uppercase', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Make all fields required
        for field in self.fields.values():
            field.required = True

        if user:
            self.fields['employee'].queryset = Employee.objects.filter(company=user.company)

        # Add empty label to employee field (adds blank option with label)
        self.fields['employee'].empty_label = 'Select Employee'

        # Add empty choice to termination_type field (CharField with choices)
        self.fields['termination_type'].choices = [('', 'Select Termination Type')] + list(self.fields['termination_type'].choices)

        # Add form-control CSS class
        self.fields['termination_type'].widget.attrs.update({'class': 'form-control'})

        # Set min date attributes
        self.fields['notice_date'].widget.attrs['min'] = date.today().isoformat()
        self.fields['termination_date'].widget.attrs['min'] = date.today().isoformat()

        # Add form-control class to all other fields except file inputs
        for field in self.fields.values():
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault('class', 'form-control')

