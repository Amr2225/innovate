from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from .models import MCQQuestionScore
from .serializers import MCQQuestionScoreSerializer
from users.permissions import isStudent, isTeacher
from mcqQuestion.models import McqQuestion
from assessment.models import Assessment, AssessmentScore
from django.db import transaction
from django.utils import timezone

# Create your views here.

class MCQQuestionScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = MCQQuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return MCQQuestionScore.objects.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            return MCQQuestionScore.objects.filter(student=user)
        return MCQQuestionScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit answers")

        # Get the question instance
        question_id = self.request.data.get('question')
        try:
            question = McqQuestion.objects.get(id=question_id)
        except McqQuestion.DoesNotExist:
            raise ValidationError({"question": "Question does not exist"})

        # Check if assessment is active and accepting submissions
        assessment = question.assessment
        if not assessment.is_active or not assessment.accepting_submissions:
            raise ValidationError({"detail": "This assessment is not currently accepting submissions"})

        # Validate that student hasn't already answered this question
        if MCQQuestionScore.objects.filter(student=user, question=question).exists():
            raise ValidationError({"detail": "You have already answered this question"})

        # Validate selected answer is one of the options
        selected_answer = self.request.data.get('selected_answer')
        if not selected_answer:
            raise ValidationError({"selected_answer": "This field is required"})

        if selected_answer not in question.answer:
            raise ValidationError({"selected_answer": "Selected answer must be one of the provided options"})

        with transaction.atomic():
            # Save the answer
            serializer.save(
                student=user,
                is_correct=(selected_answer == question.answer_key)
            )

            # Update or create AssessmentScore
            AssessmentScore.objects.update_or_create(
                student=user,
                assessment=assessment,
                defaults={'total_score': assessment.get_student_score(user)}
            )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # Include whether the answer was correct in the response
        response_data = serializer.data
        response_data['is_correct'] = serializer.instance.is_correct
        
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

class MCQQuestionScoreDetailView(generics.RetrieveAPIView):
    serializer_class = MCQQuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return MCQQuestionScore.objects.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            return MCQQuestionScore.objects.filter(student=user)
        return MCQQuestionScore.objects.none()
