from django.urls import path
from . import views

urlpatterns = [
    path('', views.estimate_list, name='estimate_list'),                     # View all estimates
    path('create/', views.estimate_list_create, name='estimate_create'),     # Create a new estimate (HR only)
    path('<int:pk>/', views.estimate_detail, name='estimate_detail'),        # Detail view of estimate
    path('<int:pk>/update/', views.estimate_update, name='estimate_update'), # Update estimate (HR only)
    path('<int:pk>/delete/', views.estimate_delete, name='estimate_delete'), # Delete estimate (HR only)
    path('ajax/get-projects/', views.get_projects_by_client, name='get_projects_by_client'),

]