from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import QuestionScore
from .serializers import QuestionScoreSerializer
from users.permissions import isTeacher, isStudent

# Create your views here.

class QuestionScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return QuestionScore.objects.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            return QuestionScore.objects.filter(student=user)
        return QuestionScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit question scores.")
        serializer.save(student=user)


class QuestionScoreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return QuestionScore.objects.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            return QuestionScore.objects.filter(student=user)
        return QuestionScore.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role == "Teacher":
            # Teachers can only update feedback
            serializer.save(score=serializer.instance.score)  # Preserve original score
        elif user.role == "Student":
            if serializer.instance.student != user:
                raise PermissionDenied("You can only modify your own scores.")
            serializer.save()
        else:
            raise PermissionDenied("You don't have permission to update scores.")
