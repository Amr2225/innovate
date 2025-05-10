# serializers.py
from rest_framework import serializers
from .models import CodingQuestion, TestCase

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = (
            'id',
            'input_data',
            'expected_output',
            'is_public',
            'question'
        )
        
        read_only_fields = ('question',)
        
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['Teacher'] = request.user
        return super().create(validated_data)

class CodingQuestionSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True)
    class Meta:
        model = CodingQuestion
        fields = (
            'id',
            'assessment_Id',
            'created_date',
            'title',
            'description',
            'function_signature',
            'language_id',
            'test_cases'
        )
        
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['Teacher'] = request.user
        return super().create(validated_data)
