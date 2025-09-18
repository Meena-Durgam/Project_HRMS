from django import forms
from .models import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['employee', 'name', 'purchase_date', 'warranty', 'warranty_end', 'value', 'status']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'warranty_end': forms.DateInput(attrs={'type': 'date'}),
        }