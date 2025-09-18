from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import JobSeekerProfileForm, SaveJobForm
from .models import JobSeekerProfile, SavedJob
from jobs.models import Job, JobApplicant
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .models import Experience, Internship, Education, Certificate
from .forms import ExperienceForm, InternshipForm, EducationForm, JobSeekerProfileForm, CertificateForm 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from .models import Experience, Internship, Education, Certificate
from .forms import ExperienceForm, InternshipForm, EducationForm, JobSeekerProfileForm
from .forms import (
    JobSeekerProfileForm, SkillsForm,
    ExperienceForm, InternshipForm, EducationForm, CertificateForm
)
from .models import JobSeekerProfile
# at the top of jobseeker/views.py
from django.forms import modelformset_factory
from .models import Experience
from .forms import ExperienceForm

# right after your imports, before the view class:
ExperienceFormSet = modelformset_factory(
    Experience,
    form=ExperienceForm,
    extra=1,
    can_delete=True,
)


from .forms import (
    JobSeekerProfileForm, SkillsForm,
    ExperienceForm, InternshipForm, EducationForm, CertificateForm
)
from .models import JobSeekerProfile
# at the top of jobseeker/views.py
from django.forms import modelformset_factory
from .models import Experience
from .forms import ExperienceForm

# right after your imports, before the view class:
ExperienceFormSet = modelformset_factory(
    Experience,
    form=ExperienceForm,
    extra=1,
    can_delete=True,
)

from django.forms import modelformset_factory
from .models import Internship
from .forms import InternshipForm

InternshipFormSet = modelformset_factory(
    Internship,
    form=InternshipForm,
    extra=1,
    can_delete=True
)


EducationFormSet = modelformset_factory(
    Education,
    form=EducationForm,
    extra=2,
    can_delete=True
)
CertificateFormSet = modelformset_factory(
    Certificate,
    form=CertificateForm,
    extra=2,
    can_delete=True
)

