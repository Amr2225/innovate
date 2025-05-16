import uuid
from django.db import models
from users.models import User
from courses.models import Course
from django.utils import timezone
from django.db.models import Sum

class Assessment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=[('Exam', 'Exam'), ('Assignment', 'Assignment'), ('Quiz', 'Quiz')])
    due_date = models.DateTimeField()
    grade = models.PositiveSmallIntegerField()
    start_date = models.DateTimeField(default=timezone.now)
    accepting_submissions = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def is_active(self):
        """
        Returns True if the assessment is currently active (between start and due date)
        """
        now = timezone.now()
        return self.start_date <= now <= self.due_date

    def get_student_score(self, student):
        """
        Calculate total score for a student based on their MCQQuestionScores
        """
        from MCQQuestionScore.models import MCQQuestionScore
        return MCQQuestionScore.objects.filter(
            question__assessment=self,
            student=student
        ).aggregate(total=Sum('score'))['total'] or 0
    
class AssessmentScore(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assessment_scores')
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='scores')
    total_score = models.DecimalField(max_digits=5, decimal_places=2)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'assessment')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.email} - {self.assessment.title} - {self.total_score}"

    def save(self, *args, **kwargs):
        # Calculate total score from MCQQuestionScores
        self.total_score = self.assessment.get_student_score(self.student)
        super().save(*args, **kwargs)

