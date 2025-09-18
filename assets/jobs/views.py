from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .models import Job, JobApplicant, Department
from .forms import JobForm, JobApplicationForm
from .utils.google_meet_helper import create_google_meet_event

from datetime import date
from datetime import datetime, timedelta
from django.utils import timezone
import json

@csrf_exempt
def oauth2callback(request):
    # OAuth logic placeholder
    pass

@login_required
def applied_candidates(request):
    role = getattr(request.user, 'role', None)
    company = request.user.company

    if role in ['company_owner', 'employee_admin']:
        applicants = JobApplicant.objects.filter(company=company)
    elif role == 'employee':
        applicants = JobApplicant.objects.filter(company=company, email=request.user.email)
    else:
        applicants = JobApplicant.objects.none()

    return render(request, 'applied_candidates.html', {'applicants': applicants})

@csrf_protect
@require_POST
def update_applicant_status(request, applicant_id):
    try:
        applicant = get_object_or_404(JobApplicant, id=applicant_id, company=request.user.company)
        data = json.loads(request.body)
        new_status = data.get('status')
        role = getattr(request.user, 'role', None)

        if role in ['company_owner', 'employee_admin']:
            if new_status in ['new', 'hired', 'interview_scheduled', 'rejected']:
                applicant.status = new_status
                applicant.save()
                return JsonResponse({'message': 'Status updated successfully.'})
            else:
                return JsonResponse({'error': 'Invalid status.'}, status=400)
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

from django.core.paginator import Paginator

from django.core.paginator import Paginator
from django.utils import timezone
from .forms import JobForm
from .models import Job, Department

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Job, Department
from .forms import JobForm

from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Job, Department
from .forms import JobForm  # ensure your ModelForm is correct



from employee.models import Employee
from jobseeker.models import JobSeekerProfile  # adjust if needed

@login_required
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    role = getattr(request.user, 'role', None)

    form = JobApplicationForm()
    if role in ['employee', 'company']:
        base_template = 'base.html'
    elif role == 'jobseeker':
        base_template = 'base_job.html'
    else:
        base_template = 'base.html'

    # Prefill data
    name = email = phone = ''
    resume_file = None
    has_applied = False
    jobseeker = None
    employee = None

    # Populate from Employee
    if role == 'employee':
        try:
            employee = Employee.objects.get(user=request.user)
            name = f"{employee.first_name} {employee.last_name}"
            email = employee.email or request.user.email
            phone = getattr(employee, 'phone', '')
            if hasattr(employee, 'resume') and employee.resume:
                resume_file = employee.resume.url
        except Employee.DoesNotExist:
            messages.error(request, "Employee profile not found.")
            return redirect('job_list')

    # Populate from JobSeeker
    elif role == 'jobseeker':
        try:
            jobseeker = JobSeekerProfile.objects.get(user=request.user)
            name = jobseeker.full_name
            email = jobseeker.user.email
            phone = jobseeker.contact_number
            resume_file = jobseeker.resume.url if jobseeker.resume else None
        except JobSeekerProfile.DoesNotExist:
            messages.error(request, "Jobseeker profile not found.")
            return redirect('all_jobs')

    # Check if already applied
    if email:
        has_applied = JobApplicant.objects.filter(job=job, email=email).exists()

    # Handle form submission
    if request.method == 'POST' and not has_applied:
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            applicant = form.save(commit=False)
            applicant.job = job
            applicant.name = name
            applicant.email = email
            applicant.phone = phone
            applicant.status = 'new'
            applicant.company = job.company

            # ✅ Save jobseeker_profile_id and jobseeker_id
            if role == 'jobseeker' and jobseeker:
                applicant.jobseeker_profile_id = jobseeker.id
                applicant.jobseeker_id = jobseeker.jobseeker_id  # <-- This saves the 3-char ID

            # ✅ Attach resume if not already provided
            if not applicant.resume:
                if role == 'employee' and employee and employee.resume:
                    applicant.resume = employee.resume
                elif role == 'jobseeker' and jobseeker and jobseeker.resume:
                    applicant.resume = jobseeker.resume

            applicant.save()

            # ✅ Create JobApplication for interview tracking
            JobApplication.objects.create(
                company=job.company,
                applicant=applicant,
                job=job,
                status='new'
            )

            messages.success(request, "Application submitted successfully.")
            return redirect('job_detail', job_id=job.id)

    elif has_applied:
        form = None

    return render(request, 'job_details.html', {
        'job': job,
        'form': form,
        'role': role,
        'has_applied': has_applied,
        'today': date.today(),
        'base_template': base_template,
        'prefill_name': name,
        'prefill_email': email,
        'prefill_phone': phone,
        'resume_url': resume_file,
    })

# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Job
from .forms import JobForm

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from .models import Job, Department
from .forms import JobForm


@login_required
def job_list(request):
    role = getattr(request.user, 'role', None)
    company = getattr(request.user, 'company', None)

    # ✅ Auto-close expired jobs
    Job.objects.filter(status='Open', expired_date__lt=timezone.now().date()).update(status='Closed')

    # ✅ Base queryset for jobs by company
    jobs_queryset = Job.objects.filter(company=company)
    departments = Department.objects.filter(company=company)

    # ✅ Filtering
    title = request.GET.get('title')
    job_type = request.GET.get('job_type')
    status = request.GET.get('status')
    salary_sort = request.GET.get('salary_sort')

    if title:
        jobs_queryset = jobs_queryset.filter(title__icontains=title)
    if job_type:
        jobs_queryset = jobs_queryset.filter(job_type=job_type)
    if status:
        jobs_queryset = jobs_queryset.filter(status=status)

    # ✅ Sorting logic
    if salary_sort == 'low-to-high':
        jobs_queryset = jobs_queryset.order_by('salary_from')
    elif salary_sort == 'high-to-low':
        jobs_queryset = jobs_queryset.order_by('-salary_from')
    else:
        jobs_queryset = jobs_queryset.order_by('-created_at')  # Latest jobs first

    # ✅ Pagination (dynamic per_page, default 5)
    per_page = request.GET.get('per_page', 5)
    try:
        per_page = int(per_page)
    except ValueError:
        per_page = 5  # fallback if invalid

    paginator = Paginator(jobs_queryset, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # ✅ Forms for editing each job (CKEditor support)
    forms = {}
    for job in page_obj:
        form = JobForm(instance=job, company=company)
        form.fields['description'].widget.attrs['id'] = f'ckeditor5-description-{job.id}'
        forms[job.id] = form

    # ✅ Add job form (for modal)
    if request.method == 'POST' and role in ['company_owner', 'employee_admin']:
        form = JobForm(request.POST, company=company)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.save()
            messages.success(request, "Job added successfully!")
            return redirect('job_list')  # Redirect to clear POST data
        else:
            messages.error(request, "There was an error adding the job. Please check the form.")
    else:
        form = JobForm(company=company)

    return render(request, 'manage_jobs.html', {
        'page_obj': page_obj,
        'form': form,
        'forms': forms,
        'departments': departments,
        'role': role,
        'salary_sort': salary_sort,
        'per_page': per_page,  # ✅ pass per_page to template
    })

@login_required
def edit_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # ✅ Permission check
    if request.user.role not in ['company_owner', 'employee_admin'] or job.company != request.user.company:
        messages.error(request, "You do not have permission to edit this job.")
        return redirect('job_list')

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job, company=request.user.company)
        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
        else:
            messages.error(request, "There was an error updating the job. Please check the form.")
        return redirect('job_list')

    # 🚨 No direct edit template (handled in modal), redirect back
    return redirect('job_list')


# ✅ Delete Job
@login_required
def delete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, company=request.user.company)

    if request.user.role in ['company_owner', 'employee_admin']:
        job.delete()
        messages.success(request, "Job deleted successfully!")
    else:
        messages.error(request, "You do not have permission to delete this job.")

    return redirect('job_list')

from jobs.utils.oauth_calendar import create_meet_event
from django.contrib import messages
from .models import InterviewRound, JobApplication




@login_required
def join_meeting(request, applicant_id):
    user = request.user
    company = user.company
    applicant = get_object_or_404(JobApplicant, id=applicant_id, company=company)

    # Allow only owner/admin or the interviewee (if internal and email matches)
    if user.role in ['company_owner'] or (applicant.is_internal and applicant.email == user.email):
        if applicant.meeting_link:
            return redirect(applicant.meeting_link)
        else:
            return JsonResponse({'error': 'No meeting link available.'}, status=404)
    return JsonResponse({'error': 'Permission denied.'}, status=403)


