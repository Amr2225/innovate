from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import Assessment, AssessmentScore, Question, QuestionResponse
from .serializers import (
    AssessmentSerializer, 
    AssessmentScoreSerializer, 
    QuestionSerializer,
    QuestionResponseSerializer
)
from users.permissions import isStudent, isTeacher

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
# Question Views
# ----------------------

class QuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, isTeacher]

    def get_queryset(self):
        assessment_id = self.kwargs.get('assessment_id')
        return Question.objects.filter(assessment_id=assessment_id)

    def perform_create(self, serializer):
        assessment_id = self.kwargs.get('assessment_id')
        serializer.save(assessment_id=assessment_id)

# ----------------------
# Question Response Views
# ----------------------

class QuestionResponseCreateAPIView(generics.CreateAPIView):
    serializer_class = QuestionResponseSerializer
    permission_classes = [permissions.IsAuthenticated, isStudent]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class QuestionResponseUpdateAPIView(generics.UpdateAPIView):
    serializer_class = QuestionResponseSerializer
    permission_classes = [permissions.IsAuthenticated, isTeacher]
    
    def get_queryset(self):
        return QuestionResponse.objects.all()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == "Teacher":
            return AssessmentScore.objects.filter(
                assessment__institution=self.request.user
            ).select_related('student', 'assessment')
        else:
            return AssessmentScore.objects.filter(
                student=self.request.user
            ).select_related('student', 'assessment')

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [isStudent]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

class AssessmentScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == "Teacher":
            return AssessmentScore.objects.filter(
                assessment__institution=self.request.user
            )
        else:
            return AssessmentScore.objects.filter(
                student=self.request.user
            )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_student_assessment_grade(request, assessment_id):
    try:
        if request.user.role == "Student":
            score = AssessmentScore.objects.get(
                assessment_id=assessment_id,
                student=request.user
            )
        else:
            student_id = request.query_params.get('student_id')
            if not student_id:
                return Response(
                    {"error": "student_id query parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            score = AssessmentScore.objects.get(
                assessment_id=assessment_id,
                student_id=student_id
            )
        
        serializer = AssessmentScoreSerializer(score)
        return Response(serializer.data)
    
    except AssessmentScore.DoesNotExist:
        return Response(
            {"error": "Assessment score not found"},
            status=status.HTTP_404_NOT_FOUND
        )
        
        

