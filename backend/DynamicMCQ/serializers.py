from rest_framework import serializers
from .models import DynamicMCQ, DynamicMCQQuestions
from assessment.serializers import AssessmentSerializer


class DynamicMCQSerializer(serializers.ModelSerializer):
    assessment_details = AssessmentSerializer(
        source='assessment', read_only=True)

    class Meta:
        model = DynamicMCQ
        fields = [
            'id',
            'assessment',
            'assessment_details',
            'section_number',
            'context',
            'lecture_ids',
            'difficulty',
            'num_options',
            'total_grade',
            'number_of_questions',
        ]
        read_only_fields = ['id', 'assessment_details', 'assessment']

    def validate(self, data):
        # Validate that either context or lecture_ids is provided
        if not data.get('context') and not data.get('lecture_ids'):
            raise serializers.ValidationError(
                "Either context or lecture_ids must be provided")
        
        # Validate num_options
        num_options = data.get('num_options', 4)  # Default to 4 if not provided
        if num_options < 2 or num_options > 6:
            raise serializers.ValidationError(
                "Number of options must be between 2 and 6")
        
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
            'question_grade',
            # 'created_by'
        ]
        read_only_fields = ['id', 'created_by']

    def validate(self, data):
        # Validate that answer_key is one of the options
        if data.get('answer_key') not in data.get('options', []):
            raise serializers.ValidationError(
                "Answer key must be one of the provided options")
        return data
