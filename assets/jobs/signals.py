# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import JobApplication
from .utils.offer_letter import generate_offer_letter

@receiver(post_save, sender=JobApplication)
def auto_generate_offer_pdf(sender, instance, **kwargs):
    if instance.status == 'hired':
        generate_offer_letter(instance)
