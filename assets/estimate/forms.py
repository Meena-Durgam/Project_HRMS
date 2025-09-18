from django import forms
from datetime import date, datetime
from .models import Estimate, EstimateItem
from .utils import is_hr_user
from tax.models import Tax
from clients.models import Client
from projects.models import Project
from django.utils.safestring import mark_safe

class EstimateForm(forms.ModelForm):
    class Meta:
        model = Estimate
        fields = [
            'client', 'project', 'billing_address',
            'estimate_date', 'expiry_date',
            'tax', 'discount', 'other_information', 'status'
        ]
        widgets = {
            'billing_address': forms.Textarea(attrs={'rows': 3}),
            'other_information': forms.Textarea(attrs={'rows': 3}),
            'estimate_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase py-3',
                'placeholder': 'MM/DD/YYYY',
                'type': 'date'
            }),

            'discount': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # ✅ Only these fields will be required
        required_fields = ['client','project', 'billing_address', 'estimate_date', 'expiry_date', 'tax', 'status']
        common_style = 'height: 38px; width: 100%; resize: none;'

        for field_name, field in self.fields.items():
            widget = field.widget
            widget.attrs['class'] = f"{widget.attrs.get('class', '')} form-control".strip()
            widget.attrs['style'] = common_style

            # ✅ Set required only for selected fields
            field.required = field_name in required_fields

            # ✅ Add red star for required fields
            label = field.label.replace('_', ' ').title()
            if field.required:
                label += ' <span style="color:red;">*</span>'
            field.label = mark_safe(label)

        # Date constraints
        today_str = date.today().isoformat()
        self.fields['estimate_date'].widget.attrs['min'] = today_str
        self.fields['expiry_date'].widget.attrs['min'] = today_str

        if 'expiry_date' in self.initial:
            expiry = self.initial['expiry_date']
            if isinstance(expiry, (date, datetime)):
                self.initial['expiry_date'] = expiry.strftime('%d/%m/%Y')

        # Company filtering
        if self.user:
            try:
                company = getattr(self.user, 'employee_account', None) and self.user.employee_account.company \
                          or getattr(self.user, 'company', None)

                self.fields['tax'].queryset = Tax.objects.filter(company=company, status='Active')
                self.fields['client'].queryset = Client.objects.filter(company=company, status='Active')
                 # Remove default '------' and set custom placeholders
                self.fields['client'].empty_label = 'Select Client'
                self.fields['project'].empty_label = 'Select Project'
                self.fields['tax'].empty_label = 'Select Tax'
                client_id = self.data.get('client') or self.initial.get('client')
                if client_id:
                    self.fields['project'].queryset = Project.objects.filter(client_id=client_id, company=company)
                elif self.instance.pk and self.instance.client:
                    self.fields['project'].queryset = Project.objects.filter(client=self.instance.client, company=company)
                else:
                    self.fields['project'].queryset = Project.objects.none()
            except Exception:
                self.fields['tax'].queryset = Tax.objects.none()
                self.fields['client'].queryset = Client.objects.none()
                self.fields['project'].queryset = Project.objects.none()

                # Still set empty labels even if empty queryset
                self.fields['client'].empty_label = 'Select Client'
                self.fields['project'].empty_label = 'Select Project'
                self.fields['tax'].empty_label = 'Select Tax'

    def clean(self):
        cleaned_data = super().clean()
        estimate_date = cleaned_data.get('estimate_date')
        expiry_date = cleaned_data.get('expiry_date')

        if estimate_date and estimate_date < date.today():
            self.add_error('estimate_date', 'Estimate date cannot be in the past.')

        if expiry_date and expiry_date < date.today():
            self.add_error('expiry_date', 'Expiry date cannot be in the past.')

        if estimate_date and expiry_date and expiry_date < estimate_date:
            self.add_error('expiry_date', 'Expiry date must be after the estimate date.')

        if self.user and not is_hr_user(self.user):
            raise forms.ValidationError("Only HR department employees or company owners can create or update estimates.")

        return cleaned_data

from django import forms
from django.utils.safestring import mark_safe
from .models import EstimateItem

class EstimateItemForm(forms.ModelForm):
    class Meta:
        model = EstimateItem
        fields = ['item_name', 'description', 'unit_cost', 'quantity']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 1}),
            'unit_cost': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        common_style = 'height: 38px; width: 100%; resize: none;'

        for field_name, field in self.fields.items():
            # Make every field required in Django & HTML
            field.required = True
            field.widget.attrs['required'] = 'required'

            # Add Bootstrap class & styling
            widget = field.widget
            classes = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{classes} form-control'.strip()
            widget.attrs['style'] = common_style

            # Add red * in label
            label = field.label.replace('_', ' ').title()
            label += ' <span style="color:red;">*</span>'
            field.label = mark_safe(label)
