from django.urls import path
from .views import JobSeekerProfileView
from . import views

urlpatterns = [
    path('profile/', JobSeekerProfileView.as_view(), name='profile_view'),
    path('profile/<str:jobseeker_id>/', JobSeekerProfileView.as_view(), name='profile_view_other'),
    path('dashboard/', views.jobseeker_dashboard, name='jobseeker_dashboard'),
    path('jobs/', views.job_list_view, name='job_list_jobseeker'),
    path('save-job/', views.save_job_view, name='save_job'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    path('apply/<int:job_id>/', views.apply_for_job, name='apply_job'),
    path('unsave-job/<int:saved_id>/', views.unsave_job_view, name='unsave_job'),
    path('manage_application/<int:application_id>/', views.manage_applications_jobseeker, name='manage_applications'),
    path('applied-jobs/', views.applied_jobs_view, name='applied_jobs_view'),
    
]