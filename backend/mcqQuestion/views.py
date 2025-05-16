from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Sum
from .models import McqQuestion
from .serializers import McqQuestionSerializer
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.exceptions import ValidationError as DjangoValidationError
from .AI import generate_mcqs_from_text, extract_text_from_pdf
from decimal import Decimal
from assessment.models import AssessmentScore, Assessment
from django.db import transaction


class McqQuestionPermission(permissions.BasePermission):
    """Custom permission class for MCQ questions"""
    
    def has_permission(self, request, view):
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Only teachers and institutions can create
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # Anyone authenticated can view
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only the creator or the assessment institution can modify/delete
        return obj.created_by == user or obj.assessment.institution == user


class McqQuestionListCreateAPIView(generics.ListCreateAPIView):
    """
    View for listing and manually creating MCQ questions.
    POST /mcqQuestion/assessments/{assessment_id}/mcq-questions/
    
    For manual creation:
    {
        "question": "What is...?",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "answer_key": "Option 1",
        "question_grade": "10.00"
    }
    """
    serializer_class = McqQuestionSerializer
    parser_classes = (JSONParser,)
    permission_classes = [McqQuestionPermission]

    def get_queryset(self):
        assessment_id = self.kwargs.get('assessment_id')
        return McqQuestion.objects.filter(assessment_id=assessment_id)

    def perform_create(self, serializer):
        # Ensure question_grade is provided or set default
        if 'question_grade' not in self.request.data:
            serializer.validated_data['question_grade'] = Decimal('0.00')
            
        serializer.save(
            created_by=self.request.user,
            assessment_id=self.kwargs.get('assessment_id')
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
        base_queryset = McqQuestion.objects.select_related('assessment', 'created_by')

        if user.role in ["Teacher", "Institution"]:
            return base_queryset.filter(
                Q(created_by=user) | Q(assessment__institution=user)
            )
        elif user.role == "Student":
            return base_queryset.filter(
                assessment__due_date__lte=timezone.now(),
                assessment__course__enrolled_students=user
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
        
        # Check if assessment is past due
        if instance.assessment.due_date < timezone.now():
            raise ValidationError("Cannot modify questions for past-due assessments")
            
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Re-fetch instance to get updated data
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Check if assessment is past due
        if instance.assessment.due_date < timezone.now():
            raise ValidationError("Cannot delete questions from past-due assessments")
            
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GenerateMCQsFromTextView(generics.GenericAPIView):
    """
    View for generating MCQ questions from text context.
    POST /mcqQuestion/assessments/{assessment_id}/generate-from-text/
    
    Request body:
    {
        "context": "Your text content here...",
        "num_questions": 10,  // optional, default is 10
        "question_grade": "10.00"  // optional, default is 0.00
    }
    """
    parser_classes = (JSONParser,)
    serializer_class = McqQuestionSerializer

    def validate_num_questions(self, num_questions, default=10):
        try:
            num = int(num_questions) if num_questions is not None else default
            if num < 1:
                raise ValidationError("Number of questions must be positive")
            if num > 50:
                raise ValidationError("Maximum 50 questions allowed per request")
            return num
        except (TypeError, ValueError):
            raise ValidationError("Number of questions must be a valid integer")

    def validate_question_grade(self, question_grade):
        try:
            grade = Decimal(str(question_grade)) if question_grade is not None else Decimal('0.00')
            if grade < Decimal('0.00'):
                raise ValidationError("Question grade cannot be negative")
            if grade > Decimal('100.00'):
                raise ValidationError("Question grade cannot exceed 100")
            return grade
        except (TypeError, ValueError):
            raise ValidationError("Question grade must be a valid decimal number")

    def save_mcq_questions(self, mcq_data, question_grade):
        saved_questions = []
        for mcq in mcq_data:
            try:
                question = McqQuestion.objects.create(
                    question=mcq['question'],
                    answer=mcq['options'],
                    answer_key=mcq['correct_answer'],
                    created_by=self.request.user,
                    assessment_id=self.kwargs['assessment_id'],
                    question_grade=question_grade
                )
                saved_questions.append({
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.answer,
                    'answer': question.answer_key,
                    'question_grade': str(question.question_grade)
                })
            except Exception as e:
                # If any question fails, delete all previously saved questions
                McqQuestion.objects.filter(id__in=[q['id'] for q in saved_questions]).delete()
                raise ValidationError(f"Error saving question: {str(e)}")
        return saved_questions

    def post(self, request, *args, **kwargs):
        try:
            # Validate input
            if 'context' not in request.data:
                raise ValidationError({"context": "Text context is required"})
            
            context = request.data['context'].strip()
            if not context:
                raise ValidationError({"context": "Text context cannot be empty"})
            
            num_questions = self.validate_num_questions(request.data.get('num_questions'))
            question_grade = self.validate_question_grade(request.data.get('question_grade'))
            
            # Generate MCQs
            mcq_data = generate_mcqs_from_text(context, num_questions)
            
            # Save to database
            saved_questions = self.save_mcq_questions(mcq_data, question_grade)
            
            return Response({
                'message': f'Successfully generated and saved {len(saved_questions)} MCQ questions',
                'mcqs': saved_questions,
                'num_questions': len(saved_questions)
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                'error': str(e),
                'error_type': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e),
                'error_type': 'processing_error'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class GenerateMCQsFromPDFView(generics.GenericAPIView):
    """
    View for generating MCQ questions from PDF files.
    POST /mcqQuestion/assessments/{assessment_id}/generate-from-pdf/
    
    Request body (multipart/form-data):
    - pdf_file: PDF file to generate questions from (required)
    - num_questions: number of questions (optional, default=10)
    - question_grade: grade per question (optional, default=0.00)
    """
    parser_classes = (MultiPartParser,)
    serializer_class = McqQuestionSerializer

    def validate_num_questions(self, num_questions, default=10):
        try:
            num = int(num_questions) if num_questions is not None else default
            if num < 1:
                raise ValidationError("Number of questions must be positive")
            if num > 50:
                raise ValidationError("Maximum 50 questions allowed per request")
            return num
        except (TypeError, ValueError):
            raise ValidationError("Number of questions must be a valid integer")

    def validate_question_grade(self, question_grade):
        try:
            grade = Decimal(str(question_grade)) if question_grade is not None else Decimal('0.00')
            if grade < Decimal('0.00'):
                raise ValidationError("Question grade cannot be negative")
            if grade > Decimal('100.00'):
                raise ValidationError("Question grade cannot exceed 100")
            return grade
        except (TypeError, ValueError):
            raise ValidationError("Question grade must be a valid decimal number")

    def save_mcq_questions(self, mcq_data, question_grade):
        saved_questions = []
        for mcq in mcq_data:
            try:
                question = McqQuestion.objects.create(
                    question=mcq['question'],
                    answer=mcq['options'],
                    answer_key=mcq['correct_answer'],
                    created_by=self.request.user,
                    assessment_id=self.kwargs['assessment_id'],
                    question_grade=question_grade
                )
                saved_questions.append({
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.answer,
                    'answer': question.answer_key,
                    'question_grade': str(question.question_grade)
                })
            except Exception as e:
                # If any question fails, delete all previously saved questions
                McqQuestion.objects.filter(id__in=[q['id'] for q in saved_questions]).delete()
                raise ValidationError(f"Error saving question: {str(e)}")
        return saved_questions

    def post(self, request, *args, **kwargs):
        try:
            # Validate input
            if 'pdf_file' not in request.FILES:
                raise ValidationError({"pdf_file": "PDF file is required"})
            
            pdf_file = request.FILES['pdf_file']
            if not pdf_file.name.endswith('.pdf'):
                raise ValidationError({"pdf_file": "Only PDF files are allowed"})
            
            num_questions = self.validate_num_questions(request.data.get('num_questions'))
            question_grade = self.validate_question_grade(request.data.get('question_grade'))
            
            # Extract text from PDF
            context = extract_text_from_pdf(pdf_file)
            if not context:
                raise ValidationError({"pdf_file": "Could not extract text from PDF"})
            
            # Generate MCQs
            mcq_data = generate_mcqs_from_text(context, num_questions)
            
            # Save to database
            saved_questions = self.save_mcq_questions(mcq_data, question_grade)
            
            return Response({
                'message': f'Successfully generated and saved {len(saved_questions)} MCQ questions',
                'mcqs': saved_questions,
                'num_questions': len(saved_questions)
            }, status=status.HTTP_201_CREATED)

        except ValidationError as e:
            return Response({
                'error': e.detail if hasattr(e, 'detail') else str(e),
                'error_type': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e),
                'error_type': 'processing_error'
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


class McqQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = McqQuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'Institution':
            return McqQuestion.objects.all()
        elif user.role == 'Teacher':
            return McqQuestion.objects.filter(created_by=user)
        elif user.role == 'Student':
            # Get questions for courses the student is actively enrolled in
            return McqQuestion.objects.filter(
                assessment__course__enrollments__student=user,
                assessment__course__enrollments__is_active=True,
                assessment__start_date__lte=timezone.now(),
                assessment__due_date__gte=timezone.now()
            ).distinct()
        return McqQuestion.objects.none()

    @action(detail=False, methods=['get'])
    def get_available_assessments(self, request):
        """Get list of available assessments for the current student"""
        if request.user.role != 'Student':
            return Response(
                {"error": "This endpoint is only available for students"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get active assessments for enrolled courses
        assessments = Assessment.objects.filter(
            course__enrollments__student=request.user,
            course__enrollments__is_active=True,
            start_date__lte=timezone.now(),
            due_date__gte=timezone.now(),
            accepting_submissions=True
        ).distinct()

        # Get assessment details including question count and total possible score
        assessment_data = []
        for assessment in assessments:
            questions = McqQuestion.objects.filter(assessment=assessment)
            total_questions = questions.count()
            total_possible_score = questions.aggregate(
                total=Sum('question_grade')
            )['total'] or 0

            # Check if student has already submitted
            has_submitted = AssessmentScore.objects.filter(
                student=request.user,
                assessment=assessment
            ).exists()

            assessment_data.append({
                'id': assessment.id,
                'title': assessment.title,
                'description': assessment.description,
                'start_date': assessment.start_date,
                'due_date': assessment.due_date,
                'total_questions': total_questions,
                'total_possible_score': total_possible_score,
                'has_submitted': has_submitted
            })

        return Response(assessment_data)

    @action(detail=False, methods=['post'])
    def submit_answers(self, request):
        assessment_id = request.data.get('assessment_id')
        answers = request.data.get('answers', [])

        if not assessment_id or not answers:
            return Response(
                {"error": "Assessment ID and answers are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify student has access to this assessment
            assessment = Assessment.objects.get(
                id=assessment_id,
                course__enrollments__student=request.user,
                course__enrollments__is_active=True,
                start_date__lte=timezone.now(),
                due_date__gte=timezone.now(),
                accepting_submissions=True
            )

            with transaction.atomic():
                # Create or update AssessmentScore
                assessment_score = AssessmentScore.objects.update_or_create(
                    student=request.user,
                    assessment=assessment,
                    defaults={'total_score': 0}  # Will be updated by MCQQuestionScore
                )[0]

                # Close the assessment
                assessment.accepting_submissions = False
                assessment.save()

                return Response({
                    "message": "Assessment submitted successfully",
                    "assessment_id": assessment.id,
                    "total_score": assessment_score.total_score
                })

        except Assessment.DoesNotExist:
            return Response(
                {"error": "Assessment not found or not available"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def get_student_answers(self, request):
        assessment_id = request.query_params.get('assessment_id')
        if not assessment_id:
            return Response(
                {"error": "Assessment ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        answers = StudentMCQAnswer.objects.filter(
            student=request.user,
            question__assessment_id=assessment_id
        )
        serializer = StudentMCQAnswerSerializer(answers, many=True)
        return Response(serializer.data)


