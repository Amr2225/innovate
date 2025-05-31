import uuid
from django.db import models
from assessment.models import Assessment
from users.models import User

class CodingQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    assessment_Id = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    function_signature = models.CharField(max_length=255)
    language_id = models.IntegerField(default=71)  # 71 = Python 3

    def __str__(self):
        return self.title

class TestCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return f"Test case for {self.question.title}"

class CodingQuestionScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE)
    student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    section_number = models.PositiveSmallIntegerField(null=False, blank=False, help_text="Section number within the assessment")