from django.db import models
from assessment.models import Assessment
from users.models import User
import uuid

class McqQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='mcq_questions')
    question = models.CharField(max_length=1000)
    options = models.JSONField(help_text="List of possible answers")
    answer_key = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mcq_questions_created')
    question_grade = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    section_number = models.PositiveSmallIntegerField(null=False, blank=False, help_text="Section number within the assessment")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assessment']),
            models.Index(fields=['created_by']),
        ]

    def __str__(self):
        return f"{self.assessment.title} - {self.question}"

    def save(self, *args, **kwargs):
        # Validate that question grade doesn't exceed assessment grade
        self.assessment.validate_question_grade(
            new_question_grade=self.question_grade,
            existing_question_id=self.id if self.pk else None
        )
        super().save(*args, **kwargs)
