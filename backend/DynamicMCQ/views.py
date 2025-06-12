from django.forms import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics, permissions
from .models import DynamicMCQ, DynamicMCQQuestions
from .serializers import DynamicMCQSerializer, DynamicMCQQuestionsSerializer
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from django.apps import apps
from rest_framework.parsers import MultiPartParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend


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

    POST /{assessment_id}/
    Create a new Dynamic MCQ for an assessment.

    Request body:
    {
        "section_number": 1,  // Required: Section number within the assessment
        "context": "string",  // Optional: Text context to generate questions from
        "lecture_ids": ["uuid1", "uuid2"],  // Optional: Array of lecture UUIDs
        "difficulty": "3",  // Optional: Difficulty level (1-5, default=3)
        "num_options": 4,  // Optional: Number of options per question (2-6, default=4)
        "total_grade": 10,  // Required: Total grade for all questions
        "number_of_questions": 5  // Required: Number of questions to generate
    }
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

    def create(self, request, *args, **kwargs):
        assessment_id = self.kwargs.get('assessment_id')
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            error_msg = next(iter(serializer.errors.values()))
            [0] if serializer.errors else "Validation error"
            return Response({"message": "\n".join(error_msg)}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Assessment = get_assessment_model()
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment": "Assessment not found"})

        # Validate course ownership
        user = self.request.user
        if user.role == "Institution" and assessment.course.institution != user:
            raise PermissionDenied(
                "You don't have permission to add questions to this assessment")
        elif user.role == "Teacher" and not assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied(
                "You don't have permission to add questions to this assessment")

        # Validate assessment status
        if assessment.due_date < timezone.now():
            raise ValidationError(
                "Cannot add questions to past-due assessments")

        # Get num_options from request data or use default
        num_options = self.request.data.get('num_options', 4)
        if not isinstance(num_options, int) or num_options < 2 or num_options > 6:
            raise ValidationError(
                "Number of options must be between 2 and 6")

        serializer.save(
            assessment=assessment,
            num_options=num_options
        )
        return Response({"message": "Dynamic MCQ created successfully"}, status=status.HTTP_201_CREATED)


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
    filter_backends = [DjangoFilterBackend]
    # filterset_class = DynamicMCQQuestionsFilterSet

    def get_queryset(self):
        user = self.request.user
        dynamic_mcq_id = self.kwargs.get('dynamic_mcq_id')

        try:
            dynamic_mcq = DynamicMCQ.objects.get(id=dynamic_mcq_id)
        except DynamicMCQ.DoesNotExist:
            raise ValidationError({"dynamic_mcq": "Dynamic MCQ not found"})

        base_queryset = DynamicMCQQuestions.objects.filter(
            dynamic_mcq=dynamic_mcq)

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
            raise PermissionDenied(
                "You don't have permission to add questions to this Dynamic MCQ")
        elif user.role == "Teacher" and not dynamic_mcq.assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied(
                "You don't have permission to add questions to this Dynamic MCQ")

        # Validate assessment status
        if dynamic_mcq.assessment.due_date < timezone.now():
            raise ValidationError(
                "Cannot add questions to past-due assessments")

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
