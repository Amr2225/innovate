from rest_framework import serializers
from .models import Assessment, AssessmentScore
from courses.models import Course
from users.models import User
from django.utils import timezone

class AssessmentSerializer(serializers.ModelSerializer):
    accepting_submissions = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'type',
            'due_date',
            'grade',
            'course',
            'accepting_submissions',
        )


class AssessmentScoreSerializer(serializers.ModelSerializer):
    submit_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = AssessmentScore
        fields = ['id', 'submit_date', 'score', 'assessment', 'user']
        read_only_fields = ['id', 'user']
