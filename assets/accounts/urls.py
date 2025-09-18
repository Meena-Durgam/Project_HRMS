from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.company_signup, name='company_signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('setup-company-profile/', views.setup_company_profile, name='setup_company_profile'),
    path('company/details/', views.company_details, name='company_details'),
    path('jobseeker/signup/', views.jobseeker_signup_view, name='jobseeker_signup'),
    path('company/profile/', views.company_profile_view, name='company_profile'),
        path('ajax/check-email/', views.check_email, name='check_email'),

    path('employee/post-login/', views.employee_post_login, name='employee_post_login'),  # NEW
]
