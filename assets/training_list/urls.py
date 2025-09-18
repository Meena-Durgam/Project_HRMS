from django.urls import path
from . import views

urlpatterns = [

    # ========================
    # TRAINING MANAGEMENT
    # ========================
    path('trainings/', views.training_list, name='training_list'),
    path('training/delete/<int:training_id>/', views.delete_training, name='delete_training'),
    path('training/update/<int:training_id>/', views.update_training, name='update_training'),
    path('training/toggle-status/<int:id>/<str:status>/', views.training_toggle_status, name='training_toggle_status'),

    # ========================
    # TRAINING TYPE MANAGEMENT
    # ========================
    path('training-types/', views.training_type_list, name='training_type_list'),
    path('training-types/edit/<int:pk>/', views.edit_training_type, name='edit_training_type'),
    path('training-type/delete/<int:pk>/', views.delete_training_type, name='delete_training_type'),
    path('training-type/toggle-status/<int:pk>/<str:status>/', views.toggle_training_type_status, name='toggle_training_type_status'),

]
