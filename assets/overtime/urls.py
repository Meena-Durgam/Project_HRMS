from django.urls import path
from . import views

urlpatterns = [
    path('', views.overtime_list, name='overtime_list'),
    path('overtime/add/', views.add_overtime, name='add_overtime'),
    
    path('overtime/edit/<int:pk>/', views.edit_overtime, name='edit_overtime'),
    path('overtime/delete/<int:pk>/', views.delete_overtime, name='delete_overtime'),


]
