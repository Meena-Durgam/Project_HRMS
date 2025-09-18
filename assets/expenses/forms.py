from django import forms
from .models import Expense

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            'expense_title',
            'category',
            'employee',
            'department',
            'expense_date',
            'amount',
            'paid_by',
            'expense_type',
            'receipt_upload',
            'status',
            'description',
        ]
        
        widgets = {
            'expense_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Expense Title',
                'required': 'required'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
            'employee': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
            'department': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
            'expense_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'DD/MM/YYYY',
                'required': 'required'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Amount',
                'required': 'required'
            }),
            'paid_by': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
            'expense_type': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
            'receipt_upload': forms.ClearableFileInput(attrs={
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter Description',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control custom-select-padding select-arrow-spacing',
                'required': 'required'
            }),
        }

        labels = {
            'expense_title': 'Expense Title',
            'expense_date': 'Expense Date',
            'paid_by': 'Paid By',
            'expense_type': 'Expense Type',
            'receipt_upload': 'Receipt Upload',
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make ForeignKey and ChoiceFields required
        if 'employee' in self.fields:
            self.fields['employee'].empty_label = "Select Employee"
            self.fields['employee'].required = True

        if 'department' in self.fields:
            self.fields['department'].empty_label = "Select Department"
            self.fields['department'].required = True

        if 'category' in self.fields:
            self.fields['category'].choices = [('', 'Select Category')] + [
                (val, label) for val, label in self.fields['category'].choices if val != ''
            ]
            self.fields['category'].required = True

        if 'paid_by' in self.fields:
            self.fields['paid_by'].choices = [('', 'Select Paid By')] + [
                (val, label) for val, label in self.fields['paid_by'].choices if val != ''
            ]
            self.fields['paid_by'].required = True

        if 'expense_type' in self.fields:
            self.fields['expense_type'].choices = [('', 'Select Expense Type')] + [
                (val, label) for val, label in self.fields['expense_type'].choices if val != ''
            ]
            self.fields['expense_type'].required = True

        if 'status' in self.fields:
            self.fields['status'].choices = [('', 'Select Status')] + [
                (val, label) for val, label in self.fields['status'].choices if val != ''
            ]
            self.fields['status'].required = True

        # Make additional fields required
        for field_name in ['expense_title', 'expense_date', 'amount']:
            if field_name in self.fields:
                self.fields[field_name].required = True

        # Remove Django default colon (:) after label
        for field in self.fields.values():
            field.label_suffix = ''
