from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    EmployeeProfile, EmergencyContact,
    Education, Experience, BankDetails
)

@receiver(post_save, sender=EmergencyContact)
@receiver(post_save, sender=Education)
@receiver(post_save, sender=Experience)
@receiver(post_save, sender=BankDetails)
def check_profile_on_related_save(sender, instance, **kwargs):
    try:
        instance.employee.profile.check_profile_completion()
    except:
        pass

@receiver(post_save, sender=EmployeeProfile)
def check_profile_on_profile_save(sender, instance, **kwargs):
    instance.check_profile_completion()
