from django.db.models.signals import post_save
from django.dispatch import receiver
from jobs.models import InterviewRound
from django.core.mail import send_mail

@receiver(post_save, sender=InterviewRound)
def send_interview_notification(sender, instance, created, **kwargs):
    if created:
        jobseeker = instance.application.jobseeker_profile.user
        interview_date = instance.date.strftime('%d %b %Y')
        interview_time = instance.start_time.strftime('%I:%M %p')

        # Send email
        send_mail(
            subject='Upcoming Interview Scheduled',
            message=f"Hi {jobseeker.first_name},\n\nYou have an interview scheduled on {interview_date} at {interview_time}. Please check your dashboard for more details.\n\nGood luck!",
            from_email='noreply@jobportal.com',  # change if needed
            recipient_list=[jobseeker.email],
            fail_silently=True,
        )
