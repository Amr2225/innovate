from django.db import models
from mcqQuestion.models import McqQuestion
from users.models import User
from courses.models import Course
from assessment.models import AssessmentScore
from enrollments.models import Enrollments
import uuid
import logging
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)

class MCQQuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    question = GenericForeignKey('content_type', 'object_id')
    enrollment = models.ForeignKey(Enrollments, on_delete=models.CASCADE, related_name='mcq_scores')
    selected_answer = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    question_type = models.CharField(max_length=20, choices=[('mcq', 'MCQ'), ('dynamic_mcq', 'Dynamic MCQ')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('content_type', 'object_id', 'enrollment')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['enrollment']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.enrollment.user.email} - {self.question.question} - {self.score}"

    def save(self, *args, **kwargs):
        # Calculate score based on whether the answer is correct
        if self.selected_answer == self.question.answer_key:
            self.is_correct = True
            self.score = self.question.question_grade
        else:
            self.is_correct = False
            self.score = 0

        # Save the MCQQuestionScore first
        super().save(*args, **kwargs)

        try:
            # Update or create AssessmentScore
            assessment = self.question.assessment if hasattr(self.question, 'assessment') else self.question.dynamic_mcq.assessment
            assessment_score, created = AssessmentScore.objects.get_or_create(
                enrollment=self.enrollment,
                assessment=assessment,
                defaults={'total_score': 0}
            )
            
            # Calculate total score including both MCQ and Handwritten scores
            mcq_total = float(assessment.mcq_questions.filter(
                scores__enrollment=self.enrollment
            ).aggregate(total=models.Sum('scores__score'))['total'] or 0)
            
            handwritten_total = float(assessment.handwritten_questions.filter(
                scores__enrollment=self.enrollment
            ).aggregate(total=models.Sum('scores__score'))['total'] or 0)
            
            # Calculate total possible score
            mcq_max = float(assessment.mcq_questions.aggregate(total=models.Sum('question_grade'))['total'] or 0)
            handwritten_max = float(assessment.handwritten_questions.aggregate(total=models.Sum('max_grade'))['total'] or 0)
            total_max = mcq_max + handwritten_max
            
            # Calculate percentage score
            if total_max > 0:
                percentage_score = ((mcq_total + handwritten_total) / total_max) * 100
            else:
                percentage_score = 0
                
            # Update assessment score
            assessment_score.total_score = mcq_total + handwritten_total
            assessment_score.percentage_score = percentage_score
            assessment_score.save()
            
            logger.info(f"Updated assessment score for enrollment {self.enrollment.id} and assessment {assessment.id}")
            logger.info(f"MCQ total: {mcq_total}, Handwritten total: {handwritten_total}")
            logger.info(f"Total score: {assessment_score.total_score}, Percentage: {percentage_score}%")
        except Exception as e:
            # Log the error but don't prevent the MCQQuestionScore from being saved
            logger.error(f"Error saving score: {str(e)}")
