import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught', limit_choices_to={"role": "Teacher"})
    institution = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses', limit_choices_to={"role": "Institution"})

    def __str__(self):
        return self.name


# TODO: add another table for instructor courses (many-to-many) because many instuctors can be in the same course and vice-versa
