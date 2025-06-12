from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from assessment.models import Assessment
from mcqQuestion.models import McqQuestion
from HandwrittenQuestion.models import HandwrittenQuestion
from Code_Questions.models import CodingQuestion
from DynamicMCQ.models import DynamicMCQQuestions

def update_assessment_grade(assessment):
    if assessment:
        assessment.grade = assessment.total_grade  # Use the property to sum all question grades
        assessment.save(update_fields=['grade'])   # Only update the grade field

@receiver([post_save, post_delete], sender=McqQuestion)
def mcq_question_changed(sender, instance, **kwargs):
    update_assessment_grade(instance.assessment)

@receiver([post_save, post_delete], sender=DynamicMCQQuestions)
def dynamic_mcq_question_changed(sender, instance, **kwargs):
    if hasattr(instance, 'dynamic_mcq') and instance.dynamic_mcq:
        update_assessment_grade(instance.dynamic_mcq.assessment)

@receiver([post_save, post_delete], sender=HandwrittenQuestion)
def handwritten_question_changed(sender, instance, **kwargs):
    update_assessment_grade(instance.assessment)

@receiver([post_save, post_delete], sender=CodingQuestion)
def coding_question_changed(sender, instance, **kwargs):
    update_assessment_grade(instance.assessment_Id) 