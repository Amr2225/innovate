from rest_framework import serializers
from users.models import User
from enrollments.models import Enrollments
from courses.serializers import CourseSerializer, InstructorSerializer


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name', 'national_id',
                  'level', 'semester', 'birth_date', 'age', 'date_joined', 'email']


class EligibleCourseSerializer(CourseSerializer):
    instructors = InstructorSerializer(many=True, read_only=True)

    class Meta(CourseSerializer.Meta):
        fields = (
            'id',
            'name',
            'description',
            'instructors',
            'credit_hours',
            'semester',
            'level'
        )


class EnrollmentsSerializer(serializers.ModelSerializer):
    user = StudentSerializer(read_only=True)
    course = serializers.SerializerMethodField()

    class Meta:
        model = Enrollments
        fields = (
            'id',
            'user',
            'course',
            'enrolled_at',
            'is_completed'
        )

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('user', None)
        rep.pop('course', None)
        return rep

    def get_course(self, obj):
        serializer_context = {'request': self.context.get(
            'request')} if self.context.get('request') else {}
        return CourseSerializer(obj.course, context=serializer_context).data


class EnrollMultipleCoursesSerializer(serializers.Serializer):
    courses = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of Course IDs to enroll in"
    )
