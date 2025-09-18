from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        exclude = ('company', 'client_id', 'created_at')
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Client Name',
            }),
            'client_company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Company Name',
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
            }),
       'phone': forms.TextInput(attrs={
    'class': 'form-control',
    'inputmode': 'numeric',
    'id': 'phone',
    'maxlength': '10',   # ✅ Restrict to 10 digits
    'oninput': "this.value = this.value.replace(/[^0-9]/g, '')",
    'placeholder': 'Enter 10-Digit Phone Number',
}),

            'address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Address',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ClientForm, self).__init__(*args, **kwargs)

        # Add default choice for status
        choices_list = list(self.fields['status'].choices)
        self.fields['status'].choices = [('', 'Select Status')] + choices_list[1:]

        # Apply placeholders for fields not covered in Meta
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if field.required:
                field.widget.attrs['class'] += ' required'

        # Ensure address is required
        self.fields['phone'].required = True
        self.fields['address'].required = True

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")

        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")

        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_status(self):
        status = self.cleaned_data.get('status')
        print("STATUS RECEIVED IN FORM:", repr(status))  # Debug

        if status:
            status = status.strip().capitalize()

        valid_statuses = ['Active', 'Inactive', 'Blocked']
        if status not in valid_statuses:
            raise forms.ValidationError("Invalid status.")
        
        return status


from django import forms
from .models import Agreement
# clients/forms.py
from django import forms
from .models import Agreement

from django import forms
from .models import Agreement

from django import forms
from .models import Agreement

from django import forms
from django.core.exceptions import ValidationError
from .models import Agreement


class AgreementForm(forms.ModelForm):
    class Meta:
        model = Agreement
        fields = [
            'start_date', 'end_date', 'contract_type', 'agreement_file',
            'payment_term', 'contract_value'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date',
                'required': 'required'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control text-uppercase',
                'type': 'date',
                'required': 'required'
            }),
            'contract_type': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'agreement_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf, image/*'   # ✅ Frontend restriction
            }),
            'payment_term': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contract value',
                'required': 'required'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Replace first option label for select fields
        if self.fields['contract_type'].choices:
            self.fields['contract_type'].choices = [('', 'Select Contract Type')] + list(self.fields['contract_type'].choices)[1:]

        if self.fields['payment_term'].choices:
            self.fields['payment_term'].choices = [('', 'Select Payment Term')] + list(self.fields['payment_term'].choices)[1:]

        # ✅ Ensure all fields styled + required
        for field_name, field in self.fields.items():
            css_classes = field.widget.attrs.get('class', '')
            if 'form-control' not in css_classes:
                css_classes += ' form-control'
            if field.required and 'required' not in css_classes:
                css_classes += ' required'
            field.widget.attrs['class'] = css_classes.strip()
            if field.required:
                field.widget.attrs['required'] = 'required'

    # ✅ File validation
    def clean_agreement_file(self):
        file = self.cleaned_data.get('agreement_file')
        if file:
            valid_mime_types = ['application/pdf', 'image/jpeg', 'image/png']
            if hasattr(file, 'content_type') and file.content_type not in valid_mime_types:
                raise ValidationError("Only PDF, JPG, JPEG, and PNG files are allowed.")
            if file.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("File size must be under 5MB.")
        return file



from django import forms
from django.utils.safestring import mark_safe
from .models import ClientDocument
from django import forms
from django.utils.safestring import mark_safe
from .models import ClientDocument

class ClientDocumentForm(forms.ModelForm):
    class Meta:
        model = ClientDocument
        fields = ['document_type', 'other_document_type', 'document_file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'other_document_type': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Specify other document type'}),
            'document_file': forms.ClearableFileInput(attrs={
                'class': 'form-control', 'required': True, 'accept': '.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""
        # ✅ Replace first option label for document_type
        if self.fields['document_type'].choices:
            choices_list = list(self.fields['document_type'].choices)
            self.fields['document_type'].choices = [('', 'Select Document')] + choices_list[1:]

        # Make specific fields required
        self.fields['document_type'].required = True
        self.fields['document_file'].required = True

        # Add asterisk to required fields
        for field_name, field in self.fields.items():
            if field.required:
                field.label = mark_safe(f"{field.label} <span style='color: red;'>*</span>")

    def clean(self):
        cleaned_data = super().clean()
        document_type = cleaned_data.get("document_type")
        other_doc_type = cleaned_data.get("other_document_type")

        # other_document_type required if document_type is Other
        if document_type == "Other" and not other_doc_type:
            self.add_error('other_document_type', "This field is required when document type is 'Other'.")

        # Clear other_document_type if not Other
        if document_type != "Other":
            cleaned_data['other_document_type'] = ''

        return cleaned_data

    def clean_document_file(self):
        file = self.cleaned_data.get("document_file")

        if file:
            # ✅ Ensure only .pdf files
            if not file.name.lower().endswith(".pdf"):
                raise forms.ValidationError("Only PDF files are allowed.")

            # ✅ Content type check (some browsers return 'application/x-pdf')
            if file.content_type not in ["application/pdf", "application/x-pdf"]:
                raise forms.ValidationError("Invalid file type. Please upload a valid PDF file.")

            # ✅ Optional: Check file size (e.g., max 5MB)
            if file.size > 5 * 1024 * 1024:  # 5 MB
                raise forms.ValidationError("File size must be less than 5 MB.")

        return file
