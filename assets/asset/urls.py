from django.urls import path
from . import views

urlpatterns = [
    path('', views.asset_list, name='asset_list'),
    path('add/', views.add_asset, name='add_asset'),
    path('edit/<int:asset_id>/', views.edit_asset, name='edit_asset'),
    path('delete/<int:asset_id>/', views.delete_asset, name='delete_asset'),
]