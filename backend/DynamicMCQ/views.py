from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from .models import DynamicMCQ, DynamicMCQQuestions
from .serializers import DynamicMCQSerializer, DynamicMCQQuestionsSerializer
from assessment.models import Assessment
from users.models import User
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.apps import apps
from rest_framework.parsers import MultiPartParser, JSONParser
from decimal import Decimal
from users.permissions import isInstitution, isTeacher, isStudent
from enrollments.models import Enrollments
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.

def get_assessment_model():
    return apps.get_model('assessment', 'Assessment')

class DynamicMCQPermission(permissions.BasePermission):
    """Custom permission class for Dynamic MCQ questions"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return True
            
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        if request.method in permissions.SAFE_METHODS:
            # Students can only view questions for their enrolled courses
            if user.role == "Student":
                return obj.assessment.course.enrollments.filter(user=user).exists()
            return True
            
        # Only creator or course instructor/institution can modify
        return (obj.created_by == user or 
                obj.assessment.course.instructors.filter(id=user.id).exists() or
                obj.assessment.course.institution == user)

class DynamicMCQListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list and create Dynamic MCQ questions for an assessment.

    This endpoint allows teachers and institutions to manage Dynamic MCQ questions for their assessments.

    GET /api/assessments/{assessment_id}/dynamic-mcq/
    List all Dynamic MCQ questions for an assessment with filtering options:
    - assessment: Filter by assessment ID
    - title: Filter by title (case-insensitive contains)
    - created_by: Filter by creator ID
    - created_at: Filter by creation date

    POST /api/assessments/{assessment_id}/dynamic-mcq/
    Create a new Dynamic MCQ question for an assessment.

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    POST Request Body:
    ```json
    {
        "title": "string",
        "questions": [
            {
                "question": "string",
                "options": ["string"],
                "answer_key": "string",
                "question_grade": "decimal",
                "difficulty": "string"
            }
        ]
    }
    ```

    Returns:
    ```json
    {
        "id": "uuid",
        "assessment": "uuid",
        "title": "string",
        "questions": [
            {
                "id": "uuid",
                "question": "string",
                "options": ["string"],
                "answer_key": "string",  // Only for teachers/institutions
                "question_grade": "decimal",
                "difficulty": "string",
                "created_by": "uuid",
                "created_at": "datetime",
                "updated_at": "datetime"
            }
        ],
        "created_by": "uuid",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
    ```

    Status Codes:
    - 200: Successfully retrieved questions
    - 201: Successfully created question
    - 400: Invalid input data
    - 403: Not authorized to manage questions
    - 404: Assessment not found

    Permissions:
    - Students: Can view questions for courses they're enrolled in
    - Teachers: Can manage questions for courses they teach
    - Institutions: Can manage questions for their courses

    Notes:
    - Total question grades must not exceed assessment's remaining grade
    - Answer key must be one of the provided options
    - Assessment must not be past due date
    """
    serializer_class = DynamicMCQSerializer
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [DynamicMCQPermission]

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')
        
        try:
            Assessment = get_assessment_model()
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment": "Assessment not found"})
            
        base_queryset = DynamicMCQ.objects.filter(assessment=assessment)
        
        if user.role == "Student":
            # Students can only see questions for their enrolled courses
            return base_queryset.filter(
                assessment__course__enrollments__user=user
            ).select_related('assessment', 'created_by')
            
        elif user.role in ["Teacher", "Institution"]:
            # Teachers/Institutions can see questions they created or for their courses
            return base_queryset.filter(
                Q(created_by=user) |
                Q(assessment__course__instructors=user) |
                Q(assessment__course__institution=user)
            ).select_related('assessment', 'created_by')
            
        return DynamicMCQ.objects.none()

    def perform_create(self, serializer):
        assessment_id = self.kwargs.get('assessment_id')
        try:
            Assessment = get_assessment_model()
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment": "Assessment not found"})
            
        # Validate course ownership
        user = self.request.user
        if user.role == "Institution" and assessment.course.institution != user:
            raise PermissionDenied("You don't have permission to add questions to this assessment")
        elif user.role == "Teacher" and not assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to add questions to this assessment")
            
        # Validate assessment status
        if assessment.due_date < timezone.now():
            raise ValidationError("Cannot add questions to past-due assessments")
            
        serializer.save(assessment=assessment)

class DynamicMCQQuestionsListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list and create questions for a Dynamic MCQ.

    This endpoint allows teachers and institutions to manage questions for a Dynamic MCQ.

    GET /api/dynamic-mcq/{dynamic_mcq_id}/questions/
    List all questions for a Dynamic MCQ with filtering options:
    - dynamic_mcq: Filter by Dynamic MCQ ID
    - question: Filter by question text (case-insensitive contains)
    - difficulty: Filter by difficulty level
    - question_grade: Filter by question grade
    - created_by: Filter by creator ID
    - created_at: Filter by creation date

    POST /api/dynamic-mcq/{dynamic_mcq_id}/questions/
    Create a new question for a Dynamic MCQ.

    Parameters:
    - dynamic_mcq_id (UUID): The ID of the Dynamic MCQ

    POST Request Body:
    ```json
    {
        "question": "string",
        "options": ["string"],
        "answer_key": "string",
        "question_grade": "decimal",
        "difficulty": "string"
    }
    ```

    Returns:
    ```json
    {
        "id": "uuid",
        "dynamic_mcq": "uuid",
        "question": "string",
        "options": ["string"],
        "answer_key": "string",  // Only for teachers/institutions
        "question_grade": "decimal",
        "difficulty": "string",
        "created_by": "uuid",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
    ```

    Status Codes:
    - 200: Successfully retrieved questions
    - 201: Successfully created question
    - 400: Invalid input data
    - 403: Not authorized to manage questions
    - 404: Dynamic MCQ not found

    Permissions:
    - Students: Can view questions for courses they're enrolled in
    - Teachers: Can manage questions for courses they teach
    - Institutions: Can manage questions for their courses

    Notes:
    - Question grade must not exceed Dynamic MCQ's remaining grade
    - Answer key must be one of the provided options
    """
    serializer_class = DynamicMCQQuestionsSerializer
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [DynamicMCQPermission]

    def get_queryset(self):
        user = self.request.user
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        
        try:
            dynamic_mcq = DynamicMCQ.objects.get(id=dynamic_mcq_id)
        except DynamicMCQ.DoesNotExist:
            raise ValidationError({"dynamic_mcq": "Dynamic MCQ not found"})
            
        base_queryset = DynamicMCQQuestions.objects.filter(dynamic_mcq=dynamic_mcq)
        
        if user.role == "Student":
            # Students can only see questions for their enrolled courses
            return base_queryset.filter(
                dynamic_mcq__assessment__course__enrollments__user=user
            ).select_related('dynamic_mcq', 'created_by')
            
        elif user.role in ["Teacher", "Institution"]:
            # Teachers/Institutions can see questions they created or for their courses
            return base_queryset.filter(
                Q(created_by=user) |
                Q(dynamic_mcq__assessment__course__instructors=user) |
                Q(dynamic_mcq__assessment__course__institution=user)
            ).select_related('dynamic_mcq', 'created_by')
            
        return DynamicMCQQuestions.objects.none()

    def perform_create(self, serializer):
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        try:
            dynamic_mcq = DynamicMCQ.objects.get(id=dynamic_mcq_id)
        except DynamicMCQ.DoesNotExist:
            raise ValidationError({"dynamic_mcq": "Dynamic MCQ not found"})
            
        # Validate course ownership
        user = self.request.user
        if user.role == "Institution" and dynamic_mcq.assessment.course.institution != user:
            raise PermissionDenied("You don't have permission to add questions to this Dynamic MCQ")
        elif user.role == "Teacher" and not dynamic_mcq.assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to add questions to this Dynamic MCQ")
            
        # Validate assessment status
        if dynamic_mcq.assessment.due_date < timezone.now():
            raise ValidationError("Cannot add questions to past-due assessments")
            
        serializer.save(
            created_by=user,
            dynamic_mcq=dynamic_mcq
        )

class DynamicMCQDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DynamicMCQSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see MCQs for courses they're enrolled in
            return DynamicMCQ.objects.filter(
                assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see MCQs for their courses
            return DynamicMCQ.objects.filter(
                assessment__course__institution=user
            )
        
        return DynamicMCQ.objects.none()

class DynamicMCQQuestionsDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting Dynamic MCQ questions.

    This endpoint allows teachers and institutions to:
    - Get a specific question's details (GET)
    - Update a question (PUT/PATCH)
    - Delete a question (DELETE)

    GET /api/dynamic-mcqs/{dynamic_mcq_id}/questions/{question_id}/
    
    Returns question details:
    ```json
    {
        "id": "uuid",
        "question": "string",
        "options": ["string"],
        "answer_key": "string",
        "question_grade": "string",
        "difficulty": "string",
        "created_by": "uuid"
    }
    ```

    PUT /api/dynamic-mcqs/{dynamic_mcq_id}/questions/{question_id}/
    
    Update a question:
    ```json
    {
        "question": "Updated question?",
        "options": ["New Option 1", "New Option 2", "New Option 3", "New Option 4"],
        "answer_key": "New Option 1",
        "question_grade": "2.00",
        "difficulty": "3"
    }
    ```

    DELETE /api/dynamic-mcqs/{dynamic_mcq_id}/questions/{question_id}/
    
    Delete a question.

    Status Codes:
    - 200: Successfully retrieved/updated question
    - 204: Question deleted successfully
    - 400: Invalid input data
    - 403: Not authorized to modify question
    - 404: Question not found
    """
    serializer_class = DynamicMCQQuestionsSerializer
    permission_classes = [permissions.IsAuthenticated, DynamicMCQPermission]

    def get_queryset(self):
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see questions for MCQs in courses they're enrolled in
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__enrollments__user=user
            ).distinct()
        elif user.role == "Teacher":
            # Teachers can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__instructors=user
            )
        elif user.role == "Institution":
            # Institutions can see questions for their MCQs
            return DynamicMCQQuestions.objects.filter(
                dynamic_mcq_id=dynamic_mcq_id,
                dynamic_mcq__assessment__course__institution=user
            )
        
        return DynamicMCQQuestions.objects.none()
