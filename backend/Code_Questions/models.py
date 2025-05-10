# models.py
import uuid
from django.db import models

class CodingQuestion(models.Model):
    questionId = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=255)
    description = models.TextField()
    function_signature = models.CharField(max_length=255)
    language_id = models.IntegerField(default=71)  # 71 = Python 3

    def __str__(self):
        return self.title

class TestCase(models.Model):
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Test case for {self.question.title}"
