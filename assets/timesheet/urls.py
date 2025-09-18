from django.urls import path
from . import views

urlpatterns = [
    path('employee/submit/', views.submit_timesheet, name='submit_timesheet'),
    path('employee/clock_in/', views.clock_in, name='clock_in'),
    path('employee/clock_out/', views.clock_out, name='clock_out'),
    path('admin/timesheets/', views.all_timesheets, name='all_timesheets'),
    path('admin/timesheet/status/<int:pk>/<str:status>/', views.update_timesheet_status, name='update_timesheet_status'),
]
