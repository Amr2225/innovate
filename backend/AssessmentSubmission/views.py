from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import AssessmentSubmission
from .serializers import AssessmentSubmissionSerializer
from assessment.models import Assessment
from enrollments.models import Enrollments
from mcqQuestion.models import McqQuestion
from HandwrittenQuestion.models import HandwrittenQuestion, HandwrittenQuestionScore
from django.conf import settings
import os

class AssessmentSubmissionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow all authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only students can submit
        return request.user.role == "Student"
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Students can only access their own submissions
        if request.user.role == "Student":
            return obj.enrollment.user == request.user
        
        # Teachers can access submissions for their courses
        if request.user.role == "Teacher":
            return obj.assessment.course.teacher == request.user.teacher
        
        # Institutions can access submissions for their courses
        if request.user.role == "Institution":
            return obj.assessment.course.institution == request.user.institution
        
        return False

class AssessmentSubmissionAPIView(generics.CreateAPIView):
    """View to submit all answers for an assessment"""
    serializer_class = AssessmentSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentSubmissionPermission]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request, *args, **kwargs):
        """Get all students' answers for an assessment"""
        try:
            assessment_id = kwargs.get('pk')
            assessment = Assessment.objects.get(id=assessment_id)
            user = request.user

            # Check permissions
            if user.role == "Student":
                # Students can only view their own submissions
                is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
                try:
                    enrollment = Enrollments.objects.get(
                        user=user,
                        course=assessment.course,
                        is_completed=is_completed
                    )
                    submissions = AssessmentSubmission.objects.filter(
                        assessment=assessment,
                        enrollment=enrollment
                    )
                except Enrollments.DoesNotExist:
                    return Response(
                        {"detail": "You are not enrolled in this course"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif user.role == "Teacher":
                # Teachers can view submissions for courses they teach
                if not assessment.course.teacher == user.teacher:
                    return Response(
                        {"detail": "You don't have permission to view these submissions"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                submissions = AssessmentSubmission.objects.filter(assessment=assessment)
            elif user.role == "Institution":
                # Institution can view all submissions for their courses
                if assessment.course.institution != user.institution:
                    return Response(
                        {"detail": "You don't have permission to view these submissions"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                submissions = AssessmentSubmission.objects.filter(assessment=assessment)
            else:
                return Response(
                    {"detail": "You don't have permission to view these submissions"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get all questions based on user role
            if user.role == "Student":
                # For students, get their own MCQ questions and all handwritten questions
                mcq_questions = assessment.mcq_questions.filter(
                    assessment=assessment,
                    
                )
                handwritten_questions = assessment.handwritten_questions.filter(
                    assessment=assessment
                )
            else:
                # For teachers and institutions, get all questions
                mcq_questions = assessment.mcq_questions.filter(assessment=assessment)
                handwritten_questions = assessment.handwritten_questions.filter(assessment=assessment)

            # Prepare response data
            response_data = {
                'assessment_id': str(assessment.id),
                'assessment_title': assessment.title,
                'total_submissions': submissions.count(),
                'questions': []
            }

            # Process each submission
            for submission in submissions:
                # Get MCQ answers for this submission
                mcq_answers = submission.mcq_answers
                
                # Add MCQ questions with their answers
                for question in mcq_questions:
                    question_data = {
                        'id': str(question.id),
                        'question': question.question,
                        'options': question.options,
                        'answer_key': question.answer_key,
                        'question_grade': str(question.question_grade)
                    }
                    
                    # Add student's answer if available
                    if str(question.id) in mcq_answers:
                        answer = mcq_answers[str(question.id)]
                        question_data.update({
                            'selected_answer': answer,
                            'is_correct': answer == question.answer_key
                        })
                    
                    response_data['questions'].append(question_data)

                # Add Handwritten questions with their answers
                for question in handwritten_questions:
                    question_data = {
                        'id': str(question.id),
                        'question': question.question_text,
                        'answer_key': question.answer_key,
                        'max_grade': str(question.max_grade)
                    }
                    
                    # Add student's answer if available
                    if str(question.id) in submission.handwritten_answers:
                        try:
                            score = HandwrittenQuestionScore.objects.get(
                                question=question,
                                enrollment=submission.enrollment
                            )
                            question_data.update({
                                'image_url': request.build_absolute_uri(score.answer_image.url) if score.answer_image else None,
                                'extracted_text': score.extracted_text,
                                'feedback': score.feedback,
                                'score': str(score.score)
                            })
                        except HandwrittenQuestionScore.DoesNotExist:
                            pass
                    
                    # Always append the question data, regardless of whether it has been answered
                    response_data['questions'].append(question_data)

            return Response(response_data)

        except Assessment.DoesNotExist:
            return Response(
                {"detail": "Assessment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        try:
            # Get assessment ID from URL
            assessment_id = kwargs.get('pk')
            if not assessment_id:
                return Response(
                    {"detail": "Assessment ID is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                assessment = Assessment.objects.get(id=assessment_id)
                print(f"Found assessment: {assessment.title}")
            except Assessment.DoesNotExist:
                return Response(
                    {"detail": "Assessment not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the enrollment
            is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
            try:
                enrollment = Enrollments.objects.get(
                    user=request.user,
                    course=assessment.course,
                    is_completed=is_completed
                )
                print(f"Found enrollment for user: {request.user.email}")
            except Enrollments.DoesNotExist:
                return Response(
                    {"detail": "You are not enrolled in this course"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create submission
            submission = AssessmentSubmission.get_or_create_submission(assessment, enrollment)
            print(f"Got/Created submission: {submission.id}")

            # Check if already submitted
            if submission.is_submitted:
                return Response(
                    {"detail": "You have already submitted this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Initialize answers dictionaries
            mcq_answers = {}
            handwritten_answers = {}

            # Get all questions for the assessment
            mcq_questions = McqQuestion.objects.filter(assessment=assessment)
            handwritten_questions = HandwrittenQuestion.objects.filter(assessment=assessment)

            # Log the number of questions found
            print(f"Found {mcq_questions.count()} MCQ questions and {handwritten_questions.count()} handwritten questions")

            # Check if there are any questions at all
            if not mcq_questions.exists() and not handwritten_questions.exists():
                print("No questions found for assessment")
                return Response(
                    {"detail": "No questions found for this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process MCQ answers if provided
            mcq_data = request.data.get('mcq_answers')
            if mcq_data is not None and mcq_questions.exists():
                print(f"Processing MCQ answers: {mcq_data}")
                # Get question details for better error messages
                question_details = {
                    str(q.id): {
                        'question': q.question,
                        'options': q.options,
                        'answer_key': q.answer_key,
                        'question_grade': str(q.question_grade)
                    } for q in mcq_questions
                }
                question_ids = list(question_details.keys())

                if isinstance(mcq_data, str):
                    import json
                    try:
                        mcq_data = json.loads(mcq_data)
                    except json.JSONDecodeError:
                        return Response(
                            {"detail": "Invalid MCQ answers format"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                if not isinstance(mcq_data, dict):
                    return Response(
                        {"detail": "MCQ answers must be a dictionary"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validate MCQ answers
                for question_id, answer in mcq_data.items():
                    if question_id not in question_details:
                        return Response(
                            {
                                "detail": f"Invalid question ID: {question_id}",
                                "valid_questions": question_details
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    if answer not in question_details[question_id]['options']:
                        return Response(
                            {
                                "detail": f"Invalid answer for question {question_id}",
                                "question": question_details[question_id],
                                "provided_answer": answer
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    
                    mcq_answers[question_id] = answer

            # Process Handwritten answers
            print(f"Processing files: {list(request.FILES.keys())}")
            for question_id, image in request.FILES.items():
                if question_id.startswith('handwritten_'):
                    question_id = question_id.replace('handwritten_', '')
                    print(f"Processing handwritten question: {question_id}")
                    # Verify the question exists
                    try:
                        question = HandwrittenQuestion.objects.get(
                            id=question_id,
                            assessment=assessment
                        )
                        print(f"Found handwritten question: {question.question_text[:50]}...")
                    except HandwrittenQuestion.DoesNotExist:
                        print(f"Handwritten question not found: {question_id}")
                        return Response(
                            {"detail": f"Invalid handwritten question ID: {question_id}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    try:
                        # Now evaluate the answer using AI
                        from main.AI import evaluate_handwritten_answer
                        from django.core.files.base import ContentFile
                        import io
                        from PIL import Image as PILImage
                        import tempfile
                        import os

                        # Ensure we have a proper file object
                        if not hasattr(image, 'read'):
                            # If it's not a file object, create one
                            image_content = image.read()
                            image = ContentFile(image_content, name=image.name)
                        
                        # Reset file pointer to beginning
                        image.seek(0)
                        
                        # Open and process the image
                        pil_image = PILImage.open(image)
                        if pil_image.mode != 'RGB':
                            pil_image = pil_image.convert('RGB')
                        
                        # Create a temporary file
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_file:
                            # Save the image to the temporary file
                            pil_image.save(temp_file, format='JPEG', quality=95)
                            temp_file_path = temp_file.name
                        
                        try:
                            # Create a file-like object with both read and path attributes
                            class FileWithPath:
                                def __init__(self, path):
                                    self.path = path
                                    self._file = open(path, 'rb')
                                
                                def read(self, size=-1):
                                    return self._file.read(size)
                                
                                def seek(self, pos):
                                    self._file.seek(pos)
                                
                                def close(self):
                                    if hasattr(self._file, 'close'):
                                        self._file.close()
                            
                            # Create the file object
                            file_obj = FileWithPath(temp_file_path)
                            
                            try:
                                # Evaluate the answer using the file object
                                score, feedback, extracted_text = evaluate_handwritten_answer(
                                    question=question.question_text,
                                    answer_key=question.answer_key,
                                    student_answer_image=file_obj,
                                    max_grade=float(question.max_grade)
                                )
                                print(f"AI evaluation completed. Score: {score}")
                            finally:
                                # Ensure the file is closed
                                file_obj.close()
                        finally:
                            # Clean up the temporary file
                            try:
                                if os.path.exists(temp_file_path):
                                    os.unlink(temp_file_path)
                            except Exception as e:
                                # Log the error but don't fail the request
                                print(f"Warning: Failed to delete temporary file {temp_file_path}: {str(e)}")
                        
                        # Reset file pointer again for saving
                        image.seek(0)

                        # Create or update the score record
                        score_obj, created = HandwrittenQuestionScore.objects.update_or_create(
                            question=question,
                            enrollment=enrollment,
                            defaults={
                                'answer_image': image,
                                'score': score,
                                'feedback': feedback,
                                'extracted_text': extracted_text
                            }
                        )
                        print(f"Created/Updated score record: {score_obj.id}")

                        # Store only the relative path in handwritten_answers
                        relative_path = os.path.relpath(score_obj.answer_image.path, settings.MEDIA_ROOT)
                        handwritten_answers[str(question_id)] = relative_path
                    except Exception as e:
                        print(f"Error processing handwritten answer: {str(e)}")
                        return Response(
                            {"detail": f"Error evaluating handwritten answer: {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

            # Check if at least one type of answer is provided
            if not mcq_answers and not handwritten_answers:
                print("No answers provided")
                return Response(
                    {"detail": "At least one answer (MCQ or handwritten) must be provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update submission
            with transaction.atomic():
                if mcq_answers:
                    submission.mcq_answers = mcq_answers
                if handwritten_answers:
                    submission.handwritten_answers = handwritten_answers
                submission.is_submitted = True
                submission.save()
                print(f"Updated submission with answers. MCQ: {len(mcq_answers)}, Handwritten: {len(handwritten_answers)}")

            # Return success message with details
            response_data = {
                "message": "Assessment submitted successfully",
                "submission_details": {
                    "mcq_answers_count": len(mcq_answers) if mcq_answers else 0,
                    "handwritten_answers_count": len(handwritten_answers) if handwritten_answers else 0
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error in create method: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
