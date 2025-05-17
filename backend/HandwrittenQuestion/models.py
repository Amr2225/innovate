import uuid
from django.db import models
from assessment.models import Assessment
from users.models import User
from enrollments.models import Enrollments
from django.conf import settings
import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

def get_handwritten_answer_path(instance, filename):
    # Get the assessment ID from the question
    assessment_id = instance.question.assessment.id
    # Create path: AssessmentUploads/assessment_id/filename
    return os.path.join(settings.ASSESSMENT_UPLOADS_DIR, str(assessment_id), filename)

class HandwrittenQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='handwritten_questions')
    question_text = models.TextField()
    answer_key = models.TextField(help_text="The correct answer or key points for evaluation", blank=True, null=True)
    max_grade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(100)],
        help_text="Maximum grade for this question"
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_handwritten_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['assessment']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.assessment.title} - Question {self.id}"

    def save(self, *args, **kwargs):
        # Ensure max_grade is not greater than assessment grade
        if self.max_grade > self.assessment.grade:
            raise ValidationError("Question grade cannot be greater than assessment grade")
        super().save(*args, **kwargs)

class HandwrittenQuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(HandwrittenQuestion, on_delete=models.CASCADE, related_name='scores')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='handwritten_scores')
    score = models.FloatField(
        validators=[MinValueValidator(0)],
        default=0
    )
    feedback = models.TextField(blank=True, null=True)
    answer_image = models.ImageField(upload_to='handwritten_answers/')
    extracted_text = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    evaluated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['question', 'enrollment']
        ordering = ['-submitted_at']
        indexes = [
            models.Index(fields=['question', 'enrollment']),
            models.Index(fields=['submitted_at']),
        ]

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.question.assessment.title} - {self.score}"

    def save(self, *args, **kwargs):
        # Ensure score is not negative
        self.score = max(0, self.score)
        super().save(*args, **kwargs)

        # Update assessment score
        assessment = self.question.assessment
        from assessment.models import AssessmentScore
        assessment_score, created = AssessmentScore.objects.get_or_create(
            enrollment=self.enrollment,
            assessment=assessment,
            defaults={'total_score': 0}
        )
        
        # Calculate total score including both MCQ and Handwritten scores
        mcq_total = assessment.mcq_questions.filter(
            scores__enrollment=self.enrollment
        ).aggregate(total=models.Sum('scores__score'))['total'] or 0
        
        handwritten_total = assessment.handwritten_questions.filter(
            scores__enrollment=self.enrollment
        ).aggregate(total=models.Sum('scores__score'))['total'] or 0
        
        assessment_score.total_score = mcq_total + handwritten_total
        assessment_score.save()

@receiver(post_delete, sender=HandwrittenQuestionScore)
def update_assessment_score_on_delete(sender, instance, **kwargs):
    """Update AssessmentScore when a HandwrittenQuestionScore is deleted"""
    try:
        assessment = instance.question.assessment
        from assessment.models import AssessmentScore
        assessment_score = AssessmentScore.objects.get(
            enrollment=instance.enrollment,
            assessment=assessment
        )
        
        # Recalculate total score
        mcq_total = assessment.mcq_questions.filter(
            scores__enrollment=instance.enrollment
        ).aggregate(total=models.Sum('scores__score'))['total'] or 0
        
        handwritten_total = assessment.handwritten_questions.filter(
            scores__enrollment=instance.enrollment
        ).aggregate(total=models.Sum('scores__score'))['total'] or 0
        
        assessment_score.total_score = mcq_total + handwritten_total
        assessment_score.save()
    except AssessmentScore.DoesNotExist:
        pass
