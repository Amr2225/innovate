from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, permissions, status, generics
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import HandwrittenQuestion, HandwrittenQuestionScore
from .serializers import HandwrittenQuestionSerializer, HandwrittenQuestionScoreSerializer
from assessment.models import Assessment
from enrollments.models import Enrollments
from main.AI import evaluate_handwritten_answer
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging
from rest_framework.exceptions import PermissionDenied
from django.conf import settings
from django.apps import apps
# from assessment.filters import HandwrittenQuestionFilterSet
from decimal import Decimal
from users.permissions import isInstitution, isTeacher, isStudent

logger = logging.getLogger(__name__)


def get_assessment_model():
    return apps.get_model('assessment', 'Assessment')


class HandwrittenQuestionPermission(permissions.BasePermission):
    """Custom permission class for Handwritten questions"""

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


class HandwrittenQuestionListCreateAPIView(generics.ListCreateAPIView):
    """
    API endpoint to list and create Handwritten questions for an assessment.

    This endpoint allows teachers and institutions to manage Handwritten questions for their assessments.

    GET /api/assessments/{assessment_id}/handwritten-questions/
    List all Handwritten questions for an assessment with filtering options:
    - assessment: Filter by assessment ID
    - question: Filter by question text (case-insensitive contains)
    - max_grade: Filter by maximum grade
    - section_number: Filter by section number
    - created_by: Filter by creator ID
    - created_at: Filter by creation date

    POST /api/assessments/{assessment_id}/handwritten-questions/
    Create a new Handwritten question for an assessment.

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    POST Request Body:
    ```json
    {
        "question": "string",
        "max_grade": "decimal",
        "section_number": "integer"
    }
    ```

    Returns:
    ```json
    {
        "id": "uuid",
        "assessment": "uuid",
        "question": "string",
        "max_grade": "decimal",
        "section_number": "integer",
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
    - Question grade must not exceed assessment's remaining grade
    - Assessment must not be past due date
    """
    serializer_class = HandwrittenQuestionSerializer
    parser_classes = (MultiPartParser, JSONParser)
    permission_classes = [HandwrittenQuestionPermission]
    filter_backends = [DjangoFilterBackend]
    # filterset_class = HandwrittenQuestionFilterSet

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')

        try:
            Assessment = get_assessment_model()
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment": "Assessment not found"})

        base_queryset = HandwrittenQuestion.objects.filter(
            assessment=assessment)

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

        return HandwrittenQuestion.objects.none()

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
            raise PermissionDenied(
                "You don't have permission to add questions to this assessment")
        elif user.role == "Teacher" and not assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied(
                "You don't have permission to add questions to this assessment")

        # Validate assessment status
        if assessment.due_date < timezone.now():
            raise ValidationError(
                "Cannot add questions to past-due assessments")

        # Set default grade if not provided
        if 'max_grade' not in self.request.data:
            serializer.validated_data['max_grade'] = Decimal('0.00')

        serializer.save(
            created_by=user,
            assessment=assessment
        )


class HandwrittenQuestionDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HandwrittenQuestionSerializer
    permission_classes = [HandwrittenQuestionPermission]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            return HandwrittenQuestion.objects.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            return HandwrittenQuestion.objects.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            is_completed = self.request.query_params.get(
                'is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return HandwrittenQuestion.objects.filter(assessment__course__id__in=enrolled_courses)
        return HandwrittenQuestion.objects.none()


class HandwrittenQuestionScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HandwrittenQuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        queryset = HandwrittenQuestionScore.objects.all()

        # Filter by question_id if provided
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # Filter by enrollment_id if provided
        enrollment_id = self.request.query_params.get('enrollment_id')
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        if user.role == "Institution":
            return queryset.filter(question__assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only see their own scores for enrolled courses
            is_completed = self.request.query_params.get(
                'is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return queryset.filter(
                question__assessment__course__id__in=enrolled_courses,
                enrollment__user=user
            )
        return HandwrittenQuestionScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise permissions.PermissionDenied(
                "Only students can submit answers")

        question = serializer.validated_data['question']

        # Check if the assessment is still accepting submissions
        if not question.assessment.accepting_submissions:
            raise permissions.PermissionDenied(
                "This assessment is no longer accepting submissions")

        # Get the enrollment
        is_completed = self.request.query_params.get(
            'is_completed', 'false').lower() == 'true'
        try:
            enrollment = Enrollments.objects.get(
                user=user,
                course=question.assessment.course,
                is_completed=is_completed
            )
        except Enrollments.DoesNotExist:
            raise permissions.PermissionDenied(
                "You are not enrolled in this course")

        # Check if student has already submitted
        if HandwrittenQuestionScore.objects.filter(question=question, enrollment=enrollment).exists():
            raise permissions.PermissionDenied(
                "You have already submitted an answer for this question")

        serializer.save(enrollment=enrollment)


class HandwrittenQuestionScoreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HandwrittenQuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        queryset = HandwrittenQuestionScore.objects.all()

        # Filter by question_id if provided
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)

        # Filter by enrollment_id if provided
        enrollment_id = self.request.query_params.get('enrollment_id')
        if enrollment_id:
            queryset = queryset.filter(enrollment_id=enrollment_id)

        if user.role == "Institution":
            return queryset.filter(question__assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(question__assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only access their own scores for enrolled courses
            is_completed = self.request.query_params.get(
                'is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return queryset.filter(
                question__assessment__course__id__in=enrolled_courses,
                enrollment__user=user
            )
        return HandwrittenQuestionScore.objects.none()


class HandwrittenQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = HandwrittenQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return HandwrittenQuestion.objects.all()
        return HandwrittenQuestion.objects.filter(
            assessment__course__enrollments__user=user,
            assessment__course__enrollments__is_active=True
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def submit_answer(self, request, pk=None):
        try:
            question = self.get_object()
            enrollment = get_object_or_404(
                Enrollments,
                user=request.user,
                course=question.assessment.course,
                is_active=True
            )

            # Check if assessment is still active
            if not question.assessment.is_active:
                return Response(
                    {"error": "This assessment is no longer active"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if student has already submitted an answer
            existing_score = HandwrittenQuestionScore.objects.filter(
                question=question,
                enrollment=enrollment
            ).first()

            if existing_score:
                return Response(
                    {"error": "You have already submitted an answer for this question"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the image file from request
            answer_image = request.FILES.get('image')
            if not answer_image:
                return Response(
                    {"error": "No image file provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Evaluate the answer using AI
            try:
                score, feedback, extracted_text = evaluate_handwritten_answer(
                    question=question.question_text,
                    answer_key=question.answer_key,
                    student_answer_image=answer_image,
                    max_grade=question.max_grade
                )
            except Exception as e:
                logger.error(f"AI evaluation error: {str(e)}")
                return Response(
                    {"error": f"Failed to evaluate answer: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create the score record
            score_data = {
                'question': question.id,
                'enrollment': enrollment.id,
                'score': score,
                'feedback': feedback,
                'answer_image': answer_image,
                'extracted_text': extracted_text
            }

            serializer = HandwrittenQuestionScoreSerializer(data=score_data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def get_score(self, request, pk=None):
        try:
            question = self.get_object()
            enrollment = get_object_or_404(
                Enrollments,
                user=request.user,
                course=question.assessment.course,
                is_active=True
            )

            score = HandwrittenQuestionScore.objects.filter(
                question=question,
                enrollment=enrollment
            ).first()

            if not score:
                return Response(
                    {"error": "No score found for this question"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = HandwrittenQuestionScoreSerializer(score)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error getting score: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HandwrittenQuestionScoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HandwrittenQuestionScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return HandwrittenQuestionScore.objects.all()
        return HandwrittenQuestionScore.objects.filter(
            enrollment__user=user,
            enrollment__is_active=True
        )
