from django.db import models
from mcqQuestion.models import McqQuestion
from users.models import User
from courses.models import Course
from assessment.models import AssessmentScore
import uuid

class MCQQuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(McqQuestion, on_delete=models.CASCADE, related_name='mcq_scores')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mcq_scores', limit_choices_to={"role": "Student"})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='mcq_scores')
    selected_answer = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['question', 'student']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['question', 'student']),
            models.Index(fields=['course']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.student.email} - {self.question.question} - {'Correct' if self.is_correct else 'Incorrect'}"

    def save(self, *args, **kwargs):
        # Set course from question's assessment
        if not self.course_id:
            self.course = self.question.assessment.course
            
        # Check if the answer is correct and calculate score
        if self.selected_answer == self.question.answer_key:
            self.is_correct = True
            self.score = self.question.question_grade
        else:
            self.is_correct = False
            self.score = 0

        # Save the MCQQuestionScore first
        super().save(*args, **kwargs)

        # Update or create AssessmentScore
        assessment = self.question.assessment
        assessment_score, created = AssessmentScore.objects.get_or_create(
            student=self.student,
            assessment=assessment,
            defaults={'total_score': 0}
        )
        
        # The AssessmentScore's save method will automatically calculate the total score
        assessment_score.save()
