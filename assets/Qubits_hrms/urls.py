"""
URL configuration for Qubits_hrms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from dashboard.views import home 
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', home, name='home'),  
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('department/',include('department.urls')),
    path('designation/',include('designation.urls')),
    path('employee/',include('employee.urls')),
    path('clients/',include('clients.urls')),
    path('leave_management/',include('leave_management.urls')),
    path('ticket_list/',include('ticket_list.urls')),
    path('tax/',include('tax.urls')),
    path('payroll/',include('payroll.urls')),
    path('projects/',include('projects.urls')),
    path('estimate/',include('estimate.urls')),
    path('invoices/',include('invoices.urls')),
    path('goal/',include('goal.urls')),
    path('asset/',include('asset.urls')),
    path('policies/',include('policies.urls')),
    path('promotion/',include('promotion.urls')),
    path('resignation/',include('resignation.urls')),
    path('termination/',include('termination.urls')),
    path('expenses/',include('expenses.urls')),
    path('trainers/',include('trainers.urls')),
    path('training_list/',include('training_list.urls')),
    path('performance/',include('performance.urls')),
    path('holiday/',include('holiday.urls')),
    path('attendance/',include('attendance.urls')),
    path('jobs/',include('jobs.urls')),
    path('timesheet/',include('timesheet.urls')),
    path('overtime /',include('overtime.urls')),
    path('jobseeker/', include('jobseeker.urls')),
    path('select2/', include('django_select2.urls')),
    path('contact/', include('contact.urls')),
    path('notifications/', include('notifications.urls')),
    path('activities/', include('activities.urls')),
    path('event_calendar/', include('event_calendar.urls')),
    path('superadmin/',include('superadmin.urls')),
    path('package/',include('package.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)