# termination/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.termination_list, name='termination_list'),
    path('edit/<int:pk>/', views.edit_termination, name='edit_termination'),
    path('delete/<int:pk>/', views.delete_termination, name='delete_termination'),
]
