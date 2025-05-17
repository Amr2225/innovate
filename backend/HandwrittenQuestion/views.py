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
from main.AI import evaluate_handwritten_answer, extract_text_from_image
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class HandwrittenQuestionPermission(permissions.BasePermission):
    """Custom permission class for handwritten questions"""
    
    def has_permission(self, request, view):
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Teachers and institutions can create/update/delete
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # For read operations
        if request.method in permissions.SAFE_METHODS:
            if user.role == "Student":
                # Students can only view questions for courses they're enrolled in
                is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
                return Enrollments.objects.filter(
                    user=user,
                    course=obj.assessment.course,
                    is_completed=is_completed
                ).exists()
            elif user.role == "Teacher":
                # Teachers can view questions for courses they teach
                return obj.assessment.course.instructors.filter(id=user.id).exists()
            elif user.role == "Institution":
                # Institution can view any question in their courses
                return obj.assessment.course.institution == user
            return False

        # For write operations (create/update/delete)
        if user.role == "Teacher":
            # Teachers can modify questions for courses they teach
            return obj.assessment.course.instructors.filter(id=user.id).exists()
        elif user.role == "Institution":
            # Institution can modify any question in their courses
            return obj.assessment.course.institution == user
        return False

class HandwrittenQuestionListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = HandwrittenQuestionSerializer
    permission_classes = [HandwrittenQuestionPermission]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            # Institution can see all questions in their courses
            return HandwrittenQuestion.objects.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            # Teachers can see questions for courses they teach
            return HandwrittenQuestion.objects.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only see questions for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return HandwrittenQuestion.objects.filter(assessment__course__id__in=enrolled_courses)
        return HandwrittenQuestion.objects.none()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
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
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
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
            raise permissions.PermissionDenied("Only students can submit answers")

        question = serializer.validated_data['question']
        
        # Check if the assessment is still accepting submissions
        if not question.assessment.accepting_submissions:
            raise permissions.PermissionDenied("This assessment is no longer accepting submissions")
        
        # Get the enrollment
        is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
        try:
            enrollment = Enrollments.objects.get(
                user=user,
                course=question.assessment.course,
                is_completed=is_completed
            )
        except Enrollments.DoesNotExist:
            raise permissions.PermissionDenied("You are not enrolled in this course")
        
        # Check if student has already submitted
        if HandwrittenQuestionScore.objects.filter(question=question, enrollment=enrollment).exists():
            raise permissions.PermissionDenied("You have already submitted an answer for this question")
        
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
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
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
    parser_classes = (MultiPartParser, FormParser)

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

class ExtractTextFromImageAPIView(generics.CreateAPIView):
    """
    API endpoint to extract text from an image
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_file = request.FILES['image']
            
            # Extract text from the image
            extracted_text = extract_text_from_image(image_file)
            
            return Response({
                'text': extracted_text
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ExtractAndEvaluateAnswerAPIView(generics.CreateAPIView):
    """
    API endpoint to extract text from an image and evaluate it using AI
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        try:
            if 'image' not in request.FILES:
                return Response(
                    {'error': 'No image file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            image_file = request.FILES['image']
            
            # Validate image file
            if not image_file.content_type.startswith('image/'):
                return Response(
                    {'error': 'The uploaded file is not an image. Please upload a valid image file (JPEG, PNG, etc.)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check file size (max 5MB)
            if image_file.size > 5 * 1024 * 1024:  # 5MB in bytes
                return Response(
                    {'error': 'Image file is too large. Maximum size is 5MB'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            question_id = request.data.get('question_id')
            if not question_id:
                return Response(
                    {'error': 'question_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                question = HandwrittenQuestion.objects.get(id=question_id)
            except HandwrittenQuestion.DoesNotExist:
                return Response(
                    {'error': 'Question not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the enrollment with more detailed error handling
            try:
                # First check if any enrollment exists
                enrollment_exists = Enrollments.objects.filter(
                    user=request.user,
                    course=question.assessment.course
                ).exists()
                
                if not enrollment_exists:
                    return Response(
                        {'error': 'You are not enrolled in this course. Please enroll first.'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                
                # Then check for active enrollment
                enrollment = Enrollments.objects.get(
                    user=request.user,
                    course=question.assessment.course,
                    is_completed=False
                )
            except Enrollments.DoesNotExist:
                return Response(
                    {'error': 'You are not enrolled in this course'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Check if student has already submitted
            if HandwrittenQuestionScore.objects.filter(question=question, enrollment=enrollment).exists():
                return Response(
                    {'error': 'You have already submitted an answer for this question'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get combined OCR and evaluation
            try:
                score, feedback, extracted_text = evaluate_handwritten_answer(
                    question=question.question_text,
                    answer_key=question.answer_key,
                    student_answer_image=image_file,
                    max_grade=float(question.max_grade)
                )
            except Exception as e:
                logger.error(f"AI evaluation error: {str(e)}")
                return Response(
                    {'error': f'Failed to process image: {str(e)}. Please ensure the image is clear and readable.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create the score record
            score_data = {
                'question': question.id,
                'enrollment': enrollment.id,
                'score': score,
                'feedback': feedback,
                'answer_image': image_file,
                'extracted_text': extracted_text
            }

            serializer = HandwrittenQuestionScoreSerializer(data=score_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'extracted_text': extracted_text,
                    'evaluation': {
                        'score': score,
                        'feedback': feedback,
                        'max_grade': question.max_grade
                    },
                    'score_record': serializer.data
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in extract and evaluate: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )