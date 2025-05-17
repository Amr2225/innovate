import uuid
from django.db import models
from assessment.models import Assessment
from users.models import User
from enrollments.models import Enrollments
from django.conf import settings
import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.validators import MinValueValidator, MaxValueValidator, FileExtensionValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

def get_handwritten_answer_path(instance, filename):
    logger = logging.getLogger(__name__)
    
    try:
        # Get the assessment ID from the question
        assessment_id = instance.question.assessment.id
        logger.info(f"Processing image upload for assessment: {assessment_id}")
        logger.info(f"Original filename: {filename}")
        
        # Ensure filename has correct extension
        ext = filename.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
            logger.error(f"Invalid file extension: {ext}")
            raise ValidationError(f"Invalid file extension: {ext}. Allowed extensions: jpg, jpeg, png, gif, bmp")
        
        # Create a unique filename
        unique_filename = f"{uuid.uuid4()}.{ext}"
        logger.info(f"Generated unique filename: {unique_filename}")
        
        # Create path: AssessmentUploads/assessment_id/filename
        path = os.path.join(settings.ASSESSMENT_UPLOADS_DIR, str(assessment_id), unique_filename)
        logger.info(f"Final upload path: {path}")
        
        return path
    except Exception as e:
        logger.error(f"Error in get_handwritten_answer_path: {str(e)}")
        raise ValidationError(f"Error processing image upload: {str(e)}")

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
    answer_image = models.ImageField(
        upload_to=get_handwritten_answer_path,
        null=True,
        blank=True,
        help_text="Upload a JPEG, PNG, GIF, or BMP image file (max 5MB)",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'bmp'])
        ]
    )
    extracted_text = models.TextField(
        blank=True, 
        null=True,
        help_text="Text extracted from the handwritten answer image"
    )
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
        
        # Clean and validate
        self.clean()
        
        # Create the upload directory if it doesn't exist
        if self.answer_image:
            upload_path = os.path.join(
                settings.MEDIA_ROOT,
                settings.ASSESSMENT_UPLOADS_DIR,
                str(self.question.assessment.id)
            )
            os.makedirs(upload_path, exist_ok=True)
        
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

    def clean(self):
        if self.answer_image:
            # Validate image file
            try:
                from PIL import Image
                image = Image.open(self.answer_image)
                if image.format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
                    raise ValidationError("Unsupported image format. Please upload a JPEG, PNG, GIF, or BMP file")
            except Exception as e:
                raise ValidationError(f"Invalid image file: {str(e)}")

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
