from rest_framework import serializers
from .models import MCQQuestionScore
from courses.serializers import CourseSerializer

class MCQQuestionScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='student.email')
    student_name = serializers.SerializerMethodField()
    question_text = serializers.ReadOnlyField(source='question.question')
    assessment_title = serializers.ReadOnlyField(source='question.assessment.title')
    course_details = serializers.SerializerMethodField()
    total_attempts = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestionScore
        fields = (
            'id', 'question', 'student', 'student_email', 'student_name',
            'selected_answer', 'is_correct', 'score',
            'created_at', 'updated_at', 'question_text', 'assessment_title',
            'course', 'course_details', 'total_attempts'
        )
        read_only_fields = (
            'is_correct', 'score', 'created_at', 'updated_at',
            'student_email', 'student_name', 'question_text',
            'assessment_title', 'course_details', 'total_attempts', 'student'
        )
        extra_kwargs = {
            'course': {'required': False},  # Will be set automatically
            'student': {'required': False}  # Will be set from request
        }

    def get_student_name(self, obj):
        if hasattr(obj, 'student'):
            return f"{obj.student.first_name} {obj.student.last_name}"
        return None

    def get_total_attempts(self, obj):
        if hasattr(obj, 'question') and hasattr(obj, 'student'):
            return MCQQuestionScore.objects.filter(
                question=obj.question,
                student=obj.student
            ).count()
        return 0

    def get_course_details(self, obj):
        if hasattr(obj, 'course') and obj.course:
            return CourseSerializer(obj.course, context=self.context).data
        return None

    def validate(self, data):
        # Ensure selected_answer is one of the question options
        if 'selected_answer' in data and 'question' in data:
            if data['selected_answer'] not in data['question'].answer:
                raise serializers.ValidationError(
                    "Selected answer must be one of the provided options"
                )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and request.user.role == 'Student':
            return {
                'message': 'student submits his answer successfully'
            }
        
        # For teachers and institutions
        data = super().to_representation(instance)
        if request and request.user.role in ['Teacher', 'Institution']:
            data.update({
                'student_details': {
                    'id': str(instance.student.id),
                    'email': instance.student.email,
                    'name': self.get_student_name(instance)
                },
                'assessment_details': {
                    'id': str(instance.question.assessment.id),
                    'title': instance.question.assessment.title,
                    'due_date': instance.question.assessment.due_date
                },
                'question_details': {
                    'options': instance.question.answer,
                    'correct_answer': instance.question.answer_key
                }
            })
        return data 