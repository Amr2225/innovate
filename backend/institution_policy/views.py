from rest_framework import generics
from rest_framework.exceptions import NotFound
from institution_policy.models import InstitutionPolicy
from institution_policy.serializers import InstitutionPolicySerializer
from users.permissions import isInstitution

class PolicyUpdateOrCreateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = InstitutionPolicySerializer
    permission_classes = [isInstitution]

    def get_object(self):
        obj, created = InstitutionPolicy.objects.get_or_create(institution=self.request.user)
        return obj

    def get_permissions(self):
        self.permission_classes = [isInstitution]
        return super().get_permissions()