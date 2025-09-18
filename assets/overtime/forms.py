from django import forms
from .models import Overtime
from django.contrib.auth import get_user_model

User = get_user_model()

class OvertimeForm(forms.ModelForm):
    class Meta:
        model = Overtime
        fields = ['employee', 'date', 'hours', 'ot_type', 'assigned_by']  # Include assigned_by here

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OvertimeForm, self).__init__(*args, **kwargs)

        if self.user:
            # Restrict employee selection
            if self.user.role == 'employee':
                self.fields['employee'].widget = forms.HiddenInput()
                self.fields['employee'].initial = self.user
            else:
                self.fields['employee'].queryset = User.objects.filter(role='employee', company=self.user.company)

            # Assign 'assigned_by' field visibility and filtering
            if self.user.role == 'company_owner':
                # Hide assigned_by — auto-filled in views
                self.fields['assigned_by'].queryset = User.objects.filter(company=self.user.company)
                self.fields['assigned_by'].label_from_instance = lambda obj: obj.email

            else:
                # Show HR employees only
                hr_users = User.objects.filter(
                    employee_account__department__name__iexact='human resources',
                    company=self.user.company
                )

                self.fields['assigned_by'].queryset = hr_users
                self.fields['assigned_by'].required = True
