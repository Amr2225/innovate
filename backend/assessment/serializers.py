from rest_framework import serializers
from .models import Assessment, AssessmentScore
from courses.models import Course
from users.models import User
from django.utils import timezone

class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'type',
            'due_date',
            'grade',
            'course',
            'institution',
        )
        read_only_fields = ('institution',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['institution'] = request.user
        return super().create(validated_data)


class AssessmentScoreSerializer(serializers.ModelSerializer):
    submit_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = AssessmentScore
        fields = ['id', 'submit_date', 'score', 'assessment']
        read_only_fields = ['id']
