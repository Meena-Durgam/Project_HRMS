# department/urls.py
from django.urls import path
from .views import manage_departments,delete_department

urlpatterns = [
    path('', manage_departments, name='manage_departments'),
    path('delete/<int:pk>/', delete_department, name='delete_department'),
]
