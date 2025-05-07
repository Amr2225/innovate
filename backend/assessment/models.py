import uuid
from django.db import models
from users.models import User
from courses.models import Course

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    institution = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('Exam', 'Exam'), ('Assignment', 'Assignment'), ('Quiz', 'Quiz')])
    due_date = models.DateTimeField()
    grade = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.title
    
class AssessmentScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submit_date = models.DateTimeField()
    score = models.PositiveSmallIntegerField()
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='assessment')
    def __str__(self):
        return f"{self.score}"

