from rest_framework import generics, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import AssessmentScore
from .serializers import AssessmentScoreSerializer

class AssessmentScoreListCreateView(generics.ListCreateAPIView):
    queryset = AssessmentScore.objects.all()
    serializer_class = AssessmentScoreSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['userId', 'assessmentId']
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Optional: auto-assign user if only users can submit their own score
        serializer.save()

class AssessmentScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssessmentScore.objects.all()
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
