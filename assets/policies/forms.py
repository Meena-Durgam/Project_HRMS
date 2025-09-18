from django import forms
from .models import Policy

class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter policy name',
            }),
            'description': forms.Textarea(attrs={
                'id': 'ckeditor5-description',
                'class': 'form-control',
                'placeholder': 'Enter description',
            }),
        }
