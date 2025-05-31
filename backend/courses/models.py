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
    instructors = models.ManyToManyField(User, related_name='courses_taught', limit_choices_to={"role": "Teacher"})
    institution = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses', limit_choices_to={"role": "Institution"})
    semester = models.PositiveSmallIntegerField(null=True, blank=True)
    passing_grade = models.FloatField(default=50.0, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    # Faculty fields
    credit_hours = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # School fields
    total_grade = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['name', 'institution'], name='unique_course_per_institution')
        ]

    @property
    def level(self):
        if self.semester:
            return (self.semester + 1) // 2
        return None


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