from django.db import models
from nanoid_field import NanoidField
from django.contrib.auth.hashers import make_password
import uuid

# Create your models here.


class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False,
                            null=False, unique=True)
    credits = models.PositiveIntegerField(blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.CharField(max_length=255)
    logo = models.ImageField(
        upload_to='uploads/institution/logo', null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.credits}"

    def save(self, **fields):
        self.password = make_password(self.password)
        return super().save(**fields)