class JobSeekerProfileView(LoginRequiredMixin, View):
    template_name = 'jobseeker/profile_combined.html'
    readonly_template_name = 'jobseeker/profile_readonly.html'

    def get_profile(self, request, jobseeker_id=None):
        """Get the profile depending on if it's own profile or another user's."""
        if jobseeker_id:
            return get_object_or_404(JobSeekerProfile, jobseeker_id=jobseeker_id)
        else:
            profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
            if created:
                profile.user = request.user
                profile.save()
            return profile

    def get_context_data(self, request, profile, editable, jobseeker_id=None):
        """
        Prepare context for rendering with correct base template:
        - If jobseeker_id is provided (company owner view) → base.html
        - If no jobseeker_id (own profile) → base_job.html
        """
        if jobseeker_id:
            base_template = 'base.html'      # Company owner view
        else:
            base_template = 'base_job.html'  # Jobseeker view own profile

        return {
            'user': request.user,
            'profile': profile,
            'editable': editable,
            'base_template': base_template,
            'profile_form': JobSeekerProfileForm(instance=profile) if editable else None,
            'skills_form': SkillsForm(instance=profile) if editable else None,
            'experience_formset': ExperienceFormSet(queryset=profile.experiences.all()) if editable else None,
            'internship_formset': InternshipFormSet(queryset=profile.internships.all()) if editable else None,
            'education_formset': EducationFormSet(queryset=profile.educations.all()) if editable else None,
            'certificate_formset': CertificateFormSet(queryset=profile.certificates.all()) if editable else None,
            'experiences': profile.experiences.all(),
            'internships': profile.internships.all(),
            'educations': profile.educations.all(),
            'certificates': profile.certificates.all(),
        }

    def get(self, request, jobseeker_id=None):
        profile = self.get_profile(request, jobseeker_id)
        editable = (jobseeker_id is None)
        context = self.get_context_data(request, profile, editable, jobseeker_id)

        # Switch template: readonly if viewing other's profile
        template = self.readonly_template_name if jobseeker_id else self.template_name
        return render(request, template, context)

    def post(self, request, jobseeker_id=None):
        """Handle profile updates (only allowed for owner)."""
        if jobseeker_id:
            messages.error(request, "You cannot edit another jobseeker's profile.")
            return redirect('profile_view_other', jobseeker_id=jobseeker_id)

        profile = self.get_profile(request)
        action = request.POST.get("action")
        context = self.get_context_data(request, profile, editable=True, jobseeker_id=jobseeker_id)

        if action == "save_profile":
            form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "There was an error updating the profile.")
                context['profile_form'] = form

        elif action == "save_skills":
            form = SkillsForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Skills updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "There was an error updating skills.")
                context['skills_form'] = form

        elif action == "save_experiences":
            formset = ExperienceFormSet(request.POST, queryset=profile.experiences.all())
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.profile = profile
                    instance.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Experience details updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "There was an error saving experience details.")
                context['experience_formset'] = formset

        elif action == "save_internships":
            formset = InternshipFormSet(request.POST, queryset=profile.internships.all())
            if formset.is_valid():
                instances = formset.save(commit=False)
                for instance in instances:
                    instance.profile = profile
                    instance.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Internship details updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "There was an error saving internship details.")
                context['internship_formset'] = formset

        elif action == "save_education":
            education_formset = EducationFormSet(request.POST, queryset=profile.educations.all())
            if education_formset.is_valid():
                educations = education_formset.save(commit=False)
                for education in educations:
                    education.profile = profile
                    education.save()
                for obj in education_formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Education details updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "Please correct the errors in the education formset.")
                context['education_formset'] = education_formset

        elif action == "save_certificate":
            certificate_formset = CertificateFormSet(request.POST, request.FILES, queryset=profile.certificates.all())
            if certificate_formset.is_valid():
                certificates = certificate_formset.save(commit=False)
                for certificate in certificates:
                    certificate.profile = profile
                    certificate.save()
                for obj in certificate_formset.deleted_objects:
                    obj.delete()
                messages.success(request, "Certificates updated successfully.")
                return redirect('profile_view')
            else:
                messages.error(request, "Please correct the errors in the certificate formset.")
                context['certificate_formset'] = certificate_formset

        else:
            messages.error(request, "Unknown action submitted.")

        return render(request, self.template_name, context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime
from django.db.models import Q

from jobs.models import JobApplicant, JobApplication, Job, InterviewRound
from .models import SavedJob, JobSeekerProfile
from .forms import JobSeekerProfileForm
from .recommendation import get_recommended_jobs  # Ensure this is implemented

@login_required
def jobseeker_dashboard(request):
    # Get or create jobseeker profile
    profile, _ = JobSeekerProfile.objects.get_or_create(user=request.user)

    # Profile completeness check
    is_profile_incomplete = not all([
        profile.contact_number,
        profile.dob,
        profile.gender,
        profile.current_location,
        profile.preferred_location,
        profile.preferred_domain,
        profile.resume,
        profile.profile_picture,
        bool(profile.skills),
        profile.educations.exists()
    ])

    # Find matching JobApplicant by email
    job_applicant = JobApplicant.objects.filter(email=request.user.email).first()

    # Applied and saved jobs
    applied_jobs = JobApplication.objects.filter(applicant=job_applicant) if job_applicant else JobApplication.objects.none()
    saved_jobs = SavedJob.objects.filter(jobseeker=request.user)

    # Recommended jobs
    recommended_jobs = get_recommended_jobs(request.user) if callable(get_recommended_jobs) else []

    # Latest jobs
    latest_jobs = Job.objects.all().order_by('-start_date')[:6]

    # ✅ Filter only upcoming interviews and add countdown text
    today = date.today()
    now = datetime.now().time()
    upcoming_interviews = []
    all_scheduled_interviews = []  # For calendar display
    
    if job_applicant:
        # Get all scheduled interviews for calendar
        all_interviews = InterviewRound.objects.filter(
            application__applicant=job_applicant
        ).select_related('application__job').order_by('interview_date', 'interview_time')
        
        # Filter upcoming interviews for countdown
        upcoming_interviews = all_interviews.filter(
            Q(interview_date__gt=today) |
            Q(interview_date=today, interview_time__gte=now)
        )

        # Add countdown_text attribute dynamically
        for interview in upcoming_interviews:
            days_left = (interview.interview_date - today).days
            if days_left == 0:
                interview.countdown_text = "Today"
            elif days_left == 1:
                interview.countdown_text = "Tomorrow"
            elif days_left > 1:
                interview.countdown_text = f"In {days_left} days"
            else:
                interview.countdown_text = "Missed"

        # Prepare all interviews for calendar
        for interview in all_interviews:
            all_scheduled_interviews.append({
                'id': interview.id,
                'date': interview.interview_date,
                'time': interview.interview_time,
                'title': interview.application.job.title,
                'round_number': interview.round_number,
                'round_type': interview.round_type,
                'mode': interview.interview_mode,
                'status': interview.status,
                'is_upcoming': interview in upcoming_interviews
            })

    # Profile completion percentage
    filled_fields = sum(bool(field) for field in [
        profile.contact_number,
        profile.dob,
        profile.gender,
        profile.current_location,
        profile.preferred_location,
        profile.preferred_domain,
        profile.resume,
        profile.profile_picture,
        bool(profile.skills),
        profile.educations.exists()
    ])
    total_fields = 10
    profile_completion = int((filled_fields / total_fields) * 100)

    # Profile form (for display or editing)
    form = JobSeekerProfileForm(instance=profile)

    # Context for the dashboard template
    context = {
        'profile': profile,
        'form': form,
        'applied_jobs_count': applied_jobs.count(),
        'saved_jobs_count': saved_jobs.count(),
        'matching_jobs_count': recommended_jobs.count() if recommended_jobs else 0,
        'latest_jobs': latest_jobs,
        'recommended_jobs': recommended_jobs,
        'applications': applied_jobs,
        'application_status': {
            application.id: application.status for application in applied_jobs
        },
        'is_profile_incomplete': is_profile_incomplete,
        'profile_completion': profile_completion,
        'upcoming_interviews': upcoming_interviews,
        'today': today,
        # Add interview data as JSON for JavaScript
        'interviews_json': [
            {
                'id': interview.id,
                'date': interview.interview_date.strftime('%Y-%m-%d') if interview.interview_date else None,
                'time': interview.interview_time.strftime('%H:%M:%S') if interview.interview_time else None,
                'title': interview.application.job.title
            }
            for interview in upcoming_interviews
        ],
        'all_scheduled_interviews': all_scheduled_interviews,
        'calendar_interviews_json': [
            {
                'id': interview['id'],
                'date': interview['date'].strftime('%Y-%m-%d') if interview['date'] else None,
                'time': interview['time'].strftime('%H:%M:%S') if interview['time'] else None,
                'title': interview['title'],
                'round_number': interview['round_number'],
                'round_type': interview['round_type'],
                'mode': interview['mode'],
                'status': interview['status'],
                'is_upcoming': interview['is_upcoming']
            }
            for interview in all_scheduled_interviews
        ],
    }

    return render(request, 'jobseeker_dashboard.html', context)

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Job, SavedJob  # Make sure SavedJob is imported

@login_required
def job_list_view(request):
    job_type = request.GET.get('job_type')
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')

    jobs = Job.objects.filter(status='Open').order_by('-start_date')

    if job_type:
        jobs = jobs.filter(job_type__iexact=job_type)

    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(company__name__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    if location:
        jobs = jobs.filter(location__icontains=location)

    saved_job_ids = list(
        SavedJob.objects.filter(jobseeker=request.user).values_list('job__id', flat=True)
    )

    # Get the current user's JobSeekerProfile
    try:
        jobseeker_profile = request.user.jobseekerprofile
    except JobSeekerProfile.DoesNotExist:
        jobseeker_profile = None

    applied_job_ids = []
    if jobseeker_profile:
        applied_job_ids = list(
            JobSeekerApplication.objects.filter(
                jobseeker_profile=jobseeker_profile
            ).values_list('job_id', flat=True)
        )

    context = {
        'jobs': jobs,
        'saved_job_ids': saved_job_ids,
        'applied_job_ids': applied_job_ids,  # <-- pass applied jobs here
        'job_type': job_type,
        'keyword': keyword,
        'location': location,
    }

    return render(request, 'jobseeker/job_list.html', context)


# Save job view (save a job)
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import SavedJob  # adjust import as needed
from .forms import SaveJobForm  # adjust if form name is different

@login_required
def save_job_view(request):
    if request.method == 'POST':
        form = SaveJobForm(request.POST)
        if form.is_valid():
            job = form.cleaned_data['job']
            saved_job = SavedJob.objects.filter(job=job, jobseeker=request.user).first()

            if saved_job:
                saved_job.delete()
                messages.success(request, 'Job unsaved successfully.')
            else:
                new_saved = form.save(commit=False)
                new_saved.jobseeker = request.user
                new_saved.save()
                messages.success(request, 'Job saved successfully.')
        else:
            messages.error(request, 'Invalid submission.')

    return redirect(request.META.get('HTTP_REFERER', 'job_list_jobseeker'))

from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# View for saved jobs (with filters)
@login_required
def saved_jobs_view(request):
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    # Get all SavedJob objects for this user (with job not expired)
    saved_jobs_qs = SavedJob.objects.filter(
        jobseeker=request.user,
        job__expired_date__gt=tomorrow
    ).select_related('job', 'job__company')

    # Extract saved job IDs
    saved_job_ids = saved_jobs_qs.values_list('job__id', flat=True)

    # Filters
    keyword = request.GET.get('keyword')
    location = request.GET.get('location')
    job_type = request.GET.get('job_type')

    # Apply filters to jobs inside the saved list
    if keyword:
        saved_jobs_qs = saved_jobs_qs.filter(
            Q(job__title__icontains=keyword) |
            Q(job__description__icontains=keyword) |
            Q(job__company__name__icontains=keyword)
        )
    if location:
        saved_jobs_qs = saved_jobs_qs.filter(job__location__icontains=location)
    if job_type:
        saved_jobs_qs = saved_jobs_qs.filter(job__job_type__iexact=job_type)

    return render(request, 'jobseeker/saved_jobs.html', {
        'saved_jobs': saved_jobs_qs,
        'saved_job_ids': list(saved_job_ids),  # used to keep button blue
        'keyword': keyword,
        'location': location,
        'job_type': job_type,
    })

# Apply for job view (submit job application)

from .forms import JobSeekerApplicationForm
from .models import JobSeekerProfile, JobSeekerApplication, Job

def apply_for_job(request, job_id):
    # Get the job and the logged-in jobseeker's profile
    job = Job.objects.get(id=job_id)
    jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)

    # Check if the job seeker has already applied for this job
    if JobSeekerApplication.objects.filter(job=job, jobseeker_profile=jobseeker_profile).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        # Pass the jobseeker profile to the form using the initial keyword argument
        form = JobSeekerApplicationForm(request.POST, request.FILES, initial={'jobseeker_profile': jobseeker_profile})
        if form.is_valid():
            # Save the application with jobseeker_profile automatically populated
            application = form.save(commit=False)
            application.jobseeker_profile = jobseeker_profile
            application.save()

            messages.success(request, f"Application for {job.title} submitted successfully!")
            return redirect('job_list_view')
    else:
        form = JobSeekerApplicationForm(initial={'jobseeker_profile': jobseeker_profile})

    return render(request, 'jobseeker/apply_for_job.html', {'form': form, 'job': job})

# views.py
from .models import JobSeekerApplication

def application_detail(request, application_id):
    application = JobSeekerApplication.objects.select_related('job').get(id=application_id)
    return render(request, 'jobseeker/application_detail.html', {'application': application})


from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from .models import JobSeekerApplication
from .forms import InterviewScheduleForm

def manage_applications_jobseeker(request, application_id):
    # Get the application by ID
    application = get_object_or_404(JobSeekerApplication, id=application_id)
    
    # Get the job associated with the application
    job = application.job
    company = job.company  # Get the company related to the job
    
    # Check if the logged-in user is the company owner
    if request.user.role != 'company_owner' or request.user.company != company:
        # Ensure that the logged-in user is the company owner associated with the job
        messages.error(request, "You are not authorized to manage this application.")
        return redirect('home')

    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST)
        if form.is_valid():
            # Schedule the interview
            application.interview_date = form.cleaned_data['interview_date']
            application.interview_time = form.cleaned_data['interview_time']
            application.interview_mode = form.cleaned_data['interview_mode']
            application.status = 'interview_scheduled'  # Update the status to interview scheduled
            application.save()

            messages.success(request, "Interview scheduled successfully.")
            return redirect('manage_applications_jobseeker', application_id=application.id)
    else:
        form = InterviewScheduleForm()

    return render(request, 'manage_application.html', {
        'application': application, 
        'form': form,
    })

