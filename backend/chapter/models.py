import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class Chapter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='chapters')

    class Meta:
        unique_together = ('title', 'course')

    def __str__(self):
        return self.title