from rest_framework import serializers
from .models import DynamicMCQ, DynamicMCQQuestions
from assessment.serializers import AssessmentSerializer

class DynamicMCQSerializer(serializers.ModelSerializer):
    assessment_details = AssessmentSerializer(source='assessment', read_only=True)

    class Meta:
        model = DynamicMCQ
        fields = [
            'id',
            'assessment',
            'assessment_details',
            'section_number',
            'context',
            'attachments',
            'difficulty',
            'total_grade',
            'number_of_questions'
        ]
        read_only_fields = ['id', 'assessment_details']

    def validate(self, data):
        # Validate that either context or attachments is provided
        if not data.get('context') and not data.get('attachments'):
            raise serializers.ValidationError("Either context or attachments must be provided")
        return data

class DynamicMCQQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicMCQQuestions
        fields = [
            'id',
            'dynamic_mcq',
            'question',
            'options',
            'answer_key',
            'question_grade'
        ]
        read_only_fields = ['id']

    def validate(self, data):
        # Validate that answer_key is one of the options
        if data.get('answer_key') not in data.get('options', []):
            raise serializers.ValidationError("Answer key must be one of the provided options")
        return data 