from rest_framework import serializers
from courses.models import Course
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
        fields = ['id', 'name', 'description', 'prerequisite_course',
                  'instructors', 'total_grade', 'credit_hours', 'semester', 'level']


class CourseSerializer(serializers.ModelSerializer):
    prerequisite_course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.none(),
        required=False,
        allow_null=True,
        write_only=True
    )

    prerequisite_course_detail = PrerequisiteCourseSerializer(
        source='prerequisite_course', read_only=True)
    instructors_detials = InstructorSerializer(
        source='instructors', many=True, read_only=True)
    # chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'description',
            'prerequisite_course',
            'prerequisite_course_detail',
            'instructors',
            "instructors_detials",
            'total_grade',
            'credit_hours',
            'semester',
            'level',
            # 'chapters'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request and request.user.role == "Institution":
            institution_id = request.user.id
            self.fields['prerequisite_course'].queryset = Course.objects.filter(
                institution_id=institution_id)
            self.fields['instructors'].queryset = User.objects.filter(
                role="Teacher", institution=institution_id)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        # Remove the write-only field from the response
        # rep.pop('prerequisite_course', None)
        return rep

    def create(self, validated_data):
        request = self.context.get('request')
        instructors = validated_data.pop('instructors', [])
        print(instructors)
        prerequisite_course = validated_data.pop('prerequisite_course', None)
        course = Course.objects.create(
            institution=request.user, **validated_data)
        course.instructors.set(instructors)
        if prerequisite_course:
            course.prerequisite_course = prerequisite_course
            course.save()
        if request.user.institution_type == "school":
            semester = course.semester
            students = User.objects.filter(
                role="Student", semester=semester, institution=request.user)
            for student in students:
                Enrollments.objects.get_or_create(user=student, course=course)

        return course
