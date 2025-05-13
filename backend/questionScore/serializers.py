from rest_framework import serializers
from .models import QuestionScore

class QuestionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionScore
        fields = [
            'id',
            'question',
            'student',
            'score',
            'feedback',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 