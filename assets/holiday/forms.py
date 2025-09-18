from django import forms
from datetime import date, timedelta
from .models import Holiday

class HolidayForm(forms.ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'min': (date.today() + timedelta(days=1)).isoformat(),  # ✅ Only allow dates from tomorrow
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically set min attribute again during form rendering (for safety)
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        self.fields['date'].widget.attrs['min'] = tomorrow

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date <= date.today():
            raise forms.ValidationError("You can only select future dates (from tomorrow onward).")
        return selected_date
