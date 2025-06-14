from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from mcqQuestion.models import McqQuestion
from HandwrittenQuestion.models import HandwrittenQuestion
from DynamicMCQ.models import DynamicMCQ


def update_assessment_grade(assessment):
    if assessment:
        # Use the property to sum all question grades
        assessment.grade = assessment.total_grade
        # Only update the grade field
        assessment.save(update_fields=['grade'])


@receiver([post_save, post_delete], sender=McqQuestion)
def mcq_question_changed(sender, instance, **kwargs):
    update_assessment_grade(instance.assessment)


@receiver([post_save, post_delete], sender=DynamicMCQ)
def dynamic_mcq_question_changed(sender, instance, **kwargs):
    if hasattr(instance, 'assessment') and instance.assessment:
        update_assessment_grade(instance.assessment)


@receiver([post_save, post_delete], sender=HandwrittenQuestion)
def handwritten_question_changed(sender, instance, **kwargs):
    update_assessment_grade(instance.assessment)
