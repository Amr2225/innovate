from rest_framework import generics
from institution.models import Plan
from institution.plansSerializers import PlanSerializer

from users.permissions import isInstitution
from institution.models import Payment


class PlanListView(generics.ListAPIView):
    queryset = Plan.objects.all().order_by('order')
    serializer_class = PlanSerializer
    pagination_class = None


class PlanDetailView(generics.RetrieveAPIView):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = 'id'


class InstitutionCurrentPlanView(generics.RetrieveAPIView):
    serializer_class = PlanSerializer
    permission_classes = [isInstitution]

    def get_object(self):
        # Get current payment for logged in institution
        current_payment = Payment.objects.filter(
            institution=self.request.user,
            is_current=True
        ).first()

        if current_payment:
            return current_payment.plan
        return None
