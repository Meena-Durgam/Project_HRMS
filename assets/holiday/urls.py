from django.urls import path
from . import views

urlpatterns = [
    path('', views.holiday_list, name='holiday_list'),
    path('export/', views.export_holidays_csv, name='export_holidays_csv'),
    path('holidays/delete/<int:id>/', views.delete_holiday, name='delete_holiday'),
    path('holidays/edit/<int:id>/', views.edit_holiday, name='edit_holiday'),
    path('add/', views.add_holiday, name='add_holiday'),
]
