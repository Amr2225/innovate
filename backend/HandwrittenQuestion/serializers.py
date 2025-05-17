from rest_framework import serializers
from .models import HandwrittenQuestion, HandwrittenQuestionScore
from assessment.serializers import AssessmentSerializer
from enrollments.serializers import EnrollmentsSerializer
from decimal import Decimal
import logging
import uuid
import io

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
    answer_image = serializers.ImageField(
        required=True,
        allow_null=False,
        error_messages={
            'required': 'Please upload an image file',
            'invalid_image': 'The uploaded file is not a valid image. Please upload a JPEG, PNG, GIF, or BMP file.',
            'invalid': 'Invalid image file. Please ensure the file is not corrupted.'
        }
    )

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
            'assessment_title', 'course_details'
        )

    def get_student_name(self, obj):
        return f"{obj.enrollment.user.first_name} {obj.enrollment.user.last_name}"

    def get_course_details(self, obj):
        course = obj.question.assessment.course
        return {
            'id': str(course.id),
            'title': course.title,
            'code': course.code
        }

    def get_answer_image_url(self, obj):
        if obj.answer_image:
            return self.context['request'].build_absolute_uri(obj.answer_image.url)
        return None

    def validate_answer_image(self, value):
        """
        Process and validate the uploaded image
        """
        from PIL import Image
        import io

        try:
            # Check file extension
            ext = value.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                raise serializers.ValidationError(
                    f"Invalid file extension: {ext}. Allowed extensions: jpg, jpeg, png, gif, bmp"
                )
            
            # Check file size (5MB max)
            if value.size > 5 * 1024 * 1024:  # 5MB in bytes
                raise serializers.ValidationError(
                    f"File too large. Maximum size is 5MB. Your file is {value.size / (1024 * 1024):.2f}MB"
                )
            
            # Open and validate image
            image = Image.open(value)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a new file-like object
            output = io.BytesIO()
            
            # Save as JPEG with good quality
            image.save(output, format='JPEG', quality=95)
            output.seek(0)
            
            # Create a new file with the processed image
            from django.core.files.base import ContentFile
            value = ContentFile(output.getvalue(), name=f"{uuid.uuid4()}.jpg")
            
            # Reset file pointer
            value.seek(0)
            
            return value
            
        except (IOError, OSError) as e:
            raise serializers.ValidationError("Invalid or corrupted image file. Please upload a valid image file")
        except Exception as e:
            raise serializers.ValidationError(f"Error processing image: {str(e)}")

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

