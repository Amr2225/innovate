from rest_framework import serializers
from .models import AssessmentSubmission
from django.core.exceptions import ValidationError

class AssessmentSubmissionSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='enrollment.user.email')
    assessment_title = serializers.ReadOnlyField(source='assessment.title')
    course_name = serializers.ReadOnlyField(source='assessment.course.name')

    class Meta:
        model = AssessmentSubmission
        fields = (
            'id', 'assessment', 'enrollment', 'student_email', 
            'assessment_title', 'course_name', 'mcq_answers', 
            'handwritten_answers', 'submitted_at', 'is_submitted'
        )
        read_only_fields = (
            'id', 'student_email', 'assessment_title', 
            'course_name', 'submitted_at'
        )

    def validate(self, data):
        # Ensure user is a student
        if self.context['request'].user.role != "Student":
            raise ValidationError("Only students can submit answers")

        # Check if assessment is still accepting submissions
        if not data['assessment'].accepting_submissions:
            raise ValidationError("This assessment is no longer accepting submissions")

        # Check if student is enrolled in the course
        if not data['enrollment'].user == self.context['request'].user:
            raise ValidationError("You can only submit for your own enrollment")

        # Validate MCQ answers
        for question_id, answer in data.get('mcq_answers', {}).items():
            try:
                question = data['assessment'].mcq_questions.get(id=question_id)
                if answer not in question.options:
                    raise ValidationError(f"Invalid answer for MCQ question {question_id}")
            except Exception as e:
                raise ValidationError(f"Invalid MCQ question ID: {question_id}")

        # Validate Handwritten answers
        for question_id, image_path in data.get('handwritten_answers', {}).items():
            try:
                question = data['assessment'].handwritten_questions.get(id=question_id)
                # Additional validation for image path can be added here
            except Exception as e:
                raise ValidationError(f"Invalid Handwritten question ID: {question_id}")

        return data 