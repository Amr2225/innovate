from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollments
from assessment.models import AssessmentScore
from decimal import Decimal


@receiver(post_save, sender=AssessmentScore)
def update_enrollment_total_grade(sender, instance, created, **kwargs):
    """
    Signal to update enrollment total_grade when an AssessmentScore is created or updated
    """
    if created:
        # Get enrollment by id and course
        enrollment = Enrollments.objects.get(
            id=instance.enrollment.id,
            course=instance.assessment.course
        )

        current_Total_Grade = Decimal(str(enrollment.total_score))
        enrollment.total_grade = current_Total_Grade + instance.total_score
        enrollment.save()
