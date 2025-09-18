from django.urls import path
from . import views

urlpatterns = [
    path('employee/', views.employee_leave, name='employee_leave'),
    path('leave/delete/<int:leave_id>/', views.delete_leave, name='delete_leave'),
    path('leave/create-type/', views.create_leave_type_and_assign, name='create_leave_type'),
path('leave/review-all/', views.review_all_leave_requests, name='review_all_leave_requests'),
path('leave/type/edit/<int:type_id>/', views.edit_leave_type, name='edit_leave_type'),
path('leave/type/delete/<int:type_id>/', views.delete_leave_type, name='delete_leave_type'),
    path('company-owner/', views.company_owner_leave, name='company_owner_leave'),
path('leave-types/<int:leave_type_id>/assign/', views.assign_leave_balance, name='assign_leave_balances'),

   
]
