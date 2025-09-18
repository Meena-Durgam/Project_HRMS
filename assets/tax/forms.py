from django import forms
from .models import Tax

class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'percentage', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Tax Name',
                'required': 'required'
            }),
            'percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Enter Percentage',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make all fields required
        for field in self.fields.values():
            field.required = True

        # Replace default choices for 'status'
        choices = list(self.fields['status'].choices)
        if choices and choices[0][0] == '':
            choices.pop(0)  # Remove the default "---------"
        self.fields['status'].choices = [('', 'Select status')] + choices

