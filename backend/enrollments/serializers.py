from rest_framework import serializers
from users.models import User
from enrollments.models import Enrollments

class EnrollmentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Enrollments
        fields = (
            'id',
            'user',
            'course',
            'enrolled_at',
            'is_completed'
        )


class EnrollMultipleCoursesSerializer(serializers.Serializer):
    courses = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of Course IDs to enroll in"
    )