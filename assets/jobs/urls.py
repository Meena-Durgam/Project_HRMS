from django.urls import path
from . import views
from jobs.views import job_list  # adjust if your view is in another app
urlpatterns = [
    path('jobs/', views.job_list, name='job_list'),
    path('applicants/', views.applicant_list, name='applicant_list'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('schedule/<int:applicant_id>/', views.schedule_interview, name='schedule_interview'),
    path('job/<int:job_id>/edit/', views.edit_job, name='edit_job'),
    path('jobs/delete/<int:job_id>/', views.delete_job, name='delete_job'),
    path('interviews/', views.employee_interviews, name='employee_interviews'),
    path('update_applicant_status/<int:applicant_id>/', views.update_applicant_status, name='update_applicant_status'),
    path('join-meeting/interviewer/<int:applicant_id>/', views.join_meeting_interviewer, name='join_meeting_interviewer'),
    path('join-meeting/interviewee/<int:applicant_id>/', views.join_meeting_interviewee, name='join_meeting_interviewee'),
    path('all-jobs/', views.all_jobs_view, name='all_jobs'),
    path('jobs/', job_list, name='recruiter_jobs'),
    path('applicants/<int:applicant_id>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('generate-offer/<int:application_id>/', views.generate_offer_letter_view, name='generate_offer_letter'),
    path('applications/', views.job_applications_list, name='job_applications_list'),
    path('applicant/feedback/<int:applicant_id>/', views.job_feedback_view, name='job_feedback'),
    path('job/edit/<int:job_id>/', views.edit_job, name='edit_job'),

]
