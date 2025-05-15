import uuid # Ensure this is at the top if not already present
from django.db import models
# Make sure to import the Assessment model from its app, e.g.:
# from assessment.models import Assessment # Adjust 'assessment.models' to the correct path
from assessment.models import Assessment
from django.contrib.auth.models import User

class HandwrittenQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='handwritten_questions') # Ensure 'Assessment' is correctly imported
    question = models.CharField( max_length=50)
    answer = models.TextField(blank=True, null=True)  # Student's answer
    answer_key = models.CharField( max_length=50)
    image = models.ImageField(upload_to='handwritten_questions_images/', blank=True, null=True)

    def __str__(self):
        # Check if assessment is loaded to prevent errors if it's a deferred field or not yet saved
        assessment_title = self.assessment.title if self.assessment_id else "N/A"
        return f"Handwritten Question for {assessment_title}: {self.question[:50]}..."

class WrittenQuestion(models.Model):
    question_id = models.ForeignKey('HandwrittenQuestion', on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    student_answer = models.TextField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)  # AI generated
    feedback = models.TextField(blank=True, null=True)  # AI generated
