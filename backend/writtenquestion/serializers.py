from rest_framework import serializers
from .models import HandwrittenQuestion, WrittenQuestion
from django.contrib.auth.models import User

class HandwrittenQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandwrittenQuestion
        fields = ['id', 'assessment', 'question', 'answer', 'answer_key', 'image']

class WrittenQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = WrittenQuestion
        fields = ['id', 'question_id', 'user_id', 'student_answer', 'score', 'feedback']
        read_only_fields = ['score', 'feedback']  # These are AI generated