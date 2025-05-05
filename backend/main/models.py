from django.db import models
from django.core.exceptions import ValidationError

class User(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    # Additional fields...

class Assessment(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    # Additional fields...

class AssessmentScore(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    assessmentId = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    submit_date = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()

    class Meta:
        unique_together = ('userId', 'assessmentId')

    def clean(self):
        if self.score < 0 or self.score > 100:
            raise ValidationError("Score must be between 0 and 100.")

    def __str__(self):
        return f"{self.userId} - {self.assessmentId} - {self.score}"
