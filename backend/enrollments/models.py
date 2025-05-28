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

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"

    @property
    def total_score(self):
        """
        Calculates the total score from all assessment scores for this enrollment.
        Returns the average score across all assessments.
        """
        from assessment.models import AssessmentScore
        
        # Get all assessment scores for this enrollment
        scores = AssessmentScore.objects.filter(enrollment=self)
        
        # If no scores exist, return 0
        if not scores.exists():
            return Decimal('0.00')
        
        # Calculate total and count
        result = scores.aggregate(
            total=Sum('total_score'),
            count=Count('id')
        )
        
        # Ensure we have valid numbers
        total = result['total'] or Decimal('0.00')
        count = result['count'] or 1
        
        # Calculate average and round to 2 decimal places
        average = (total / count).quantize(Decimal('0.01'))
        return average