from rest_framework import serializers
from .models import MCQQuestionScore

class MCQQuestionScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='student.email')
    question_text = serializers.ReadOnlyField(source='question.question')
    assessment_title = serializers.ReadOnlyField(source='question.assessment.title')

    class Meta:
        model = MCQQuestionScore
        fields = ('id', 'question', 'student', 'student_email', 'selected_answer', 
                 'is_correct', 'score', 'created_at', 'question_text', 'assessment_title')
        read_only_fields = ('is_correct', 'score', 'created_at', 'student_email', 
                          'question_text', 'assessment_title') 