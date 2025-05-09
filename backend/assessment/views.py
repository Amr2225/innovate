from rest_framework import generics, permissions
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer

# ----------------------
# Assessment Views
# ----------------------

class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['due_date', 'type', 'title']

    def get_queryset(self):
        return Assessment.objects.filter(institution=self.request.user)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user)


class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Assessment.objects.filter(institution=self.request.user)

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    queryset = AssessmentScore.objects.all()
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]


class AssessmentScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AssessmentScore.objects.all()
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
