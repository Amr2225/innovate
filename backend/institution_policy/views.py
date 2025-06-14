from rest_framework import generics
from institution_policy.models import InstitutionPolicy
from institution_policy.serializers import InstitutionPolicySerializer
from users.permissions import isInstitution


class PolicyUpdateOrCreateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [isInstitution]
    serializer_class = InstitutionPolicySerializer

    def get_object(self):
        obj = InstitutionPolicy.objects.get_or_create(
            institution=self.request.user)

        return obj[0]
