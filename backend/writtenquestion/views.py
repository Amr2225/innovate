from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import HandwrittenQuestion, WrittenQuestion
from .serializers import HandwrittenQuestionSerializer, WrittenQuestionSerializer

class HandwrittenQuestionViewSet(viewsets.ModelViewSet):
    queryset = HandwrittenQuestion.objects.all()
    serializer_class = HandwrittenQuestionSerializer
    permission_classes = [permissions.IsAuthenticated] # Adjust as needed
    parser_classes = (MultiPartParser, FormParser) # Crucial for image uploads

class WrittenQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = WrittenQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Students can only see their own answers
        # Staff/admin can see all answers
        if self.request.user.is_staff:
            return WrittenQuestion.objects.all()
        return WrittenQuestion.objects.filter(user_id=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user_id to the current user
        serializer.save(user_id=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_feedback(self, request, pk=None):
        written_question = self.get_object()
        
        if not written_question.student_answer:
            return Response({
                "error": "No answer provided to generate feedback"
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Here you would implement your AI scoring and feedback logic
            # For now, we'll use placeholder values
            score = 0.0  # Replace with actual AI scoring
            feedback = "Placeholder feedback"  # Replace with actual AI feedback

            written_question.score = score
            written_question.feedback = feedback
            written_question.save()

            return Response({
                "score": score,
                "feedback": feedback
            })
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

