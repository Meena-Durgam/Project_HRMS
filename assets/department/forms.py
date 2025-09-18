# department/forms.py
from django import forms
from .models import Department

from django import forms
from .models import Department

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'status': forms.Select(attrs={'class': 'form-control','required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        super(DepartmentForm, self).__init__(*args, **kwargs)
        # Make both fields required
        self.fields['name'].required = True
        self.fields['status'].required = True
        # Add empty label for select field
        self.fields['status'].empty_label = "Select Status"

