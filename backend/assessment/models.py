import uuid
from django.db import models
from users.models import User
from courses.models import Course
from django.db.models import Sum

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    institution = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assessments', limit_choices_to={"role": "Teacher"})
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('Exam', 'Exam'), ('Assignment', 'Assignment'), ('Quiz', 'Quiz')])
    due_date = models.DateTimeField()
    grade = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.title

class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    max_score = models.PositiveSmallIntegerField()
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.assessment.title} - Question {self.order}"

class QuestionResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='responses')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_responses', limit_choices_to={"role": "Student"})
    answer = models.TextField()
    score = models.PositiveSmallIntegerField()
    feedback = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['question', 'student']

    def __str__(self):
        return f"{self.student.email} - {self.question.assessment.title} - Q{self.question.order}"
    
class AssessmentScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submit_date = models.DateTimeField(auto_now=True)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assessment_scores", limit_choices_to={"role":"Student"})

    class Meta:
        unique_together = ['assessment', 'student']

    @property
    def score(self):
        total_score = self.student.question_responses.filter(
            question__assessment=self.assessment
        ).aggregate(total=Sum('score'))['total']
        return total_score or 0

    def __str__(self):
        return f"{self.student.email} - {self.assessment.title}: {self.score}"

