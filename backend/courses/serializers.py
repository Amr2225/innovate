from rest_framework import serializers
from django.db import IntegrityError
from courses.models import Course
from rest_framework.exceptions import ValidationError
from chapter.serializers import ChapterSerializer
from users.models import User
from enrollments.models import Enrollments

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "middle_name", "last_name", "national_id", "birth_date", "age", 'date_joined', 'email',]

class PrerequisiteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'prerequisite_course', 'instructors', 'total_grade', 'credit_hours', 'semester', 'level', 'is_active', 'is_summer_open']

class CourseSerializer(serializers.ModelSerializer):
    prerequisite_course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.none(),
        required=False,
        allow_null=True
    )
    instructors_data = InstructorSerializer(source='instructors', many=True, read_only=True)
    prerequisite_course_data = PrerequisiteCourseSerializer(source='prerequisite_course', read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'description',
            'prerequisite_course',
            'prerequisite_course_data',
            'instructors',
            'instructors_data',
            'passing_grade',
            'total_grade',
            'is_active',
            'credit_hours',
            'semester',
            'level',
            'chapters',
            'is_summer_open'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request.user.role == "Institution":
            institution_id = request.user.id
            self.fields['prerequisite_course'].queryset = Course.objects.filter(institution_id=institution_id)
            self.fields['instructors'].queryset = User.objects.filter(role="Teacher", institution=institution_id)
    
    def validate_prerequisite_course(self, value):
        request = self.context.get('request')
        if value and request and request.user.role == "Institution":
            if value.institution != request.user:
                raise ValidationError("Prerequisite course must belong to the same institution.")
        return value
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep.pop('instructors', None)
        rep.pop('prerequisite_course', None)
        return rep
    
    def create(self, validated_data):
        request = self.context.get('request')
        instructors = validated_data.pop('instructors', [])

        try:
            course = Course.objects.create(institution=request.user, **validated_data)
        except IntegrityError:
            raise ValidationError({"name": "A course with this name already exists for your institution."})

        course.instructors.set(instructors)
        if request.user.institution_type == "school":
            semester = course.semester
            students = User.objects.filter(role="Student", semester=semester, institution=request.user)
            for student in students:
                Enrollments.objects.get_or_create(user=student, course=course)

        return course