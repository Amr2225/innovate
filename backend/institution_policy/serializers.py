from rest_framework import serializers
from institution.serializers import User
from institution_policy.models import InstitutionPolicy


class InstitutionPolicySerializer(serializers.ModelSerializer):
    access_code = serializers.SerializerMethodField(read_only=True)

    def get_access_code(self, obj):
        request = self.context.get('request')
        if request and request.user:
            institution = User.objects.get(id=request.user.id)
            return institution.access_code if institution else None
        return None

    class Meta:
        model = InstitutionPolicy
        fields = (
            'id',
            'min_passing_percentage',
            'max_allowed_failures',
            'min_gpa_required',
            'min_attendance_percent',
            'max_allowed_courses_per_semester',
            'year_registration_open',
            'summer_registration_open',
            'promotion_time',
            "access_code"
        )
