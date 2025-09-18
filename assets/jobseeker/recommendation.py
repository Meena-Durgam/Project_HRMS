from django.db.models import Q
from jobs.models import Job
from jobseeker.models import JobSeekerProfile

def get_recommended_jobs(user):
    profile = JobSeekerProfile.objects.filter(user=user).first()
    if not profile or not profile.skills:
        return Job.objects.none()

    q_filter = Q()
    for skill in profile.skills:
        q_filter |= Q(description__icontains=skill) | Q(title__icontains=skill)

    return Job.objects.filter(q_filter).distinct()