from employee.models import Employee
def employee_interviews(request):
    employee = Employee.objects.get(user=request.user)

    # Filter applicants where employee is internal or assigned
    interviews = JobApplicant.objects.filter(
        is_internal=True,
        interview_date__isnull=False,
        meeting_link__isnull=False
    )

    return render(request, 'interviews.html', {
        'interviews': interviews
    })

@login_required
def join_meeting_interviewer(request, applicant_id):
    user = request.user
    role = getattr(user, 'role', None)

    # Ensure user is company owner and has a company
    if role == 'company_owner' and hasattr(user, 'company'):
        company = user.company

        # Check that applicant belongs to this company
        applicant = get_object_or_404(JobApplicant, id=applicant_id)

        # Redirect to meeting link if available
        if applicant.meeting_link:
            return redirect(applicant.meeting_link)
        else:
            return JsonResponse({'error': 'No meeting link available.'}, status=404)

    return JsonResponse({'error': 'Permission denied.'}, status=403)


@login_required
def join_meeting_interviewee(request, applicant_id):
    user = request.user
    company = user.company
    applicant = get_object_or_404(JobApplicant, id=applicant_id, company=company)

    if applicant.email == user.email and applicant.status == 'interview_scheduled':
        if applicant.meeting_link:
            return redirect(applicant.meeting_link)
        else:
            return JsonResponse({'error': 'No meeting link available.'}, status=404)
    else:
        return JsonResponse({'error': 'Permission denied.'}, status=403)
    

def all_jobs_view(request):
    jobs = Job.objects.filter(status='Open').order_by('-start_date')
    return render(request, 'career.html',{'jobs':jobs})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from datetime import datetime, timedelta
from .models import JobApplicant, JobApplication, InterviewRound, Job   
from django.views.decorators.http import require_POST
from django.utils.timezone import now


