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
from django.apps import apps

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

class AssessmentSubmissionAPIView(generics.GenericAPIView):
    """View to submit all answers for an assessment"""
    permission_classes = [permissions.IsAuthenticated, AssessmentSubmissionPermission]
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    serializer_class = AssessmentSubmissionSerializer

    def post(self, request, *args, **kwargs):
        """Handle POST requests by calling the create method"""
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """Get all students' answers for an assessment"""
        try:
            assessment_id = kwargs.get('pk')
            assessment = Assessment.objects.get(id=assessment_id)
            
            # Get all submissions for this assessment
            submissions = AssessmentSubmission.objects.filter(assessment=assessment)
            
            # Get all questions
            mcq_questions = McqQuestion.objects.filter(assessment=assessment)
            handwritten_questions = HandwrittenQuestion.objects.filter(assessment=assessment)
            DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
            dynamic_questions = DynamicMCQQuestions.objects.filter(
                dynamic_mcq__assessment=assessment,
                created_by=request.user
            )
            
            response_data = {
                'assessment_id': str(assessment.id),
                'assessment_title': assessment.title,
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
                        'type': 'mcq',
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

                # Add Dynamic MCQ questions with their answers
                for question in dynamic_questions:
                    question_data = {
                        'id': str(question.id),
                        'type': 'dynamic_mcq',
                        'question': question.question,
                        'options': question.options,
                        'answer_key': question.answer_key,
                        'question_grade': str(question.question_grade),
                        'difficulty': question.difficulty
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
                        'type': 'handwritten',
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
            DynamicMCQ = apps.get_model('DynamicMCQ', 'DynamicMCQ')
            DynamicMCQQuestions = apps.get_model('DynamicMCQ', 'DynamicMCQQuestions')
            
            # Get dynamic questions through DynamicMCQ
            dynamic_mcq = DynamicMCQ.objects.filter(assessment=assessment).first()
            print(f"Found DynamicMCQ: {dynamic_mcq}")
            
            if dynamic_mcq:
                print(f"DynamicMCQ details - ID: {dynamic_mcq.id}, Assessment: {dynamic_mcq.assessment.title}")
                dynamic_questions = DynamicMCQQuestions.objects.filter(
                    dynamic_mcq=dynamic_mcq,
                    created_by=request.user
                )
                print(f"Found {dynamic_questions.count()} dynamic questions for user {request.user.email}")
                for q in dynamic_questions:
                    print(f"Question ID: {q.id}, Question: {q.question[:50]}...")
            else:
                print("No DynamicMCQ found for this assessment")
                dynamic_questions = DynamicMCQQuestions.objects.none()

            # Log the number of questions found
            print(f"Found {mcq_questions.count()} MCQ questions, {dynamic_questions.count()} dynamic MCQ questions, and {handwritten_questions.count()} handwritten questions")

            # Check if there are any questions at all
            if not mcq_questions.exists() and not dynamic_questions.exists() and not handwritten_questions.exists():
                print("No questions found for assessment")
                # Try to generate questions if they don't exist
                try:
                    questions = assessment.get_all_questions_for_student(request.user)
                    print(f"Generated questions: {questions}")
                    if questions['dynamic_mcq'] or questions['mcq'] or questions['handwritten']:
                        # Questions were generated, try to get them again
                        dynamic_mcq = DynamicMCQ.objects.filter(assessment=assessment).first()
                        if dynamic_mcq:
                            dynamic_questions = DynamicMCQQuestions.objects.filter(
                                dynamic_mcq=dynamic_mcq,
                                created_by=request.user
                            )
                            if dynamic_questions.exists():
                                print(f"Found {dynamic_questions.count()} questions after generation")
                                return self.create(request, *args, **kwargs)
                except Exception as e:
                    print(f"Error generating questions: {str(e)}")
                
                return Response(
                    {"detail": "No questions found for this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process MCQ answers if provided
            mcq_data = request.data.get('mcq_answers')
            if mcq_data is not None and (mcq_questions.exists() or dynamic_questions.exists()):
                print(f"Processing MCQ answers: {mcq_data}")
                # Get question details for better error messages
                question_details = {
                    str(q.id): {
                        'question': q.question,
                        'options': q.options,
                        'answer_key': q.answer_key,
                        'question_grade': str(q.question_grade)
                    } for q in list(mcq_questions) + list(dynamic_questions)
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
            handwritten_data = request.data.get('handwritten_answers', {})
            if isinstance(handwritten_data, str):
                try:
                    handwritten_data = json.loads(handwritten_data)
                except json.JSONDecodeError:
                    return Response(
                        {"detail": "Invalid handwritten answers format"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            if not isinstance(handwritten_data, dict):
                return Response(
                    {"detail": "Handwritten answers must be a dictionary"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process each handwritten answer
            for question_id, image_file in request.FILES.items():
                if question_id in handwritten_data:
                    try:
                        question = HandwrittenQuestion.objects.get(id=question_id)
                    except HandwrittenQuestion.DoesNotExist:
                        return Response(
                            {"detail": f"Handwritten question {question_id} not found"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Save the image file
                    file_path = os.path.join(
                        'handwritten_answers',
                        str(assessment.id),
                        str(enrollment.id),
                        f"{question_id}_{image_file.name}"
                    )
                    full_path = os.path.join(settings.MEDIA_ROOT, file_path)
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    with open(full_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    
                    handwritten_answers[question_id] = file_path

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
