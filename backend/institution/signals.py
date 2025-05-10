from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment


@receiver(post_save, sender=Payment)
def update_institution_credits(sender, instance, created, **kwargs):
    """
    Signal to update institution credits when a new payment is created
    """
    if created and instance.payment_status == 'success':
        institution = instance.institution
        # Add the new credits to the existing credits
        current_credits = institution.credits or 0
        institution.credits = current_credits + instance.credits_amount
        institution.save()
