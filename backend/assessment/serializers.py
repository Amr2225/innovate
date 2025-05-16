from rest_framework import serializers
from .models import Assessment, AssessmentScore
from courses.models import Course
from users.models import User
from django.utils import timezone

class AssessmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    accepting_submissions = serializers.BooleanField(read_only=True)

    class Meta:
        model = Assessment
        fields = ('id', 'course', 'course_title', 'title', 'type', 'due_date', 'grade', 
                 'start_date', 'accepting_submissions')
        read_only_fields = ('id', 'course_title', 'accepting_submissions')


class AssessmentScoreSerializer(serializers.ModelSerializer):
    student_email = serializers.ReadOnlyField(source='student.email')
    assessment_title = serializers.ReadOnlyField(source='assessment.title')
    course_title = serializers.ReadOnlyField(source='assessment.course.title')

    class Meta:
        model = AssessmentScore
        fields = ('id', 'student', 'student_email', 'assessment', 'assessment_title', 
                 'course_title', 'total_score', 'submitted_at')
        read_only_fields = ('student_email', 'assessment_title', 'course_title', 
                          'submitted_at', 'total_score')
