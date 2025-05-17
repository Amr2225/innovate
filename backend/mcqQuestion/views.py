from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
from django.db.models import Q, Sum, Count
from .models import McqQuestion
from .serializers import McqQuestionSerializer
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.exceptions import ValidationError as DjangoValidationError
from main.AI import generate_mcqs_from_text, extract_text_from_pdf
from decimal import Decimal
from assessment.models import AssessmentScore, Assessment
from django.db import transaction
from users.permissions import isInstitution, isTeacher, isStudent


class McqQuestionPermission(permissions.BasePermission):
    """Custom permission class for MCQ questions"""
    
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
            raise PermissionDenied("You don't have permission to add questions to this assessment")
        elif user.role == "Teacher" and not assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to add questions to this assessment")
            
        # Validate assessment status
        if assessment.due_date < timezone.now():
            raise ValidationError("Cannot add questions to past-due assessments")
            
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
        base_queryset = McqQuestion.objects.select_related('assessment', 'created_by')

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
            raise ValidationError("Cannot modify questions for past-due assessments")
            
        # Validate answer format
        if 'answer' in request.data:
            if not isinstance(request.data['answer'], list):
                raise ValidationError({"answer": "Answer must be a list of options"})
            if len(request.data['answer']) < 2:
                raise ValidationError({"answer": "At least 2 options are required"})
                
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Validate assessment status
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
    permission_classes = [McqQuestionPermission]

    def get_queryset(self):
        user = self.request.user
        base_queryset = McqQuestion.objects.select_related('assessment', 'created_by')

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

    @action(detail=False, methods=['get'])
    def get_available_assessments(self, request):
        user = request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can access this endpoint")
            
        assessments = Assessment.objects.filter(
            course__enrollments__user=user,
            due_date__gt=timezone.now()
        ).select_related('course')
        
        return Response([{
            'id': str(assessment.id),
            'title': assessment.title,
            'course': assessment.course.name,
            'due_date': assessment.due_date,
            'total_questions': assessment.mcq_questions.count()
        } for assessment in assessments])

    @action(detail=False, methods=['post'])
    def submit_answers(self, request):
        user = request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit answers")
            
        answers = request.data.get('answers', [])
        if not isinstance(answers, list):
            raise ValidationError({"answers": "Answers must be a list"})
            
        results = []
        with transaction.atomic():
            for answer in answers:
                question_id = answer.get('question_id')
                selected_answer = answer.get('selected_answer')
                
                if not question_id or not selected_answer:
                    raise ValidationError("Each answer must include question_id and selected_answer")
                    
                try:
                    question = McqQuestion.objects.get(
                        id=question_id,
                        assessment__course__enrollments__user=user
                    )
                except McqQuestion.DoesNotExist:
                    raise ValidationError(f"Question {question_id} not found or not accessible")
                    
                # Create or update score
                score, created = MCQQuestionScore.objects.update_or_create(
                    question=question,
                    student=user,
                    defaults={
                        'selected_answer': selected_answer,
                        'is_correct': selected_answer == question.answer_key,
                        'score': question.question_grade if selected_answer == question.answer_key else 0
                    }
                )
                
                results.append({
                    'question_id': str(question_id),
                    'is_correct': score.is_correct,
                    'score': str(score.score)
                })
                
        return Response({
            'message': 'Answers submitted successfully',
            'results': results
        })

    @action(detail=False, methods=['get'])
    def get_student_answers(self, request):
        user = request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can access this endpoint")
            
        assessment_id = request.query_params.get('assessment_id')
        if not assessment_id:
            raise ValidationError("assessment_id is required")
            
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            raise ValidationError("Assessment not found")
            
        # Validate course ownership
        if user.role == "Institution" and assessment.course.institution != user:
            raise PermissionDenied("You don't have permission to view answers for this assessment")
        elif user.role == "Teacher" and not assessment.course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You don't have permission to view answers for this assessment")
            
        scores = MCQQuestionScore.objects.filter(
            question__assessment=assessment
        ).select_related('student', 'question')
        
        results = {}
        for score in scores:
            if score.student.id not in results:
                results[score.student.id] = {
                    'student': {
                        'id': str(score.student.id),
                        'email': score.student.email,
                        'name': f"{score.student.first_name} {score.student.last_name}"
                    },
                    'answers': []
                }
            results[score.student.id]['answers'].append({
                'question_id': str(score.question.id),
                'selected_answer': score.selected_answer,
                'is_correct': score.is_correct,
                'score': str(score.score)
            })
            
        return Response(list(results.values()))


