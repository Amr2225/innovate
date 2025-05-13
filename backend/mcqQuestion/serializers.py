from rest_framework import serializers
from .models import McqQuestion

class McqQuestionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = McqQuestion
        fields = ('id', 'assessment', 'question', 'answer', 'answer_key', 'created_by')
