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
            'lecture_ids',
            'difficulty',
            'total_grade',
            'number_of_questions'
        ]
        read_only_fields = ['id', 'assessment_details', 'assessment']

    def validate(self, data):
        # Validate that either context or lecture_ids is provided
        if not data.get('context') and not data.get('lecture_ids'):
            raise serializers.ValidationError("Either context or lecture_ids must be provided")
        
        # Validate that number_of_questions is positive
        if data.get('number_of_questions', 0) <= 0:
            raise serializers.ValidationError("Number of questions must be positive")
            
        # Validate that total_grade is positive
        if data.get('total_grade', 0) <= 0:
            raise serializers.ValidationError("Total grade must be positive")
            
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
            'difficulty',
            'created_by'
        ]
        read_only_fields = ['id', 'created_by']

    def validate(self, data):
        # Validate that answer_key is one of the options
        if data.get('answer_key') not in data.get('options', []):
            raise serializers.ValidationError("Answer key must be one of the provided options")
            
        # Validate that question_grade is positive
        if data.get('question_grade', 0) <= 0:
            raise serializers.ValidationError("Question grade must be positive")
            
        return data 