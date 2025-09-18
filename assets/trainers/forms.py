from django import forms
from .models import Trainer

class TrainerForm(forms.ModelForm):
    class Meta:
        model = Trainer
        exclude = ['company']  # Company is set in the view

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'trainer_role': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trainer Role'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email',
                'autocomplete': 'off'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone',
                'inputmode': 'numeric',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'Please enter a 10-digit phone number using numbers only',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
                'autocomplete': 'off'
            }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Short Bio', 'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain digits only.")
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and not forms.EmailField().clean(email):
            raise forms.ValidationError("Please enter a valid email address.")
        return email
