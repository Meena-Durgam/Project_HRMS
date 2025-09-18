from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField  # ✅ Required for skill choices

# Optional: only if you're using Job model somewhere
from jobs.models import Job  


from django.db import models
from django.conf import settings
from multiselectfield import MultiSelectField
from django.core.exceptions import ValidationError



class JobSeekerProfile(models.Model):
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    SKILL_CHOICES = [
        ("Python", "Python"), ("Java", "Java"), ("JavaScript", "JavaScript"),
        ("HTML", "HTML"), ("CSS", "CSS"), ("Django", "Django"),
        ("React", "React"), ("Node.js", "Node.js"), ("SQL", "SQL"),
        ("MySQL", "MySQL"), ("PostgreSQL", "PostgreSQL"), ("MongoDB", "MongoDB"),
        ("AWS", "AWS"), ("Azure", "Azure"), ("Docker", "Docker"),
        ("Kubernetes", "Kubernetes"), ("Git", "Git"), ("Linux", "Linux"),
        ("Agile", "Agile"), ("Figma", "Figma"), ("Photoshop", "Photoshop"),
        ("Illustrator", "Illustrator"), ("SEO", "SEO"), ("Google Ads", "Google Ads"),
        ("Excel", "Excel"), ("Data Analysis", "Data Analysis"),
        ("Machine Learning", "Machine Learning"), ("Deep Learning", "Deep Learning"),
        ("TensorFlow", "TensorFlow"), ("PyTorch", "PyTorch"), ("NLP", "NLP"),
        ("Communication", "Communication"), ("Teamwork", "Teamwork"),
        ("Leadership", "Leadership"), ("Project Management", "Project Management"),
        ("Time Management", "Time Management"), ("Creativity", "Creativity"),
        ("Critical Thinking", "Critical Thinking"), ("Problem Solving", "Problem Solving"),
        ("Adaptability", "Adaptability"), ("Testing", "Testing"),
        ("REST API", "REST API"), ("FastAPI", "FastAPI"), ("Bootstrap", "Bootstrap"),
        ("Tailwind CSS", "Tailwind CSS"), ("TypeScript", "TypeScript"),
        ("Vue.js", "Vue.js"), ("Spring Boot", "Spring Boot"), ("Flutter", "Flutter"),
        ("Android Development", "Android Development"), ("iOS Development", "iOS Development"),
        ("Others", "Others"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='jobseekerprofile'
    )

    # Increased length to store "ID-###"
    jobseeker_id = models.CharField(max_length=10, unique=True, blank=True, null=True)

    # Personal Info
    full_name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15, blank=True)
    hometown = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    current_location = models.CharField(max_length=255, blank=True, null=True)

    # Preferences
    preferred_location = models.CharField(max_length=255, blank=True)
    preferred_domain = models.CharField(max_length=255, blank=True)
    salary_expectation = models.PositiveIntegerField(blank=True, null=True)
    skills = MultiSelectField(choices=SKILL_CHOICES, blank=True)

    # Experience
    work_experience = models.TextField(blank=True)

    # File Uploads
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    certificate = models.FileField(upload_to='certificates/', blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validate Resume - only PDF
        if self.resume and not self.resume.name.lower().endswith('.pdf'):
            raise ValidationError({'resume': 'Only PDF files are allowed.'})

        # Validate Profile Picture - only JPG/PNG
        if self.profile_picture:
            valid_extensions = ['.jpg', '.jpeg', '.png']
            if not any(self.profile_picture.name.lower().endswith(ext) for ext in valid_extensions):
                raise ValidationError({'profile_picture': 'Only JPG, JPEG, or PNG images are allowed.'})

    def save(self, *args, **kwargs):
        if not self.jobseeker_id:
            last_profile = JobSeekerProfile.objects.exclude(
                jobseeker_id__isnull=True
            ).order_by('-jobseeker_id').first()

            if last_profile and last_profile.jobseeker_id:
                try:
                    last_num = int(last_profile.jobseeker_id.replace("ID-", ""))
                except ValueError:
                    last_num = 0
                new_num = last_num + 1
            else:
                new_num = 1

            # Format as ID-01, ID-02, ID-100, etc.
            self.jobseeker_id = f"ID-{str(new_num).zfill(2)}"

        super().save(*args, **kwargs)

    def _str_(self):
        return self.full_name or self.user.email
    
    
# Experience Model
class Experience(models.Model):
    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name='experiences'
    )
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    def _str_(self):
        return f"{self.job_title} at {self.company}"


# Internship Model
from django.db import models

class Internship(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='internships')
    title = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    description = models.TextField(blank=True)

    def _str_(self):
        return f"{self.title} at {self.company}"


from django.db import models
from django.core.exceptions import ValidationError
import os

from jobseeker.models import JobSeekerProfile  # adjust import as needed


def validate_pdf(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError("Only PDF files are allowed.")
    if value.content_type != 'application/pdf':
        raise ValidationError("Invalid file type. Only PDF is allowed.")


class Certificate(models.Model):
    user = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name='certificates'
    )
    title = models.CharField(max_length=255)
    file = models.FileField(
        upload_to='certificates/',
        validators=[validate_pdf]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.title
    


# Education Model
class Education(models.Model):
    DEGREE_CHOICES = [
        ("High School", "High School"),
        ("Diploma", "Diploma"),
        ("Bachelor of Arts", "Bachelor of Arts"),
        ("Bachelor of Science", "Bachelor of Science"),
        ("Bachelor of Commerce", "Bachelor of Commerce"),
        ("Bachelor of Technology", "Bachelor of Technology"),
        ("Master of Arts", "Master of Arts"),
        ("Master of Science", "Master of Science"),
        ("Master of Commerce", "Master of Commerce"),
        ("Master of Technology", "Master of Technology"),
        ("MBA", "MBA"),
        ("MCA", "MCA"),
        ("PhD", "PhD"),
        
    ]

    profile = models.ForeignKey(
        JobSeekerProfile,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    degree = models.CharField(max_length=100, choices=DEGREE_CHOICES)

    institution = models.CharField(max_length=200)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)

    def _str_(self):
        return f"{self.degree} from {self.institution} ({self.start_year} - {self.end_year})"

class SavedJob(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_jobs')
    jobseeker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_jobs',
        null=True,
        blank=True
    )
    saved_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"{self.jobseeker.username if self.jobseeker else 'Unknown User'} saved {self.job.title}"

class JobSeekerApplication(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('under_review', 'Under Review'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='job_seeker_applications')
    jobseeker_profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='job_seeker_applications')
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='job_seeker_applications/resumes/', blank=True, null=True)
    interview_date = models.DateField(null=True, blank=True)
    interview_time = models.TimeField(null=True, blank=True)
    interview_mode = models.CharField(max_length=20, choices=[('Online', 'Online'), ('Offline', 'Offline')], null=True, blank=True)

    def _str_(self):
        return f"{self.jobseeker_profile.full_name} - {self.job.title} ({self.status})"

    @property
    def is_interview_scheduled(self):
        return self.status == 'interview_scheduled' and self.interview_date and self.interview_time

    class Meta:
        unique_together = ('job', 'jobseeker_profile')