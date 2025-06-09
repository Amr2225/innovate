from rest_framework import serializers
from .models import CodingQuestion, TestCase, CodingQuestionScore

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
        
        read_only_fields = ('question', 'id')
        
    # def create(self, validated_data):
        # request = self.context.get('request')
        # validated_data['Teacher'] = request.user
        # return super().create(validated_data)

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
        read_only_fields = ('id',)
    # def create(self, validated_data):
        # request = self.context.get('request', 'created_date')
        # validated_data['Teacher'] = request.user
        # return super().create(validated_data)

class CodingQuestionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingQuestionScore
        fields = (
            'id',
            'question',
            'enrollment_id',
            'questionScore',
            'score'
        )
        read_only_fields = ('id',)

class GenerateCodingQuestionsSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()
    assessment_id = serializers.UUIDField()
    num_questions = serializers.IntegerField(default=5)
    difficulty = serializers.IntegerField(default=3)
    language_id = serializers.IntegerField(default=71)

class GenerateCodingQuestionsContextSerializer(serializers.Serializer):
    context = serializers.CharField()
    assessment_id = serializers.UUIDField()
    num_questions = serializers.IntegerField(default=5)
    difficulty = serializers.IntegerField(default=3)
    language_id = serializers.IntegerField(default=71)
