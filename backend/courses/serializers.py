from rest_framework import serializers
from users.models import User
from courses.models import Course

class CourseSerializer(serializers.ModelSerializer):
    prerequisite_course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.none(), required=False, allow_null=True)

    class Meta:
        model = Course
        fields = (
            'id',
            'name',
            'description',
            'prerequisite_course',
            'instructor',
            'credit_hours',
            'level'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get('request')
        if request.user.role == "Institution":
            institution_id = request.user.id
            self.fields['prerequisite_course'].queryset = Course.objects.filter(institution_id=institution_id)
            self.fields['instructor'].queryset = User.objects.filter(role="Teacher", institution=institution_id)

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['institution'] = request.user
        return Course.objects.create(**validated_data)