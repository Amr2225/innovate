from rest_framework import serializers
from users.models import User
from enrollments.models import Enrollments
from users.serializers import InstitutionUserSeralizer
from courses.serializers import CourseSerializer
from assessment.models import AssessmentScore

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'national_id', 'level', 'semester', 'birth_date', 'age', 'date_joined', 'email']

class EnrollmentsSerializer(serializers.ModelSerializer):
    user_data = StudentSerializer(source='user', read_only=True)
    course_data = serializers.SerializerMethodField()
    total_score = serializers.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        model = Enrollments
        fields = (
            'id',
            'user',
            'user_data',
            'course',
            'course_data',
            'enrolled_at',
            'is_completed',
            'total_score'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('user', None)
        rep.pop('course', None)
        return rep
    
    def get_course_data(self, obj):
        serializer_context = {'request': self.context.get('request')} if self.context.get('request') else {}
        return CourseSerializer(obj.course, context=serializer_context).data

class EnrollMultipleCoursesSerializer(serializers.Serializer):
    courses = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of Course IDs to enroll in"
    )

class AssessmentScoreSerializer(serializers.ModelSerializer):
    assessment_title = serializers.CharField(source='assessment.title')
    assessment_type = serializers.CharField(source='assessment.type')
    
    class Meta:
        model = AssessmentScore
        fields = ['id', 'assessment_title', 'assessment_type', 'total_score', 'submitted_at']
