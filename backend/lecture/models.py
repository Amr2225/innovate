import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from chapter.models import Chapter


class Lecture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    video = models.FileField(upload_to='lectures/videos/', blank=True, null=True)
    attachment = models.FileField(upload_to='lectures/attachments/', blank=True, null=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lectures')

    def __str__(self):
        return self.title


class LectureProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    enrollment = models.ForeignKey('enrollments.Enrollments', on_delete=models.CASCADE)
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    time_spent = models.FloatField(null=True, blank=True)  # in minutes

    class Meta:
        unique_together = ('enrollment', 'lecture')

    def __str__(self):
        return f'{self.enrollment.user.username} - {self.lecture.title} - Completed: {self.completed}'