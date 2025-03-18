import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from user.models import User
from institution.models import Institution


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught',
        limit_choices_to={'is_teacher': True},
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.CASCADE, related_name='courses', default="1")

    def __str__(self):
        return self.name
