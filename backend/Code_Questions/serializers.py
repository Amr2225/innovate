from rest_framework import serializers
from .models import CodingQuestion, TestCase, CodingQuestionScore, CodingScoreTestInteractions

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

class CodingScoreTestInteractionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodingScoreTestInteractions
        fields = ('id', 'questionScore', 'testCase', 'passed')
        read_only_fields = ('id',)

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
            'difficulty',
            'max_grade',
            'section_number',
            'test_cases'
        )
        read_only_fields = ('id', 'created_date',)
    # def create(self, validated_data):
        # request = self.context.get('request', 'created_date')
        # validated_data['Teacher'] = request.user
        # return super().create(validated_data)

class CodingQuestionScoreSerializer(serializers.ModelSerializer):
    test_interactions = CodingScoreTestInteractionsSerializer(many=True, read_only=True)
    class Meta:
        model = CodingQuestionScore
        fields = (
            'id',
            'question',
            'enrollment_id',
            # 'questionScore',
            'score',
            'test_interactions',
            'student_answer',
            'feedback'
        )
        read_only_fields = ('id',)
        

class GenerateCodingQuestionsSerializer(serializers.Serializer):
    pdf_file = serializers.FileField()
    assessment_id = serializers.UUIDField()
    num_questions = serializers.IntegerField(min_value=1, max_value=10, default=5)
    difficulty = serializers.ChoiceField(choices=CodingQuestion.DIFFICULTY_CHOICES, default='3')
    language_id = serializers.ChoiceField(choices=CodingQuestion.LANGUAGE_CHOICES, default='python3')

class GenerateCodingQuestionsContextSerializer(serializers.Serializer):
    assessment_id = serializers.UUIDField()
    num_questions = serializers.IntegerField(min_value=1, max_value=10, default=5)
    difficulty = serializers.ChoiceField(choices=CodingQuestion.DIFFICULTY_CHOICES, default='3')
    language_id = serializers.ChoiceField(choices=CodingQuestion.LANGUAGE_CHOICES, default='python3')
    context = serializers.CharField()
