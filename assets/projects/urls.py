from django.urls import path
from . import views

urlpatterns = [
    # Project URLs
    path('', views.project_list, name='project_list'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('view/<int:pk>/', views.project_view, name='project_view'),
    path('projects/<int:project_id>/update-priority/', views.update_priority, name='update_priority'),
    path('projects/update-status/<int:project_id>/', views.update_status, name='update_status'),
    path('my-projects/',views.my_projects_view, name='my_projects'),
    # Task URLs
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/view/', views.task_view, name='task_view'),
path('projects/tasks/<int:pk>/edit/', views.edit_task, name='edit_task'),
    path('tasks/<int:task_id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:task_id>/update-priority/', views.update_task_priority, name='update_task_priority'),
    path('tasks/<int:task_id>/progress/', views.add_task_progress, name='add_task_progress'),
    path('ajax/get-project-team-members/', views.get_project_team_members, name='get_project_team_members'),

    # Task Board
    path('task-board/', views.task_board, name='task_board'),

    # AJAX
    path('get-team-members/<int:project_id>/', views.get_team_members, name='get_team_members'),
    path('ajax/task/<int:task_id>/status/', views.update_task_status_ajax, name='update_task_status_ajax'),
]
