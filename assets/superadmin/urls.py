from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('companies/', views.company_list_view, name='company_list'),
    path('subscription/', views.subscription_package_view, name='package_list'),
    path('domain-purchase/', views.domain_purchase_view, name='domain_purchases'),
    path('transactions/', views.transaction_list_view, name='transactions'),
    
    path('packages/edit/<int:plan_id>/', views.edit_plan, name='edit_plan'),
    path('packages/delete/<int:plan_id>/', views.delete_plan, name='delete_plan'),
    
    path('subscribed-companies/', views.subscribed_companies_list, name='subscribed_companies_list'),


]