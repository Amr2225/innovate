from django.db import models
from users.models import User
import uuid

# Create your models here.
class InstitutionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.OneToOneField(User, on_delete=models.CASCADE, related_name='policy', limit_choices_to={"role": "Institution"})
    min_passing_percentage = models.FloatField(default=50.0, null=True, blank=True)
    max_allowed_failures = models.IntegerField(default=2, null=True, blank=True)
    min_gpa_required = models.FloatField(null=True, blank=True)
    min_attendance_percent = models.FloatField(default=75.0, null=True, blank=True)
    max_allowed_courses_per_semester = models.IntegerField(default=6, null=True, blank=True)