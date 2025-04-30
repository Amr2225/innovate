import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from lecture.models import Lecture, LectureProgress


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prerequisite_course = models.ForeignKey(
    'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='dependent_courses')
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught')
    institution = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses', limit_choices_to={"role": "Institution"})
    
    # Faculty fields
    credit_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    semester = models.PositiveSmallIntegerField(null=True, blank=True)

    # School fields
    level = models.PositiveSmallIntegerField(null=True, blank=True)


    def get_user_course_progress(self, user):
        lectures = Lecture.objects.filter(chapter__course=self)
        
        completed_lectures = LectureProgress.objects.filter(user=user, lecture__in=lectures, completed=True).count()
        total_lectures = lectures.count()
        if total_lectures > 0:
            progress = (completed_lectures / total_lectures) * 100
        else:
            progress = 0
        
        return progress

    def __str__(self):
        return self.name


# TODO: add another table for instructor courses (many-to-many) because many instuctors can be in the same course and vice-versa
