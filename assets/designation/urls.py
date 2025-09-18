from django.urls import path
from .views import manage_designations,delete_designation

urlpatterns = [
    path('manage/', manage_designations, name='manage_designations'),
    path('designation/delete/<int:pk>/', delete_designation, name='delete_designation'),
]
