from rest_framework import serializers
from users.models import User
from courses.models import Course
from enrollments.models import Enrollments

class CourseSerializer(serializers.ModelSerializer):
    prerequisite_course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.none(), required=False, allow_null=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'description',
            'prerequisite_course',
            'instructors',
            'total_grade',
            'credit_hours',
            'semester',
            'level'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request.user.role == "Institution":
            institution_id = request.user.id
            self.fields['prerequisite_course'].queryset = Course.objects.filter(institution_id=institution_id)
            self.fields['instructors'].queryset = User.objects.filter(role="Teacher", institution=institution_id)

    def create(self, validated_data):
        request = self.context.get('request')
        instructors = validated_data.pop('instructors', [])
        course = Course.objects.create(institution=request.user, **validated_data)
        course.instructors.set(instructors)
        if request.user.institution_type == "school":
            semester = course.semester
            students = User.objects.filter(role="Student", semester=semester, institution=request.user)
            for student in students:
                Enrollments.objects.get_or_create(user=student, course=course)

        return course
