from django import forms
from .models import Invoice, InvoiceItem
from estimate.models import Estimate
from clients.models import Client
from projects.models import Project
from tax.models import Tax
from invoices.utils import get_company_from_user


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'client',
            'estimate',
            'project',
            'invoice_date',
            'due_date',
            'tax',
            'discount',
            'notes',
            'status',
        ]
        widgets = {
            'invoice_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase py-3',
                'placeholder': 'MM/DD/YYYY',
                'type': 'date'
            }),
            'discount': forms.NumberInput(attrs={'step': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'estimate': 'Estimate',
            'client': 'Client Name',
            'project': 'Project',
            'invoice_date': 'Invoice Date',
            'due_date': 'Due Date',
            'tax': 'Tax',
            'discount': 'Discount (%)',
            'notes': 'Notes',
            'status': 'Status',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Required fields
        required_fields = ['client', 'project', 'invoice_date', 'due_date', 'status', 'tax']
        for field_name in required_fields:
            self.fields[field_name].required = True

        # Styling all fields
        for field_name, field in self.fields.items():
            widget = field.widget
            widget.attrs.setdefault('class', 'form-control')
            widget.attrs.setdefault('style', 'height: 38px; width: 100%; resize: none;')

        # ✅ Remove default "------" and replace with "Select ..."
        self.fields['client'].empty_label = "Select Client"
        self.fields['project'].empty_label = "Select Project"
        self.fields['estimate'].empty_label = "Select Estimate"
        self.fields['tax'].empty_label = "Select Tax"

        company = get_company_from_user(self.user)

        if company:
            self.fields['client'].queryset = Client.objects.filter(company=company, status='Active')
            self.fields['tax'].queryset = Tax.objects.filter(company=company, status='Active')

            client_id = self.data.get('client') or getattr(self.instance, 'client_id', None)

            if client_id:
                self.fields['project'].queryset = Project.objects.filter(client_id=client_id, company=company)
                self.fields['estimate'].queryset = Estimate.objects.filter(client_id=client_id, company=company)
            else:
                self.fields['project'].queryset = Project.objects.none()
                self.fields['estimate'].queryset = Estimate.objects.none()
        else:
            self.fields['client'].queryset = Client.objects.none()
            self.fields['project'].queryset = Project.objects.none()
            self.fields['estimate'].queryset = Estimate.objects.none()
            self.fields['tax'].queryset = Tax.objects.none()


from django import forms
from django.utils.safestring import mark_safe
from .models import InvoiceItem


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item_name', 'description', 'unit_cost', 'quantity']
        widgets = {
            'unit_cost': forms.NumberInput(attrs={
                'step': '0.01',
                'min': '0',
                'required': 'required'
            }),
            'quantity': forms.NumberInput(attrs={
                'min': '1',
                'required': 'required'
            }),
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

