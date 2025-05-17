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
            # Log request details
            logger.info("Received request for image evaluation")
            logger.info(f"Request content type: {request.content_type}")
            logger.info(f"Request FILES keys: {list(request.FILES.keys())}")
            
            # Check for image in both possible field names
            image_file = request.FILES.get('image') or request.FILES.get('answer_image')
            if not image_file:
                logger.error("No image file found in request")
                return Response(
                    {'error': 'No image file provided. Please upload an image file.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Log image file details
            logger.info(f"Image file name: {image_file.name}")
            logger.info(f"Image file content type: {image_file.content_type}")
            logger.info(f"Image file size: {image_file.size} bytes")

            # Validate image file
            if not image_file.content_type:
                logger.error("Image file has no content type")
                return Response(
                    {'error': 'Invalid image file. The file has no content type.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not image_file.content_type.startswith('image/'):
                logger.error(f"Invalid content type: {image_file.content_type}")
                return Response(
                    {
                        'error': 'Invalid file type',
                        'details': {
                            'received_type': image_file.content_type,
                            'expected_type': 'image/jpeg, image/png, image/gif, or image/bmp'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check file size (max 5MB)
            if image_file.size > 5 * 1024 * 1024:  # 5MB in bytes
                logger.error(f"File too large: {image_file.size} bytes")
                return Response(
                    {
                        'error': 'File too large',
                        'details': {
                            'received_size': f"{image_file.size / (1024 * 1024):.2f}MB",
                            'max_size': '5MB'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check file extension
            ext = image_file.name.split('.')[-1].lower()
            logger.info(f"File extension: {ext}")
            
            if ext not in ['jpg', 'jpeg', 'png', 'gif', 'bmp']:
                logger.error(f"Unsupported file extension: {ext}")
                return Response(
                    {
                        'error': 'Unsupported file format',
                        'details': {
                            'received_extension': ext,
                            'supported_extensions': ['jpg', 'jpeg', 'png', 'gif', 'bmp']
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Try to validate image using PIL
            try:
                from PIL import Image
                image = Image.open(image_file)
                logger.info(f"Successfully opened image. Format: {image.format}, Mode: {image.mode}, Size: {image.size}")
                
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                    logger.info("Converted image to RGB mode")
                
                # Reset file pointer
                image_file.seek(0)
                
            except Exception as e:
                logger.error(f"Failed to validate image with PIL: {str(e)}")
                return Response(
                    {
                        'error': 'Invalid image file',
                        'details': {
                            'error': str(e),
                            'suggestion': 'Please ensure the file is a valid image and not corrupted'
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get required parameters
            question_id = request.data.get('question_id')
            enrollment_id = request.data.get('enrollment_id')

            if not question_id:
                return Response(
                    {'error': 'question_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not enrollment_id:
                return Response(
                    {'error': 'enrollment_id is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                question = HandwrittenQuestion.objects.get(id=question_id)
                logger.info(f"Found question: {question.id} for course: {question.assessment.course.id}")
            except HandwrittenQuestion.DoesNotExist:
                return Response(
                    {'error': 'Question not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            try:
                enrollment = Enrollments.objects.get(
                    id=enrollment_id,
                    user=request.user,
                    is_completed=False
                )
                logger.info(f"Found enrollment: {enrollment.id} for course: {enrollment.course.id}")
            except Enrollments.DoesNotExist:
                return Response(
                    {'error': 'Enrollment not found or you do not have permission to submit for this enrollment'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Verify enrollment is for the correct course
            if enrollment.course != question.assessment.course:
                logger.error(f"Course mismatch - Question course: {question.assessment.course.id}, Enrollment course: {enrollment.course.id}")
                return Response(
                    {
                        'error': 'This enrollment is not for the course containing this question',
                        'details': {
                            'question_course_id': str(question.assessment.course.id),
                            'enrollment_course_id': str(enrollment.course.id)
                        }
                    },
                    status=status.HTTP_400_BAD_REQUEST
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
                'extracted_text': extracted_text,
                'answer_image': image_file
            }

            # Create the score record
            serializer = HandwrittenQuestionScoreSerializer(data=score_data, context={'request': request})
            if serializer.is_valid():
                score_instance = serializer.save()
                return Response({
                    'extracted_text': extracted_text,
                    'evaluation': {
                        'score': score,
                        'feedback': feedback,
                        'max_grade': question.max_grade
                    },
                    'score_record': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            # Log validation errors for debugging
            logger.error(f"Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error in extract and evaluate: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )