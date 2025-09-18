from django import forms
from datetime import date
from .models import Promotion
from employee.models import Employee
from department.models import Department
from designation.models import Designation
from django.forms import DateInput

class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['employee', 'new_department', 'new_designation', 'promotion_date', 'remarks']
        widgets = {
            'promotion_date': DateInput(attrs={'class': 'form-control text-uppercase', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter remarks'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # set querysets scoped to company
        if user and hasattr(user, 'company'):
            company = user.company
            self.fields['employee'].queryset = Employee.objects.filter(company=company)
            self.fields['new_department'].queryset = Department.objects.filter(company=company, status='Active')
            self.fields['new_designation'].queryset = Designation.objects.filter(company=company, status='Active')

        # Make all fields required and add bootstrap classes
        for name, field in self.fields.items():
            field.required = True
            if not isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault('class', 'form-control')
            # mark HTML required attribute too (client-side)
            field.widget.attrs['required'] = 'required'

        # replace blank option label for the ModelChoiceFields to show friendly text
        placeholders = {
            'employee': 'Select Employee',
            'new_department': 'Select New Department',
            'new_designation': 'Select New Designation',
        }
        for fname, label in placeholders.items():
            f = self.fields.get(fname)
            if f:
                # Build choices robustly: if first choice is blank replace label, else insert
                choices = list(f.choices)
                if choices:
                    if str(choices[0][0]) in ('', 'None'):
                        choices[0] = ('', label)
                    else:
                        choices.insert(0, ('', label))
                else:
                    choices = [('', label)]
                f.choices = choices

        # Min date
        self.fields['promotion_date'].widget.attrs['min'] = date.today().isoformat()

    # server-side validators to ensure user actually picked a value (not blank)
    def clean_employee(self):
        val = self.cleaned_data.get('employee')
        if not val:
            raise forms.ValidationError("Please select an employee.")
        return val

    def clean_new_department(self):
        val = self.cleaned_data.get('new_department')
        if not val:
            raise forms.ValidationError("Please select a new department.")
        return val

    def clean_new_designation(self):
        val = self.cleaned_data.get('new_designation')
        if not val:
            raise forms.ValidationError("Please select a new designation.")
        return val

    def clean_promotion_date(self):
        promotion_date = self.cleaned_data.get('promotion_date')
        if promotion_date and promotion_date < date.today():
            raise forms.ValidationError("Promotion date cannot be in the past.")
        return promotion_date