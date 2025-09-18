from django.urls import path
from . import views

urlpatterns = [
    path('', views.promotion_list, name='promotion_list'),            # List all promotions
    path('add/', views.promotion_add, name='promotion_add'),          # Add new promotion
    path('edit/<int:pk>/', views.promotion_edit, name='promotion_edit'),  # Edit promotion
    path('delete/<int:pk>/', views.promotion_delete, name='promotion_delete'),  # Delete promotion
]