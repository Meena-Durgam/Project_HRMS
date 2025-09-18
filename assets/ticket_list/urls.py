from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/edit/<int:pk>/', views.edit_ticket, name='edit_ticket'),
    path('tickets/delete/<int:pk>/', views.delete_ticket, name='delete_ticket'),
    path('tickets/<int:pk>/update-status/', views.update_ticket_status, name='update_ticket_status'),

]
