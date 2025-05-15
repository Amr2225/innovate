from rest_framework import serializers
from .models import Assessment, AssessmentScore, Question, QuestionResponse
from courses.models import Course
from users.models import User
from django.utils import timezone
from django.db import models

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'max_score', 'order']

class QuestionResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionResponse
        fields = ['id', 'question', 'answer', 'score', 'feedback', 'submitted_at']
        read_only_fields = ['score', 'feedback']

class AssessmentSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Assessment
        fields = (
            'id',
            'title',
            'type',
            'due_date',
            'grade',
            'course',
            'institution',
            'questions'
        )
        read_only_fields = ('institution',)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['institution'] = request.user
        return super().create(validated_data)

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "middle_name", "last_name", "email"]

class DetailedQuestionResponseSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    
    class Meta:
        model = QuestionResponse
        fields = ['question', 'answer', 'score', 'feedback', 'submitted_at']

class AssessmentScoreSerializer(serializers.ModelSerializer):
    submit_date = serializers.DateTimeField(default=timezone.now)
    student = StudentSerializer(read_only=True)
    score = serializers.IntegerField(read_only=True)
    question_responses = serializers.SerializerMethodField()
    total_possible = serializers.SerializerMethodField()
    percentage = serializers.SerializerMethodField()

    class Meta:
        model = AssessmentScore
        fields = ['id', 'submit_date', 'score', 'assessment', 'student', 'question_responses', 'total_possible', 'percentage']
        read_only_fields = ['id', 'submit_date', 'score']

    def get_question_responses(self, obj):
        responses = QuestionResponse.objects.filter(
            student=obj.student,
            question__assessment=obj.assessment
        ).select_related('question')
        return DetailedQuestionResponseSerializer(responses, many=True).data

    def get_total_possible(self, obj):
        return obj.assessment.questions.aggregate(total=models.Sum('max_score'))['total'] or 0

    def get_percentage(self, obj):
        total_possible = self.get_total_possible(obj)
        if total_possible == 0:
            return 0
        return round((obj.score / total_possible) * 100, 2)
        