from django.db import models
import uuid
from assessment.models import Assessment
from users.models import User

class DynamicMCQ(models.Model):
    DIFFICULTY_CHOICES = [
        ('1', 'Very Easy'),
        ('2', 'Easy'),
        ('3', 'Medium'),
        ('4', 'Hard'),
        ('5', 'Very Hard')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='dynamic_mcqs')
    section_number = models.PositiveSmallIntegerField(null=False, blank=False, help_text="Section number within the assessment")
    context = models.TextField(null=True, blank=True)
    lecture_ids = models.JSONField(default=list, help_text="Array of lecture UUIDs")
    difficulty = models.CharField(
        max_length=1,
        choices=DIFFICULTY_CHOICES,
        default='3'
    )
    num_options = models.PositiveSmallIntegerField(default=4, help_text="Number of options per question (2-6)")
    total_grade = models.PositiveSmallIntegerField()
    number_of_questions = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"Dynamic MCQ for {self.assessment.title} - Section {self.section_number}"

    class Meta:
        app_label = 'DynamicMCQ'
        verbose_name = "Dynamic MCQ"
        verbose_name_plural = "Dynamic MCQs"
        ordering = ['assessment__due_date', 'section_number']

    def clean(self):
        if self.num_options < 2 or self.num_options > 6:
            raise models.ValidationError("Number of options must be between 2 and 6")

class DynamicMCQQuestions(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dynamic_mcq = models.ForeignKey(DynamicMCQ, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    options = models.JSONField(help_text="List of options for the question")
    answer_key = models.CharField(max_length=255, help_text="The correct answer from the options")
    question_grade = models.PositiveSmallIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dynamic_mcq_questions')
    difficulty = models.CharField(
        max_length=1,
        choices=DynamicMCQ.DIFFICULTY_CHOICES,
        default='3'
    )

    def __str__(self):
        return f"Question for {self.dynamic_mcq}"

    class Meta:
        app_label = 'DynamicMCQ'
        verbose_name = "Dynamic MCQ Question"
        verbose_name_plural = "Dynamic MCQ Questions"
        ordering = ['dynamic_mcq', 'id']

    def clean(self):
        # Validate that answer_key is one of the options
        if self.answer_key not in self.options:
            raise models.ValidationError("Answer key must be one of the provided options")
