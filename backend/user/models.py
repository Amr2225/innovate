from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _


class User(AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'

    username = models.TextField(max_length=255, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=12)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    role = models.CharField(
        max_length=10, choices=RoleChoices.choices, default=RoleChoices.STUDENT)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'


def __str__(self):
    return f"{self.username} ({self.role})"
