from django.urls import path
from . import views

urlpatterns = [
    # URL for activities page
    path('activities/', views.activities, name='activities'),
    # Any other URL patterns for your app
]
