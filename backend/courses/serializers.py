from rest_framework import serializers
from django.db import IntegrityError
from courses.models import Course
from rest_framework.exceptions import ValidationError
from chapter.serializers import ChapterSerializer
from users.models import User
from enrollments.models import Enrollments


class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "full_name", "avatar", "email"]

        extra_kwargs = {
            'avatar': {'read_only': True},
        }


class PrerequisiteCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'prerequisite_course', 'instructors',
                  'total_grade', 'credit_hours', 'semester', 'level', 'is_active', 'is_summer_open']


class CourseSerializer(serializers.ModelSerializer):
    prerequisite_course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.none(),
        required=False,
        allow_null=True
    )

    prerequisite_course_detail = PrerequisiteCourseSerializer(
        source='prerequisite_course', read_only=True)
    instructors_detials = InstructorSerializer(
        source='instructors', many=True, read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    # instructors_data = InstructorSerializer(
    #     source='instructors', many=True, read_only=True)
    # prerequisite_course_data = PrerequisiteCourseSerializer(
    #     source='prerequisite_course', read_only=True)

    def get_students_count(self, obj):
        return Enrollments.objects.filter(course=obj, is_completed=False).count()

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'description',
            'prerequisite_course',
            'prerequisite_course_detail',
            'instructors',
            'instructors_detials',
            'passing_grade',
            'total_grade',
            'is_active',
            'credit_hours',
            'semester',
            'level',
            'chapters',
            'students_count',
            # 'chapters'
            'is_summer_open'
        )

        extra_kwargs = {
            'instructors': {'required': False},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request.user.role == "Institution":
            institution_id = request.user.id
            self.fields['prerequisite_course'].queryset = Course.objects.filter(
                institution_id=institution_id)
            self.fields['instructors'].queryset = User.objects.filter(
                role="Teacher", institution=institution_id)

    def validate_prerequisite_course(self, value):
        request = self.context.get('request')
        if value and request and request.user.role == "Institution":
            if value.institution != request.user:
                raise ValidationError(
                    "Prerequisite course must belong to the same institution.")
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
            course = Course.objects.create(
                institution=request.user, **validated_data)
        except IntegrityError:
            raise ValidationError(
                {"name": "A course with this name already exists for your institution."})

        course.instructors.set(instructors)
        if request.user.institution_type == "school":
            semester = course.semester
            students = User.objects.filter(
                role="Student", semester=semester, institution=request.user)
            for student in students:
                Enrollments.objects.get_or_create(user=student, course=course)

        return course
