from django.apps import AppConfig


class JobseekerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobseeker'

from django.apps import AppConfig

class InterviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interviews'

    def ready(self):
        import jobseeker.signals  # 👈 add this line
