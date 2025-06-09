import uuid
from django.db import models
from assessment.models import Assessment
from users.models import User
from enrollments.models import Enrollments

class CodingQuestion(models.Model):
    LANGUAGE_CHOICES = [
        (71, 'Python'),
        (62, 'Java'),
        (50, 'C'),
        (54, 'C++'),
        (51, 'C#'),
        (63, 'JavaScript'),
        (74, 'TypeScript'),
        (68, 'PHP'),
    ]
    DIFFICULTY_CHOICES = [
        ('1', 'Very Easy'),
        ('2', 'Easy'),
        ('3', 'Medium'),
        ('4', 'Hard'),
        ('5', 'Very Hard')
    ]
    
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    assessment_Id = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    function_signature = models.CharField(max_length=255)
    language_id = models.IntegerField(choices=LANGUAGE_CHOICES, default=71)  # 71 = Python 3
    difficulty = models.CharField(max_length=1, choices=DIFFICULTY_CHOICES, default='3')
    max_grade = models.IntegerField(default=5)

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
    # student_id = models.ForeignKey(User, on_delete=models.CASCADE)
    enrollment_id = models.ForeignKey(Enrollments, on_delete=models.CASCADE)
    questionScore = models.IntegerField(default=5)
    score = models.IntegerField()
    
    
    def __str__(self):
        return f"Coding Question {self.question} score {self.score}"