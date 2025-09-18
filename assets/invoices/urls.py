from django.urls import path
from . import views

urlpatterns = [
    path('', views.invoice_list, name='invoice_list'),
    path('create/', views.invoice_create, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail, name='invoice_detail'),
    path('<int:pk>/update/', views.invoice_update, name='invoice_update'),
    path('<int:pk>/delete/', views.invoice_delete, name='invoice_delete'),
    path('payments/', views.invoice_payments, name='invoice_payments'),
    path('ajax/load-projects-estimates/', views.load_projects_estimates, name='load_projects_estimates'),
    
    path('report/', views.invoice_report_view, name='invoice_report_view'),

]
