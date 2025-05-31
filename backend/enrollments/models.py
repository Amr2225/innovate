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
        Updates the total score by summing up all assessment scores for this enrollment.
        """
        print(f"DEBUG: Starting enrollment update_total_score for enrollment {self.id}")
        print(f"DEBUG: Current total_score before update: {self.total_score}")
        
        from assessment.models import AssessmentScore
        
        # Get all assessment scores for this enrollment
        scores = AssessmentScore.objects.filter(enrollment=self)
        print(f"DEBUG: Found {scores.count()} assessment scores")
        
        # If no scores exist, set total_score to 0
        if not scores.exists():
            print("DEBUG: No assessment scores found, setting total to 0")
            self.total_score = Decimal('0.00')
            self.save()
            return
        
        # Calculate total of all scores
        total = scores.aggregate(total=Sum('total_score'))['total'] or Decimal('0.00')
        print(f"DEBUG: Calculated total from all assessment scores: {total}")
        
        # Set total score and round to 2 decimal places
        self.total_score = total.quantize(Decimal('0.01'))
        print(f"DEBUG: New total_score after calculation: {self.total_score}")
        
        # Save the changes
        self.save()
        print(f"DEBUG: Saved enrollment with new total_score: {self.total_score}")