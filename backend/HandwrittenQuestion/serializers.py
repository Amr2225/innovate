from rest_framework import serializers
from .models import HandwrittenQuestion, HandwrittenQuestionScore
from assessment.serializers import AssessmentSerializer
from enrollments.serializers import EnrollmentsSerializer
from decimal import Decimal

class HandwrittenQuestionSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.email')
    max_grade = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=Decimal('0.00'))
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = HandwrittenQuestion
        fields = (
            'id', 'assessment', 'question_text', 
            'answer_key', 'created_by', 'max_grade',
            'created_at', 'updated_at'
        )
        read_only_fields = ('created_at', 'updated_at')
        extra_kwargs = {
            'answer_key': {'write_only': True}  # Hide answer key from students
        }

    def validate_max_grade(self, value):
        if value <= 0:
            raise serializers.ValidationError("Maximum grade must be greater than 0")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.role == 'Student':
            data.pop('answer_key', None)
        return data

class HandwrittenQuestionScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='enrollment.user.email')
    student_name = serializers.SerializerMethodField()
    question_text = serializers.ReadOnlyField(source='question.question_text')
    assessment_title = serializers.ReadOnlyField(source='question.assessment.title')
    course_details = serializers.SerializerMethodField()
    answer_image_url = serializers.SerializerMethodField()

    class Meta:
        model = HandwrittenQuestionScore
        fields = (
            'id', 'question', 'enrollment', 'student_email', 'student_name',
            'score', 'feedback', 'answer_image', 'answer_image_url',
            'extracted_text', 'submitted_at', 'evaluated_at',
            'question_text', 'assessment_title', 'course_details'
        )
        read_only_fields = (
            'score', 'feedback', 'extracted_text', 'submitted_at', 'evaluated_at',
            'student_email', 'student_name', 'question_text',
            'assessment_title', 'course_details', 'enrollment'
        )
        extra_kwargs = {
            'enrollment': {'required': False}  # Will be set from request
        }

    def get_student_name(self, obj):
        if hasattr(obj, 'enrollment') and hasattr(obj.enrollment, 'user'):
            return f"{obj.enrollment.user.first_name} {obj.enrollment.user.last_name}"
        return None

    def get_course_details(self, obj):
        if hasattr(obj, 'question') and hasattr(obj.question, 'assessment'):
            return {
                'id': str(obj.question.assessment.course.id),
                'name': obj.question.assessment.course.name
            }
        return None

    def get_answer_image_url(self, obj):
        if obj.answer_image:
            return self.context['request'].build_absolute_uri(obj.answer_image.url)
        return None

    def validate(self, data):
        request = self.context.get('request')
        if request and request.user.role == 'Student':
            # Ensure student can only submit for their own enrollment
            enrollment = data.get('enrollment')
            if enrollment and enrollment.user != request.user:
                raise serializers.ValidationError(
                    "You can only submit answers for your own enrollment"
                )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        if request and request.user.role == 'Student':
            return {
                'message': 'Answer submitted successfully'
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
                    'answer_key': instance.question.answer_key
                }
            })
        return data

