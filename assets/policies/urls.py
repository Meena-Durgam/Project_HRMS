from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_policies, name='manage_policies'),
    path('add/', views.add_policy, name='add_policy'),
    path('edit/<int:pk>/', views.edit_policy, name='edit_policy'),
    path('delete/<int:pk>/', views.delete_policy, name='delete_policy'),
    path('view/<int:pk>/', views.view_policy, name='view_policy'),
]
