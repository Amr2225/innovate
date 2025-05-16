from rest_framework import serializers
from institution_policy.models import InstitutionPolicy

class InstitutionPolicySerializer(serializers.ModelSerializer):

    class Meta:
        model = InstitutionPolicy
        fields = (
            'id',
            'min_passing_grade',
            'max_allowed_failures',
            'min_gpa_required',
            'min_attendance_percent',
        )