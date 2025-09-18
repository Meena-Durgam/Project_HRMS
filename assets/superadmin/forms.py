from django import forms
from .models import Plan, PlanModule

class PlanForm(forms.ModelForm):
    modules = forms.ModelMultipleChoiceField(
        queryset=PlanModule.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Plan
        fields='_all_'