from django.urls import path
from . import views

urlpatterns = [
    path('calendar/', views.calendar_view, name='calendar_view'),
    path('add_event/', views.add_event, name='add_event'),
    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('calendar/all_events/', views.all_events, name='all_events'),
    path("get_events/", views.get_events, name="get_events"),


]