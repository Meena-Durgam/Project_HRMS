from django.urls import path
from .views import company_owner_dashboard, employee_dashboard

urlpatterns = [
    path('company/', company_owner_dashboard, name='company_owner_dashboard'),
    path('employee/', employee_dashboard, name='employee_dashboard'),
]
