import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from courses.models import Course


class Enrollments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.course.name} Completed: {self.is_completed}"
