# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications')

]
