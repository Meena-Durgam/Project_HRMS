from django.urls import path
from . import views

urlpatterns = [
    # Tax URLs
    path('taxes/', views.tax_list, name='tax_list'),
    path('taxes/delete/<int:tax_id>/', views.delete_tax, name='delete_tax'),
    path('taxes/status/<int:tax_id>/<str:status>/', views.change_tax_status, name='change_tax_status'),
]