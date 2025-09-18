from django import forms
from .models import Resignation

class ResignationForm(forms.ModelForm):
    class Meta:
        model = Resignation
        fields = [
            'resignation_date',
            'last_working_day',
            'notice_period',
            'mode_of_exit',
            'reason',
            'comments',
            'resignation_letter',
            'status',
        ]
        widgets = {
            'resignation_date': forms.DateInput(attrs={'type': 'date'}),
            'last_working_day': forms.DateInput(attrs={'type': 'date'}),
            'reason': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 2}),
        }
