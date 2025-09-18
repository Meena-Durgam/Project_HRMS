from django.urls import path
from . import views

urlpatterns = [
    path('', views.expense_list, name='expense_list'),
    path('expenses/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
# urls.py
path('expenses/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
]
