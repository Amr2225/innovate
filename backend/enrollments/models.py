import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from courses.models import Course
from django.db.models import Sum, Count
from decimal import Decimal


class Enrollments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    total_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"

    def update_total_score(self):
        """
        Updates the total score from all assessment scores for this enrollment.
        Calculates the average score across all assessments and saves it to the database.
        """
        from assessment.models import AssessmentScore
        
        # Get all assessment scores for this enrollment
        scores = AssessmentScore.objects.filter(enrollment=self)
        
        # If no scores exist, set total_score to 0
        if not scores.exists():
            self.total_score = Decimal('0.00')
            self.save()
            return
        
        # Calculate total and count
        result = scores.aggregate(
            total=Sum('total_score'),
            count=Count('id')
        )
        
        # Ensure we have valid numbers
        total = result['total'] or Decimal('0.00')
        count = result['count'] or 1
        
        # Calculate average and round to 2 decimal places
        self.total_score = (total / count).quantize(Decimal('0.01'))
        self.save()