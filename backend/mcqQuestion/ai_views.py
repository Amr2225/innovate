import logging
from decimal import Decimal
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from mcqQuestion.validation import validate_num_options, validate_difficulty, validate_num_questions, validate_question_grade

from .models import McqQuestion
from .serializers import McqQuestionSerializer
from .permission import McqQuestionPermission

from AI.generate_mcq_from_text import generate_mcqs_from_text
from AI.extract_text_from_pdf import extract_text_from_pdf
from AI.generate_mcqs_from_multiple_pdfs import generate_mcqs_from_multiple_pdfs

from .errors import MissingLectureError, InvalidLectureIdsError
from django.db.models import Q


logger = logging.getLogger(__name__)


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
    serializer_class = McqQuestionSerializer

    def save_mcq_questions(self, mcq_data, question_grade):
        saved_questions = []
        for mcq in mcq_data:
            try:
                logger.info(f"Processing MCQ: {mcq}")
                # Create question using serializer
                serializer = self.get_serializer(data={
                    'question': mcq['question'],
                    'options': mcq['options'],
                    'answer_key': mcq['correct_answer'],
                    'assessment': self.kwargs['assessment_id'],
                    'question_grade': question_grade,
                    'section_number': 1  # Default section number
                })

                # Log validation data
                logger.info(f"Serializer data: {serializer.initial_data}")

                # Validate the data
                if not serializer.is_valid():
                    logger.error(f"Validation errors: {serializer.errors}")
                    raise ValidationError(serializer.errors)

                # Save the question
                question = serializer.save(created_by=self.request.user)
                logger.info(
                    f"Successfully saved question with ID: {question.id}")

                # Add to saved questions list
                saved_questions.append({
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.options,
                    'answer': question.answer_key,
                    'question_grade': str(question.question_grade),
                    'section_number': question.section_number
                })
            except Exception as e:
                logger.error(f"Error saving question: {str(e)}")
                logger.error(f"Error type: {type(e)}")
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

        return saved_questions

    def post(self, request, *args, **kwargs):
        try:
            # Validate input
            if 'context' not in request.data:
                raise ValidationError({"context": "Text context is required"})

            context = request.data['context'].strip()
            if not context:
                raise ValidationError(
                    {"context": "Text context cannot be empty"})

            num_questions = validate_num_questions(
                request.data.get('num_questions'))
            question_grade = validate_question_grade(
                request.data.get('question_grade'))

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

    def save_mcq_questions(self, mcq_data, question_grade):
        saved_questions = []
        for mcq in mcq_data:
            try:
                question = McqQuestion.objects.create(
                    question=mcq['question'],
                    options=mcq['options'],
                    answer_key=mcq['correct_answer'],
                    created_by=self.request.user,
                    assessment_id=self.kwargs['assessment_id'],
                    question_grade=question_grade,
                    section_number=1  # Add default section number
                )
                saved_questions.append({
                    'id': str(question.id),
                    'question': question.question,
                    'options': question.options,
                    'answer': question.answer_key,
                    'question_grade': str(question.question_grade),
                    'section_number': question.section_number  # Include section number in response
                })
            except Exception as e:
                # If any question fails, delete all previously saved questions
                McqQuestion.objects.filter(
                    id__in=[q['id'] for q in saved_questions]).delete()
                raise ValidationError(f"Error saving question: {str(e)}")
        return saved_questions

    def post(self, request, *args, **kwargs):
        try:
            # Validate input
            if 'pdf_file' not in request.FILES:
                raise ValidationError({"pdf_file": "PDF file is required"})

            pdf_file = request.FILES['pdf_file']
            if not pdf_file.name.endswith('.pdf'):
                raise ValidationError(
                    {"pdf_file": "Only PDF files are allowed"})

            num_questions = validate_num_questions(
                request.data.get('num_questions'))
            question_grade = validate_question_grade(
                request.data.get('question_grade'))

            # Extract text from PDF
            context = extract_text_from_pdf(pdf_file)
            if not context:
                raise ValidationError(
                    {"pdf_file": "Could not extract text from PDF"})

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


class GenerateMCQsFromLecturesView(generics.GenericAPIView):
    """
    View for generating MCQ questions from multiple lecture attachments.
    POST /mcqQuestion/generate-from-lectures/

    Request body (JSON):
    {
        "lecture_ids": ["uuid1", "uuid2", ...],  // List of lecture IDs
        "num_questions_per_lecture": 10,  // optional, default=10
        "question_grade": "2.00",  // optional, default=0.00
        "section_number": 1,  // optional, default=1
        "difficulty": "3",  // optional, default="3" (1=Very Easy, 2=Easy, 3=Medium, 4=Hard, 5=Very Hard)
        "num_options": 4  // optional, default=4 (number of options per question, min=2, max=4)
    }
    """
    serializer_class = McqQuestionSerializer
    permission_classes = [McqQuestionPermission]

    DIFFICULTY_CHOICES = [
        ('1', 'Very Easy'),
        ('2', 'Easy'),
        ('3', 'Medium'),
        ('4', 'Hard'),
        ('5', 'Very Hard')
    ]

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

    def post(self, request, *args, **kwargs):
        try:
            logger.info("Starting MCQ generation from lectures (no save)")

            # Validate input
            if 'lecture_ids' not in request.data:
                raise MissingLectureError()

            lecture_ids = request.data['lecture_ids']
            if not isinstance(lecture_ids, list) or not lecture_ids:
                raise InvalidLectureIdsError()

            # Get lectures and validate attachments
            from lecture.models import Lecture
            lectures = Lecture.objects.filter(id__in=lecture_ids)

            if lectures.count() != len(lecture_ids):
                raise InvalidLectureIdsError()

            logger.info(f"Processing {len(lectures)} lectures")
            number_of_questions = validate_num_questions(
                request.data.get('number_of_questions'))

            # Validate and get difficulty
            difficulty = validate_difficulty(
                request.data.get('difficulty'), self.DIFFICULTY_CHOICES)

            # Validate and get number of options
            num_options = validate_num_options(
                request.data.get('num_options'))

            # Generate MCQs (no save)
            mcq_data = generate_mcqs_from_multiple_pdfs(
                [lecture.attachment for lecture in lectures],
                # Evenly distribute the number of questions per pdf
                number_of_questions=number_of_questions // len(
                    lectures),
                difficulty=difficulty,  # Pass difficulty to the generation function
                num_options=num_options  # Pass number of options to the generation function
            )
            logger.info(f"Generated {len(mcq_data)} MCQs (not saved)")

            # Return generated MCQs
            return Response({
                'message': f'Successfully generated {len(mcq_data)} MCQ questions from {len(lectures)} lectures',
                'mcqs': mcq_data,
                'num_questions': len(mcq_data),
                'num_lectures': len(lectures),
                'difficulty': dict(self.DIFFICULTY_CHOICES)[difficulty],
                'num_options': num_options
            }, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return Response({
                'error': e.detail if hasattr(e, 'detail') else str(e),
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
