from django.urls import path
from . import views

urlpatterns = [
    path('trainers/', views.trainer_list, name='trainer_list'),
    path('toggle-status/<int:trainer_id>/<str:new_status>/', views.trainer_toggle_status, name='trainer_toggle_status'),
    path('edit/<int:trainer_id>/', views.edit_trainer, name='edit_trainer'),


]
