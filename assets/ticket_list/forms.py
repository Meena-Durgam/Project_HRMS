from django import forms
from .models import Ticket, TicketComment
from django.contrib.auth import get_user_model
from clients.models import Client

User = get_user_model()

class TicketForm(forms.ModelForm):
    assigned_staff = forms.ModelChoiceField(
        queryset=User.objects.none(),
        required=False,
        label='Assign to',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    followers = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        required=False,
        label='Add Followers',
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )

    client = forms.ModelChoiceField(
        queryset=Client.objects.none(),
        required=False,
        label='Client',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Ticket
        fields = [
            'subject',
            'assigned_staff',
            'client',
            'cc',
            'priority',
            'description',
            'file',
            'status',
            'followers',
        ]
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter ticket subject...'
            }),
            'cc': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional CC email...'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue or request...'
            }),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        company = kwargs.pop('company', None)  # Expecting company in kwargs
        super().__init__(*args, **kwargs)

        if company:
            self.fields['assigned_staff'].queryset = User.objects.filter(company=company, role='employee')
            self.fields['followers'].queryset = User.objects.filter(company=company, role='employee')
            self.fields['client'].queryset = Client.objects.filter(company=company)
        else:
            self.fields['assigned_staff'].queryset = User.objects.none()
            self.fields['followers'].queryset = User.objects.none()
            self.fields['client'].queryset = Client.objects.none()

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment here...'
            }),
        }
        labels = {
            'comment': '',
        }
