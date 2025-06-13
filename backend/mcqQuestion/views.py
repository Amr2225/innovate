from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .serializers import McqQuestionSerializer
from rest_framework.parsers import JSONParser
from django.core.exceptions import ValidationError
from decimal import Decimal
import logging
from .validation import  validate_mcq_structure, validate_question_grade
from .permission import McqQuestionPermission

# Models
from mcqQuestion.models import McqQuestion
from assessment.models import Assessment


# Errors
from .errors import MissingLectureError, InvalidMCQStructureError, InvalidMCQError

logger = logging.getLogger(__name__)


class McqQuestionListCreateAPIView(generics.CreateAPIView):
    """
    API endpoint to list and create MCQ questions for an assessment.

    This endpoint allows teachers and institutions to manage MCQ questions for their assessments.

    GET /api/assessments/{assessment_id}/mcq-questions/
    List all MCQ questions for an assessment with filtering options:
    - assessment: Filter by assessment ID
    - question: Filter by question text (case-insensitive contains)
    - question_grade: Filter by question grade
    - section_number: Filter by section number
    - created_by: Filter by creator ID
    - created_at: Filter by creation date

    POST /api/assessments/{assessment_id}/mcq-questions/
    Create a new MCQ question for an assessment.

    Parameters:
    - assessment_id (UUID): The ID of the assessment

    POST Request Body:
    ```json
    {
        "question": "string",
        "options": ["string"],
        "answer_key": "string",
        "question_grade": "decimal",
        "section_number": "integer"
    }
    ```

    Returns:
    ```json
    {
        "id": "uuid",
        "assessment": "uuid",
        "question": "string",
        "options": ["string"],
        "answer_key": "string",  // Only for teachers/institutions
        "question_grade": "decimal",
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
    - Answer key must be one of the provided options
    - Assessment must not be past due date
    """
    serializer_class = McqQuestionSerializer
    parser_classes = (JSONParser,)
    permission_classes = [McqQuestionPermission]

    def get_queryset(self):
        user = self.request.user
        assessment_id = self.kwargs.get('assessment_id')

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError({"assessment": "Assessment not found"})

        base_queryset = McqQuestion.objects.filter(assessment=assessment)

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

        return McqQuestion.objects.none()

    def perform_create(self, serializer):
        assessment_id = self.kwargs.get('assessment_id')
        try:
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
        if 'question_grade' not in self.request.data:
            serializer.validated_data['question_grade'] = Decimal('0.00')

        serializer.save(
            created_by=user,
            assessment=assessment
        )


class McqQuestionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a specific MCQ question.
    Only the creator or assessment institution can modify it.
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [McqQuestionPermission]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        base_queryset = McqQuestion.objects.select_related(
            'assessment', 'created_by')

        if user.role == "Student":
            return base_queryset.filter(
                assessment__course__enrollments__user=user
            )
        elif user.role in ["Teacher", "Institution"]:
            return base_queryset.filter(
                Q(created_by=user) |
                Q(assessment__course__instructors=user) |
                Q(assessment__course__institution=user)
            )
        return McqQuestion.objects.none()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        # Remove answer key from response if user is a student
        if request.user.role == "Student":
            data.pop('answer_key', None)

        return Response(data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Validate assessment status
        if instance.assessment.due_date < timezone.now():
            raise ValidationError(
                "Cannot modify questions for past-due assessments")

        # Validate answer format
        if 'answer' in request.data:
            if not isinstance(request.data['answer'], list):
                raise ValidationError(
                    {"answer": "Answer must be a list of options"})
            if len(request.data['answer']) < 2:
                raise ValidationError(
                    {"answer": "At least 2 options are required"})

        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Validate assessment status
        if instance.assessment.due_date < timezone.now():
            raise ValidationError(
                "Cannot delete questions from past-due assessments")

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SaveGeneratedMCQsView(generics.GenericAPIView):
    """
    View for saving generated MCQ questions to the database.
    POST /mcqQuestion/assessments/{assessment_id}/save-generated-mcqs/

    Request body (JSON):
    {
        "mcqs": [
            {
                "question": "string",
                "options": ["string", "string", ...],  // Up to 6 options allowed
                "correct_answer": "string"
            }
        ],
        "question_grade": "2.00",  // optional, default=0.00
        "section_number": 1  // optional, default=1
    }
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [McqQuestionPermission]

    def post(self, request, *args, **kwargs):
        try:
            # Validate input
            if 'mcqs' not in request.data:
                raise InvalidMCQError()

            mcqs = request.data['mcqs']
            if not isinstance(mcqs, list) or not mcqs:
                raise InvalidMCQError()

            # Validate assessment exists and user has permission
            assessment_id = self.kwargs.get('assessment_id')
            try:
                assessment = Assessment.objects.get(id=assessment_id)
            except Assessment.DoesNotExist:
                raise ValidationError({"assessment": "Assessment not found"})

            # Validate course ownership
            user = request.user
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

            # Get question grade and section number
            question_grade = validate_question_grade(
                request.data.get('question_grade'))
            section_number = request.data.get('section_number', 1)
            print("question_grade", question_grade)

            # Save questions
            saved_questions = []
            for mcq in mcqs:
                try:
                    # Validate MCQ structure
                    validate_mcq_structure(mcq)

                    # Create question using serializer
                    serializer = self.get_serializer(data={
                        'question': mcq['question'],
                        'options': mcq['options'],
                        'answer_key': mcq['correct_answer'],
                        'assessment': assessment_id,
                        'question_grade': question_grade / len(mcqs),
                        'section_number': section_number
                    })

                    if not serializer.is_valid():
                        raise ValidationError(serializer.errors)

                    # Save the question
                    question = serializer.save(created_by=user)
                    saved_questions.append({
                        'id': str(question.id),
                        'question': question.question,
                        'options': question.options,
                        'answer_key': question.answer_key,
                        'question_grade': str(question.question_grade),
                        'section_number': question.section_number
                    })
                except Exception as e:
                    # If any question fails, delete all previously saved questions
                    if saved_questions:
                        for saved_q in saved_questions:
                            try:
                                instance = McqQuestion.objects.get(
                                    id=saved_q['id'])
                                instance.delete()
                            except Exception as delete_error:
                                logger.error(
                                    f"Error deleting question {saved_q['id']}: {str(delete_error)}")
                    raise

            return Response({
                'message': f'Successfully saved {len(saved_questions)} MCQ questions',
                'mcqs': saved_questions,
                'num_questions': len(saved_questions)
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({
                'message': e.detail if hasattr(e, 'detail') else str(e),
                'error_type': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Processing error: {str(e)}", exc_info=True)

            # Check if the exception is an API related exception
            if hasattr(e, 'status_code') and hasattr(e, 'error_type'):
                # Handle API-specific exceptions with their own status codes and error types
                return Response({
                    'message': str(e),
                    'error_type': e.error_type
                }, status=e.status_code)

            # Handle other exceptions with a generic error
            return Response({
                'error': str(e),
                'error_type': 'processing_error'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
