# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('subscription/', views.company_subscription_page, name='company_subscription_page'),
    path('subscribe/<int:plan_id>/', views.subscribe_to_package, name='subscribe_to_package'),
]