@login_required
def applicant_list(request):
    user = request.user
    company = getattr(user, 'company', None)
    role = getattr(user, 'role', None)

    job_id = request.GET.get('job_id')
    name_query = request.GET.get('name', '').strip()
    status_query = request.GET.get('status', '').strip()

    # Step 1: Base applicants queryset - prefetch related jobseeker_profile to avoid N+1 queries
    if job_id:
        applicants = JobApplicant.objects.select_related(
            'jobseeker_profile', 'job'
        ).filter(job_id=job_id)
    else:
        job_ids = Job.objects.filter(company=company).values_list('id', flat=True)
        applicants = JobApplicant.objects.select_related(
            'jobseeker_profile', 'job'
        ).filter(job_id__in=job_ids)

    # Step 2: Apply filters
    if name_query:
        applicants = applicants.filter(name__icontains=name_query)
    if status_query:
        applicants = applicants.filter(status=status_query)

    # Step 3: Get related JobApplication instances
    applications = JobApplication.objects.filter(applicant__in=applicants)

    # Step 4: Map (applicant_id, job_id) → JobApplication
    applications_map = {
        (applicant.id, applicant.job_id): applications.filter(
            applicant=applicant, job=applicant.job
        ).first()
        for applicant in applicants
    }

    # Step 5: Prepare enriched data
    enriched_applicants = []
    for applicant in applicants:
        application = applications_map.get((applicant.id, applicant.job_id))
        latest_round = None
        current_round = 1
        meeting_link = None

        if application:
            rounds = InterviewRound.objects.filter(application=application).order_by('-round_number')
            if rounds.exists():
                latest_round = rounds.first()
                meeting_link = latest_round.meeting_link or None
                current_round = (
                    latest_round.round_number + 1
                    if latest_round.status == 'shortlisted'
                    else latest_round.round_number
                )

        # Attach display properties
        applicant.latest_round = latest_round.round_number if latest_round else None
        applicant.latest_round_obj = latest_round
        applicant.meeting_link = meeting_link

        # ✅ Add jobseeker_id & contact number fallback logic
        applicant.display_jobseeker_id = (
            applicant.jobseeker_profile.jobseeker_id
            if applicant.jobseeker_profile else None
        )
        applicant.display_phone = (
            applicant.jobseeker_profile.contact_number
            if applicant.jobseeker_profile and applicant.jobseeker_profile.contact_number
            else applicant.phone
        )

        enriched_applicants.append({
            'applicant': applicant,
            'current_round': current_round,
        })

    # Step 6: Paginate
    paginator = Paginator(enriched_applicants, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Step 7: Render
    return render(request, 'job_applicants.html', {
        'applicants': applicants,
        'job_id': job_id,
        'rounds': [1, 2, 3],
        'applicants_data': page_obj,
        'page_obj': page_obj,
    })
from django.urls import reverse
@login_required
def schedule_interview(request, applicant_id):
    user = request.user
    company = getattr(user, 'company', None)
    role = getattr(user, 'role', None)

    if request.method == 'POST' and role == 'company_owner':
        applicant = get_object_or_404(JobApplicant, id=applicant_id)
        if applicant.job.company != company:
            return JsonResponse({'error': 'Unauthorized access to this applicant.'}, status=403)

        job_id = request.POST.get('job_id')
        job = get_object_or_404(Job, pk=job_id)

        # Get or create job application
        job_application, _ = JobApplication.objects.get_or_create(
            applicant=applicant,
            job=job,
            defaults={'company': company}
        )

        # ✅ Determine next round number dynamically
        existing_rounds = InterviewRound.objects.filter(application=job_application).order_by('round_number')
        existing_round_numbers = list(existing_rounds.values_list('round_number', flat=True))
        round_number = max(existing_round_numbers) + 1 if existing_round_numbers else 1

        # ✅ Check eligibility
        if round_number == 1 and applicant.status != 'new':
            return JsonResponse({'error': 'Only new applicants can start Round 1.'}, status=400)
        elif round_number > 1:
            last_round = existing_rounds.last()
            if last_round.status == 'rejected':
                return JsonResponse({'error': f'Rejected in Round {last_round.round_number}. Cannot proceed.'}, status=400)
            if not last_round.status or last_round.status != 'shortlisted':
                return JsonResponse({'error': f'Submit feedback for Round {last_round.round_number} first.'}, status=400)

        # ✅ Parse input values
        try:
            interview_date = request.POST.get('date')
            interview_time = request.POST.get('time')
            interview_mode = request.POST.get('mode')
            round_type = request.POST.get('round_type')
            venue = request.POST.get('message', '')

            interview_date_obj = datetime.strptime(interview_date, "%Y-%m-%d").date()
            start_dt = datetime.strptime(f"{interview_date} {interview_time}", "%Y-%m-%d %H:%M")
            end_dt = start_dt + timedelta(minutes=30)
        except Exception as e:
            return JsonResponse({'error': f'Invalid date/time input: {str(e)}'}, status=400)

        # ✅ Generate meeting link if online
        meet_link = None
        if interview_mode.lower() == 'online':
            try:
                meet_link = create_meet_event(
                    summary=f"Interview Round {round_number}",
                    description=f"Interview with {applicant.name} ({round_type})",
                    start_datetime=start_dt,
                    end_datetime=end_dt,
                    attendee_email=applicant.email
                )
            except Exception as e:
                return JsonResponse({'error': f'Meeting generation failed: {str(e)}'}, status=400)

        # ✅ Save Interview Round
        InterviewRound.objects.create(
            application=job_application,
            round_number=round_number,
            round_type=round_type,
            interview_date=interview_date_obj,
            interview_time=interview_time,
            interview_mode=interview_mode,
            venue_details=venue if interview_mode.lower() == 'offline' else '',
            meeting_link=meet_link if interview_mode.lower() == 'online' else '',
            feedback=''  # feedback will be added after interview
        )

        # ✅ Update applicant and application status
        applicant.status = 'interview_scheduled'
        applicant.interview_date = interview_date_obj
        applicant.interview_time = interview_time
        applicant.interview_mode = interview_mode
        applicant.meeting_link = meet_link
        applicant.save()

        job_application.status = 'interview_scheduled'
        job_application.save()

        messages.success(request, f'Interview Round {round_number} scheduled for {applicant.name}.')
        return redirect(f"{reverse('applicant_list')}?job_id={job_id}")

    return JsonResponse({'error': 'Invalid request or permission denied.'}, status=400)


@require_POST
@login_required
def submit_feedback(request, applicant_id):
    applicant = get_object_or_404(JobApplicant, id=applicant_id)
    status = request.POST.get('status')
    feedback = request.POST.get('feedback')
    round_number = request.POST.get('round_number')

    if not all([status, feedback, round_number]):
        messages.error(request, "All fields are required.")
        return redirect(request.META.get('HTTP_REFERER'))

    job_application = JobApplication.objects.filter(applicant=applicant).first()
    if not job_application:
        messages.error(request, "No application found.")
        return redirect(request.META.get('HTTP_REFERER'))

    # Get or create interview round
    round_obj, _ = InterviewRound.objects.get_or_create(
        application=job_application,
        round_number=int(round_number),
        defaults={'interviewed_by': request.user, 'created_at': now()}
    )

    # Update interview round details
    round_obj.status = status
    round_obj.feedback = feedback
    round_obj.feedback_given_at = now()
    round_obj.interviewed_by = request.user
    round_obj.save()

    # Update application & applicant status
    if status == 'rejected':
        applicant.status = 'rejected'
        job_application.status = 'rejected'

    elif status == 'shortlisted':
        applicant.status = 'interview_scheduled'
        job_application.status = 'interview_scheduled'

    elif status == 'hired':
        applicant.status = 'hired'
        job_application.status = 'hired'

        # ✅ Auto-generate offer letter
        if not hasattr(job_application, 'offer_letter'):
            offer = generate_offer_letter(job_application)
            if offer:
                messages.success(request, f"Offer letter auto-generated for {applicant.name}.")
            else:
                messages.error(request, f"Failed to generate offer letter for {applicant.name}.")

    applicant.save()
    job_application.save()

    messages.success(request, f"Feedback for Round {round_number} submitted.")
    return redirect(request.META.get('HTTP_REFERER'))


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import JobApplication
from .utils.offer_letter import generate_offer_letter
from django.contrib.auth.decorators import login_required

@login_required
def generate_offer_letter_view(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id)

    # Normalize the status to compare safely
    status = application.status.strip().lower()

    if status != 'hired':
        messages.error(request, "Offer letter can only be generated for hired applicants.")
        return redirect(request.META.get('HTTP_REFERER', 'jobs:applications'))

    if hasattr(application, 'offer_letter'):
        messages.warning(request, "Offer letter already generated.")
        return redirect(request.META.get('HTTP_REFERER', 'jobs:applications'))

    offer = generate_offer_letter(application)
    if offer:
        messages.success(request, "Offer letter generated successfully.")
    else:
        messages.error(request, "Failed to generate offer letter.")

    return redirect(request.META.get('HTTP_REFERER', 'jobs:applications'))


from django.db.models import Q

@login_required
def job_applications_list(request):
    company = getattr(request.user, 'company', None)

    # Get search query parameters
    applicant_name = request.GET.get('applicant_name', '').strip()
    job_title = request.GET.get('job_title', '').strip()

    # Base queryset for hired applications
    applications = JobApplication.objects.select_related(
        'job', 'applicant', 'employee', 'job__company'
    ).filter(status='hired')

    # Filter by company (if recruiter)
    if company:
        applications = applications.filter(company=company)

    # Filter by applicant name
    if applicant_name:
        applications = applications.filter(
            Q(applicant__full_name__icontains=applicant_name)
        )

    # Filter by job title
    if job_title:
        applications = applications.filter(
            Q(job__title__icontains=job_title)
        )

    context = {
        'applications': applications,
        'applicant_name': applicant_name,
        'job_title': job_title
    }
    return render(request, 'job_applications_list.html', context)

@login_required
def job_feedback_view(request, applicant_id):
    application = get_object_or_404(JobApplication, applicant__id=applicant_id)
    rounds = InterviewRound.objects.filter(application=application).order_by('round_number')

    # Get previous page URL from HTTP_REFERER or fallback to applicant list
    previous_url = request.META.get('HTTP_REFERER', reverse('applicant_list'))

    return render(request, 'job_feedback.html', {
        'application': application,
        'rounds': rounds,
        'previous_url': previous_url,
    })