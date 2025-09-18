from django.urls import path
from . import views

urlpatterns = [
    path('payitems/', views.manage_payitems, name='manage_payitems'),
    path('payitems/delete/<int:pk>/', views.delete_payitem, name='delete_payitem'),
    path('payitems/edit/', views.edit_payitem, name='edit_payitem'),  # ✅ This line fixes your issue
    path('manage/', views.manage_payroll, name='manage_payroll'),
    path('delete/<int:pk>/', views.delete_payroll, name='delete_payroll'),
     path('get_payitems/<int:employee_id>/', views.get_employee_payitems, name='get_employee_payitems'),
    path('generate-payslip/<int:payroll_id>/', views.generate_payslip, name='generate_payslip'),

]