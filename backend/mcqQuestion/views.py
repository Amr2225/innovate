from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import McqQuestion
from .serializers import McqQuestionSerializer


class McqQuestionListCreateAPIView(generics.ListCreateAPIView):
    """
    View to list all MCQ questions for a specific assessment and create new ones.
    Only users with 'Teacher' or 'Institution' roles can create questions.
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        assessment_id = self.kwargs.get('assessment_id')
        return McqQuestion.objects.filter(assessment_id=assessment_id)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only Teachers or Institutions can create MCQ questions.")
        serializer.save(created_by=user)


class McqQuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific MCQ question.
    Only the user who created the question can modify it.
    """
    queryset = McqQuestion.objects.all()
    serializer_class = McqQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj = super().get_object()
        if self.request.user != obj.created_by:
            raise PermissionDenied("You do not have permission to modify this question.")
        return obj
