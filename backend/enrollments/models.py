import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from courses.models import Course
from django.db.models import Sum, Count


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
        result = AssessmentScore.objects.filter(
            enrollment=self
        ).aggregate(
            total=Sum('total_score'),
            count=Count('id')
        )
        
        if result['count'] == 0:
            return 0
            
        return round(result['total'] / result['count'], 2)