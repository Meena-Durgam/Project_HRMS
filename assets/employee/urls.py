# employee/urls.py
from django.urls import path
from . import views


urlpatterns = [
path('view-profile/<int:pk>/', views.view_profile, name='view_profile'),
    path('employee/<int:employee_id>/financial/', views.admin_update_financial_info, name='admin_update_financial_info'),   
    path('employee/profile/approval/<int:emp_id>/', views.toggle_employee_profile_approval, name='toggle_employee_profile_approval'),
    path('company/employees/', views.company_employee_list, name='company_employee_list'),
    path('ajax/load-designations/', views.ajax_load_designations, name='ajax_load_designations'),
path('modal/manage/', views.employee_manage_modal, name='employee_manage_modal'),
path('employee/get/<int:pk>/', views.get_employee_data, name='get_employee_data'),
path('employee/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('employee/<int:employee_id>/add-education/', views.add_education, name='add_education'),
path('ajax/check-email/', views.check_email, name='check_email'),

    path('my-profile/', views.employee_profile, name='employee_profile')
   
]
