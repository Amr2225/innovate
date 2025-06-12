from rest_framework import serializers
from .models import CodingQuestion, TestCase, CodingQuestionScore

class GenerateCodingQuestionsSerializer(serializers.Serializer):
    lecture_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text="List of lecture IDs to generate questions from"
    )
    context = serializers.CharField(
        required=False,
        help_text="Context text to generate questions from"
    )
    assessment_id = serializers.UUIDField(
        required=True,
        help_text="ID of the assessment to add questions to"
    )
    grade = serializers.IntegerField(
        required=True,
        min_value=1,
        max_value=100,
        help_text="Grade for each question"
    )
    section_number = serializers.IntegerField(
        required=True,
        min_value=1,
        help_text="Section number in the assessment"
    )
    num_questions = serializers.IntegerField(
        required=False,
        default=3,
        min_value=1,
        max_value=10,
        help_text="Number of questions to generate"
    )

    def validate(self, data):
        if not data.get('lecture_ids') and not data.get('context'):
            raise serializers.ValidationError(
                "Either lecture_ids or context must be provided"
            )
        return data

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCase
        fields = ['id', 'input_data', 'expected_output', 'is_public']

class CodingQuestionSerializer(serializers.ModelSerializer):
    test_cases = TestCaseSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField()

    class Meta:
        model = CodingQuestion
        fields = [
            'id', 'title', 'description', 'function_signature',
            'language_id', 'max_grade', 'test_cases', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class CodingQuestionScoreSerializer(serializers.ModelSerializer):
    question = CodingQuestionSerializer(read_only=True)
    enrollment = serializers.StringRelatedField()

    class Meta:
        model = CodingQuestionScore
        fields = [
            'id', 'question', 'enrollment', 'score', 'feedback',
            'submitted_code', 'test_results', 'submitted_at',
            'evaluated_at'
        ]
        read_only_fields = [
            'score', 'feedback', 'test_results', 'submitted_at',
            'evaluated_at'
        ] 