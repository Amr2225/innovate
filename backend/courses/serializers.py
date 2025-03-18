from rest_framework import serializers
from users.models import User
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    instructor = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all())

    class Meta:
        model = Course
        fields = (
            'name',
            'description',
            'instructor',
            'institution'
        )

    def create(self, validated_data):
        course = Course(
            name=validated_data['name'],
            description=validated_data['description'],
            instructor=validated_data.get('instructor', None),
            institution=validated_data.get('institution', None)
        )
        course.save()
        return course
