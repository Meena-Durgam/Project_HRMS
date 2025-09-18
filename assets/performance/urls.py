from django.urls import path
from . import views

urlpatterns = [
    # Performance Indicator URLs
    path('performance-indicators/', views.performance_indicator_list, name='performance_indicator_list'),
    path('performance-indicators/create/', views.performance_indicator_create, name='performance_indicator_create'),
    path('performance-indicators/update/<int:pk>/', views.performance_indicator_update, name='performance_indicator_update'),
    path('performance-indicators/delete/<int:pk>/', views.performance_indicator_delete, name='performance_indicator_delete'),
    path('performance-indicators/toggle-status/<int:pk>/<str:new_status>/', views.performance_indicator_toggle_status, name='performance_indicator_toggle_status'),

    # Performance Appraisal URLs
    path('appraisals/', views.appraisal_list, name='appraisal_list'),
    path('appraisals/add/', views.appraisal_create, name='appraisal_create'),
    path('appraisals/edit/<int:pk>/', views.appraisal_update, name='appraisal_update'),
    path('appraisals/delete/<int:pk>/', views.appraisal_delete, name='appraisal_delete'),




    path('performance/', views.performance_list, name='performance_list'),
    
    



]
