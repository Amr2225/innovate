from rest_framework import serializers
from .models import MCQQuestionScore
from courses.serializers import CourseSerializer

class MCQQuestionScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='enrollment.user.email')
    student_name = serializers.SerializerMethodField()
    question_text = serializers.ReadOnlyField(source='question.question')
    assessment_title = serializers.ReadOnlyField(source='question.assessment.title')
    course_details = serializers.SerializerMethodField()
    total_attempts = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestionScore
        fields = (
            'id', 'question', 'enrollment', 'student_email', 'student_name',
            'selected_answer', 'is_correct', 'score',
            'created_at', 'updated_at', 'question_text', 'assessment_title',
            'course_details', 'total_attempts'
        )
        read_only_fields = (
            'is_correct', 'score', 'created_at', 'updated_at',
            'student_email', 'student_name', 'question_text',
            'assessment_title', 'course_details', 'total_attempts', 'enrollment'
        )
        extra_kwargs = {
            'enrollment': {'required': False}  # Will be set from request
        }

    def get_student_name(self, obj):
        if hasattr(obj, 'enrollment') and hasattr(obj.enrollment, 'user'):
            return f"{obj.enrollment.user.first_name} {obj.enrollment.user.last_name}"
        return None

    def get_total_attempts(self, obj):
        if hasattr(obj, 'question') and hasattr(obj, 'enrollment'):
            return MCQQuestionScore.objects.filter(
                question=obj.question,
                enrollment=obj.enrollment
            ).count()
        return 0

    def get_course_details(self, obj):
        if hasattr(obj, 'question') and hasattr(obj.question, 'assessment'):
            return {
                'id': str(obj.question.assessment.course.id),
                'name': obj.question.assessment.course.name
            }
        return None

    def validate(self, data):
        # Ensure selected_answer is one of the question options
        if 'selected_answer' in data and 'question' in data:
            if data['selected_answer'] not in data['question'].options:
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
                    'id': str(instance.enrollment.user.id),
                    'email': instance.enrollment.user.email,
                    'name': self.get_student_name(instance)
                },
                'assessment_details': {
                    'id': str(instance.question.assessment.id),
                    'title': instance.question.assessment.title,
                    'due_date': instance.question.assessment.due_date
                },
                'question_details': {
                    'options': instance.question.options,
                    'correct_answer': instance.question.answer_key
                }
            })
        return data 