# Unsave a job (remove from saved jobs)
@login_required
def unsave_job_view(request, saved_id):
    saved_job = get_object_or_404(SavedJob, id=saved_id, jobseeker=request.user)
    saved_job.delete()
    messages.success(request, "Job has been removed from saved jobs.")
    return redirect('saved_jobs')



from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jobs.models import JobApplicant

from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jobs.models import JobApplicant  # Your model for job applications

@login_required
def applied_jobs_view(request):
    user = request.user

    # Query all applications by this user's email
    applied_jobs = JobApplicant.objects.filter(email=user.email).select_related('job', 'job__company')

    # Filter parameters from GET request
    job_type = request.GET.get('job_type', '')
    keyword = request.GET.get('keyword', '')
    location = request.GET.get('location', '')

    # Apply filters
    if job_type:
        applied_jobs = applied_jobs.filter(job__job_type__icontains=job_type)

    if keyword:
        applied_jobs = applied_jobs.filter(
            Q(job__title__icontains=keyword) |
            Q(job__company__name__icontains=keyword)
        )

    if location:
        applied_jobs = applied_jobs.filter(job__location__icontains=location)

    # Ordering by most recent application (you can adjust the field if needed)
    applied_jobs = applied_jobs.order_by('-id')

    # Pagination - 6 per page
    paginator = Paginator(applied_jobs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Base template selection based on user role (optional)
    role = getattr(user, 'role', None)
    base_template = 'base.html' if role == 'employee' else 'base_job.html'

    return render(request, 'jobseeker/applied_jobs.html', {
        'applied_jobs': page_obj,  # paginated queryset for template iteration
        'page_obj': page_obj,      # for pagination controls
        'base_template': base_template
    })



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from jobs.models import JobApplication, InterviewRound

@login_required
def jobseeker_applied_jobs(request):
    applied_jobs = (
        JobApplication.objects
        .filter(applicant__user=request.user)
        .select_related('job')
        .prefetch_related('interview_rounds')
    )
    return render(request, 'jobseeker/applied_jobs.html', {'applied_jobs': applied_jobs})


import datetime
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from jobs.models import InterviewRound, JobApplicant
from datetime import datetime, time 

@login_required
def interview_events(request):
    try:
        jobapplicant = JobApplicant.objects.get(email=request.user.email)
    except JobApplicant.DoesNotExist:
        return JsonResponse([], safe=False)

    interviews = InterviewRound.objects.filter(application__applicant=jobapplicant, interview_date__isnull=False)
    events = []
    for interview in interviews:
        interview_time = interview.interview_time or datetime.time(9, 0)
        start_datetime = datetime.datetime.combine(interview.interview_date, interview_time)

        events.append({
            'title': f"Round {interview.round_number} ({interview.round_type or 'Interview'})",
            'start': start_datetime.isoformat(),
            'url': interview.meeting_link or '',
            'extendedProps': {
                'mode': interview.interview_mode,
                'status': interview.status,
                'venue': interview.venue_details or '',
            }
        })

    return JsonResponse(events, safe=False)
