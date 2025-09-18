from django.urls import path
from . import views

urlpatterns = [
    # Goal Type CRUD (Company Owner Only)
    path('goal-types/', views.goal_type_list, name='goal_type_list'),

    # Goal List View (All Employees + Owner)
    path('goals/', views.goal_list, name='goal_list'),

    # Add, Edit, Delete Goal (POST only for add/edit/delete)
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('goals/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),
]
