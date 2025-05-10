from django.db import models
from assessment.models import Assessment
from users.models import User
import uuid

class McqQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='mcq_questions')
    question = models.CharField(max_length=1000)
    answer = models.JSONField()
    answer_key = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='mcq_questions_created')

    def __str__(self):
        return f"{self.assessment.title} - {self.question}"
