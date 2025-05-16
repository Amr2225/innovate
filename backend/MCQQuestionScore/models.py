from django.db import models
from mcqQuestion.models import McqQuestion
from users.models import User
import uuid

class MCQQuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(McqQuestion, on_delete=models.CASCADE, related_name='mcq_scores')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mcq_scores', limit_choices_to={"role": "Student"})
    selected_answer = models.CharField(max_length=1000)
    is_correct = models.BooleanField(default=False)
    score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['question', 'student']
        ordering = ['created_at']

    def __str__(self):
        return f"{self.student.email} - {self.question.question} - {'Correct' if self.is_correct else 'Incorrect'}"

    def save(self, *args, **kwargs):
        # Check if the answer is correct and calculate score
        if self.selected_answer == self.question.answer_key:
            self.is_correct = True
            self.score = self.question.question_grade
        else:
            self.is_correct = False
            self.score = 0
        super().save(*args, **kwargs)
