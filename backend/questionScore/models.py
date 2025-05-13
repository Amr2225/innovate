import uuid
from django.db import models
from users.models import User
from mcqQuestion.models import McqQuestion

class QuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(McqQuestion, on_delete=models.CASCADE, related_name='question_scores')  # Question_ID
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_scores', limit_choices_to={"role": "Student"})  # Student_ID
    student_answer = models.CharField(max_length=255)  # Student's answer to the question
    score = models.PositiveSmallIntegerField()  # Score in Question
    feedback = models.TextField(blank=True, null=True)  # Feedback
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['question', 'student']  # A student can only have one score per question

    def __str__(self):
        return f"{self.score}"