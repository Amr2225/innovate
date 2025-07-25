from rest_framework import serializers

from assessment.errors import AssessmentInvalidDueDate
from .models import Assessment, AssessmentScore
from courses.models import Course
from users.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from AssessmentSubmission.models import AssessmentSubmission
from enrollments.models import Enrollments


class AssessmentListSerializer(serializers.ModelSerializer):
    has_submitted = serializers.SerializerMethodField()
    course = serializers.CharField(source='course.name', read_only=True)
    course_description = serializers.CharField(
        source='course.description', read_only=True)
    courseId = serializers.UUIDField(source='course.id', read_only=True)
    # enrollment_id = serializers.UUIDField(
    #     source='enrollment.id', read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'type', 'start_date',
                  'due_date', 'accepting_submissions', 'has_submitted', 'course', 'course_description', "grade", "courseId"]
        read_only_fields = ['id', "grade"]

    def get_has_submitted(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        try:
            # Get the enrollment for the current user and assessment's course
            enrollment = Enrollments.objects.get(
                user=request.user,
                course=obj.course,
                is_completed=False
            )

            # Check if there's a submission for this assessment and enrollment
            submission = AssessmentSubmission.objects.filter(
                assessment=obj,
                enrollment=enrollment
            ).first()

            return submission.is_submitted if submission else False

        except Enrollments.DoesNotExist:
            return False


class AssessmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    accepting_submissions = serializers.BooleanField(read_only=True)
    start_date = serializers.DateTimeField(default=timezone.now)

    class Meta:
        model = Assessment
        fields = ('id', 'course', 'course_name', 'title', 'type', 'due_date', 'grade',
                  'start_date', 'accepting_submissions')
        read_only_fields = ('id', 'course_name',

                            'accepting_submissions', 'grade')

    def to_internal_value(self, data):
        # If start_date is explicitly set to null, use the default value
        if 'start_date' in data and data['start_date'] is None:
            data['start_date'] = timezone.now()
        return super().to_internal_value(data)

    def validate(self, data):
        # Check if due date is in the future
        if data.get('due_date') and data['due_date'] < timezone.now():
            raise AssessmentInvalidDueDate()
        return data


class AssessmentScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='enrollment.user.email')
    assessment_title = serializers.ReadOnlyField(source='assessment.title')
    course_name = serializers.ReadOnlyField(source='assessment.course.name')

    class Meta:
        model = AssessmentScore
        fields = ('id', 'assessment', 'enrollment', 'student_email',
                  'assessment_title', 'course_name', 'total_score',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'student_email', 'assessment_title',
                            'course_name', 'total_score', 'created_at', 'updated_at')
