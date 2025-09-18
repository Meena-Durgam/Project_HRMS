from django.urls import path
from . import views

urlpatterns = [
    path('resignation/add/', views.add_resignation, name='add_resignation'),
    path('resignation/', views.resignation_list, name='resignation_list'),
    
    path('company-resignations/', views.company_resignation_list, name='company_resignation_list'),
    path('resignation/<int:resignation_id>/update-status/', views.update_resignation_status, name='update_resignation_status'),
    path('resignation/<int:resignation_id>/approve/', views.approve_resignation, name='approve_resignation'),
    path('resignation/<int:resignation_id>/reject/', views.reject_resignation, name='reject_resignation'),
]
