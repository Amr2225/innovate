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
from DynamicMCQ.models import DynamicMCQQuestions
from MCQQuestionScore.models import MCQQuestionScore
from Code_Questions.models import CodingQuestion
from django.conf import settings
import os
import json

class AssessmentSubmissionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(f"Checking permission for user: {request.user.email}, role: {request.user.role}")
        if not request.user.is_authenticated:
            print("User is not authenticated")
            return False
        
        # Allow all authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            print("Safe method, allowing access")
            return True
        
        # Only students can submit
        is_student = request.user.role == "Student"
        print(f"Is student: {is_student}")
        return is_student
    
    def has_object_permission(self, request, view, obj):
        print(f"Checking object permission for user: {request.user.email}, role: {request.user.role}")
        if not request.user.is_authenticated:
            print("User is not authenticated")
            return False
        
        # Students can only access their own submissions
        if request.user.role == "Student":
            is_owner = obj.enrollment.user == request.user
            print(f"Is owner: {is_owner}")
            return is_owner
        
        # Teachers can access submissions for their courses
        if request.user.role == "Teacher":
            is_teacher = obj.assessment.course.teacher == request.user.teacher
            print(f"Is teacher: {is_teacher}")
            return is_teacher
        
        # Institutions can access submissions for their courses
        if request.user.role == "Institution":
            is_institution = obj.assessment.course.institution == request.user.institution
            print(f"Is institution: {is_institution}")
            return is_institution
        
        print("No matching role found")
        return False

class AssessmentSubmissionAPIView(generics.CreateAPIView):
    """
    API endpoint to submit an assessment.

    This endpoint allows students to submit their answers for an assessment,
    including MCQ answers and handwritten answer images.

    POST /api/assessments/{assessment_id}/submit/

    Parameters:
    - assessment_id (UUID): The ID of the assessment
    - mcq_answers (JSON): Dictionary mapping question IDs to selected answers
    - handwritten_{question_id} (File): Image file for handwritten answers

    Example Request:
    ```json
    {
        "mcq_answers": {
            "question_id_1": "selected_option",
            "question_id_2": "selected_option"
        }
    }
    ```
    And form data for handwritten answers:
    ```
    handwritten_question_id_1: [image_file]
    handwritten_question_id_2: [image_file]
    ```

    Returns:
    ```json
    {
        "id": "uuid",
        "assessment": "uuid",
        "enrollment": "uuid",
        "student_email": "string",
        "assessment_title": "string",
        "course_name": "string",
        "mcq_answers": {
            "question_id": "selected_option"
        },
        "handwritten_answers": {
            "question_id": "file_url"
        },
        "submitted_at": "datetime",
        "is_submitted": "boolean"
    }
    ```

    Status Codes:
    - 201: Successfully submitted assessment
    - 400: Invalid submission data or assessment not accepting submissions
    - 403: Not authorized to submit assessment
    - 404: Assessment not found

    Permissions:
    - Students: Can submit assessments for courses they're enrolled in
    - Teachers/Institutions: Cannot submit assessments

    Notes:
    - All questions must be answered
    - MCQ answers must be one of the provided options
    - Handwritten answers must be valid image files (JPEG, PNG, GIF, BMP)
    - Assessment must be accepting submissions
    - Student must be enrolled in the course
    """
    serializer_class = AssessmentSubmissionSerializer
    permission_classes = [AssessmentSubmissionPermission]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request, *args, **kwargs):
        """
        Retrieve submitted answers and scores for an assessment.

        This endpoint returns:
        - All questions in the assessment
        - Student's selected answers
        - Scores for each question
        - Total score and percentage

        The response includes both MCQ and handwritten questions with their respective scores.
        """
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
                mcq_questions = assessment.mcq_questions.filter(assessment=assessment)
                dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(
                    dynamic_mcq__assessment=assessment,
                    created_by=user
                )
                handwritten_questions = assessment.handwritten_questions.filter(assessment=assessment)
                coding_questions = assessment.coding_questions.filter(assessment_Id=assessment)
            else:
                # For teachers and institutions, get all questions
                mcq_questions = assessment.mcq_questions.filter(assessment=assessment)
                dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(dynamic_mcq__assessment=assessment)
                handwritten_questions = assessment.handwritten_questions.filter(assessment=assessment)
                coding_questions = assessment.coding_questions.filter(assessment_Id=assessment)

            # Prepare response data
            response_data = {
                'assessment_id': str(assessment.id),
                'assessment_title': assessment.title,
                'total_submissions': submissions.count(),
                'questions': [],
                'total_score': 0,
                'max_score': 0
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
                        # Get the score for this question
                        try:
                            score = MCQQuestionScore.objects.get(
                                question=question,
                                enrollment=submission.enrollment
                            )
                            question_data.update({
                                'selected_answer': answer,
                                'is_correct': answer == question.answer_key,
                                'score': str(score.score),
                                'max_score': str(question.question_grade)
                            })
                            response_data['total_score'] += float(score.score)
                        except MCQQuestionScore.DoesNotExist:
                            question_data.update({
                                'selected_answer': answer,
                                'is_correct': answer == question.answer_key,
                                'score': '0',
                                'max_score': str(question.question_grade)
                            })
                    
                    response_data['max_score'] += float(question.question_grade)
                    response_data['questions'].append(question_data)

                # Add Dynamic MCQ questions with their answers
                for question in dynamic_mcq_questions:
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
                        # Get the score for this question
                        try:
                            score = MCQQuestionScore.objects.get(
                                dynamic_question=question,
                                enrollment=submission.enrollment
                            )
                            question_data.update({
                                'selected_answer': answer,
                                'is_correct': answer == question.answer_key,
                                'score': str(score.score),
                                'max_score': str(question.question_grade)
                            })
                            response_data['total_score'] += float(score.score)
                        except MCQQuestionScore.DoesNotExist:
                            question_data.update({
                                'selected_answer': answer,
                                'is_correct': answer == question.answer_key,
                                'score': '0',
                                'max_score': str(question.question_grade)
                            })
                    
                    response_data['max_score'] += float(question.question_grade)
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
                                'score': str(score.score),
                                'max_score': str(question.max_grade)
                            })
                            response_data['total_score'] += float(score.score)
                        except HandwrittenQuestionScore.DoesNotExist:
                            pass
                    
                    response_data['max_score'] += float(question.max_grade)
                    response_data['questions'].append(question_data)

                # Add Coding questions with their answers
                for question in coding_questions:
                    question_data = {
                        'id': str(question.id),
                        'question': question.description,
                        'max_grade': str(question.max_grade),
                        'test_cases_expected_output': question.test_cases_expected_output,
                        'test_cases_input_data': question.test_cases_input_data
                    }
                    
                    # Add student's answer if available
                    if str(question.id) in submission.codequestions_answers:
                        question_data.update({
                            'code_answer': submission.codequestions_answers[str(question.id)]
                        })
                    response_data['total_score'] += float(question.max_grade)
                    response_data['questions'].append(question_data)

            # Calculate percentage score
            if response_data['max_score'] > 0:
                response_data['percentage_score'] = f"{(response_data['total_score'] / response_data['max_score']) * 100:.2f} %"
            else:
                response_data['percentage_score'] = "0 %"

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
        """
        Submit answers for an assessment.

        This endpoint allows students to submit their answers for an assessment.
        It handles both MCQ and handwritten answers.

        The submission process:
        1. Validates the assessment exists and is accepting submissions
        2. Checks student enrollment
        3. Validates answers against questions
        4. Creates scores for each answer
        5. Updates the submission status

        Returns:
        - 201: Assessment submitted successfully
        - 400: Invalid input data
        - 403: Not authorized to submit
        - 404: Assessment not found
        """
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
                print(f"Assessment accepting submissions: {assessment.accepting_submissions}")
                print(f"Assessment due date: {assessment.due_date}")
            except Assessment.DoesNotExist:
                return Response(
                    {"detail": "Assessment not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the enrollment
            try:
                enrollment = Enrollments.objects.get(
                    user=request.user,
                    course=assessment.course
                )
                print(f"Found enrollment for user: {request.user.email}")
                print(f"Enrollment details: user={enrollment.user.email}, course={enrollment.course.name}, is_completed={enrollment.is_completed}")
            except Enrollments.DoesNotExist:
                print(f"No enrollment found for user {request.user.email} in course {assessment.course.name}")
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
            coding_answers = {}
            # Get all questions for the assessment
            mcq_questions = McqQuestion.objects.filter(assessment=assessment)
            dynamic_mcq_questions = DynamicMCQQuestions.objects.filter(
                dynamic_mcq__assessment=assessment,
                created_by=request.user
            )
            handwritten_questions = HandwrittenQuestion.objects.filter(assessment=assessment)
            coding_questions = CodingQuestion.objects.filter(assessment_Id=assessment)

            # Log the number of questions found
            print(f"Found {mcq_questions.count()} MCQ questions, {dynamic_mcq_questions.count()} dynamic MCQ questions, {handwritten_questions.count()} handwritten questions, and {coding_questions.count()} coding questions")
            print("Type mcq_questions:", type(mcq_questions))
            print("Type dynamic_mcq_questions:", type(dynamic_mcq_questions))
            print("Type handwritten_questions:", type(handwritten_questions))
            print("Type coding_questions:", type(coding_questions))
            # Check if there are any questions at all
            print("Final counts before error:",
                  mcq_questions.count(),
                  dynamic_mcq_questions.count(),
                  handwritten_questions.count(),
                  coding_questions.count())

            if not (mcq_questions.exists() or dynamic_mcq_questions.exists() or handwritten_questions.exists() or coding_questions.exists()):
                print("No questions found for assessment")
                return Response(
                    {"detail": "No questions found for this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Process MCQ answers if provided
            mcq_data = request.data.get('mcq_answers')
            print(f"Received MCQ data: {mcq_data}")
            if mcq_data is not None and (mcq_questions.exists() or dynamic_mcq_questions.exists()):
                print(f"Processing MCQ answers: {mcq_data}")
                # Get question details for better error messages
                question_details = {}
                
                # Add regular MCQ questions
                for q in mcq_questions:
                    question_details[str(q.id)] = {
                        'question': q.question,
                        'options': q.options,
                        'answer_key': q.answer_key,
                        'question_grade': str(q.question_grade)
                    }
                
                # Add dynamic MCQ questions
                for q in dynamic_mcq_questions:
                    question_details[str(q.id)] = {
                        'question': q.question,
                        'options': q.options,
                        'answer_key': q.answer_key,
                        'question_grade': str(q.question_grade)
                    }

                if isinstance(mcq_data, str):
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

            # Process Coding answers
            coding_data = request.data.get('codequestions_answers')
            print(f"Received Coding data: {coding_data}")
            if isinstance(coding_data, str):
                try:
                    coding_data = json.loads(coding_data)
                except Exception:
                    return Response(
                        {"detail": "codequestions_answers must be a valid JSON object"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if coding_data is not None and coding_questions.exists():
                print(f"Processing Coding answers: {coding_data}")
                coding_question_ids = set(str(q.id) for q in coding_questions)
                for question_id, code_answer in coding_data.items():
                    if question_id not in coding_question_ids:
                        print(f"coding question ID: {question_id}")
                        return Response(
                            {"detail": f"Invalid coding question ID: {question_id}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    # Save the answer if valid
                    coding_answers[question_id] = code_answer

            # Process Handwritten answers
            print(f"Processing files: {list(request.FILES.keys())}")
            for question_id, file in request.FILES.items():
                if question_id.startswith('handwritten_'):
                    question_id = question_id.replace('handwritten_', '')
                    try:
                        question = handwritten_questions.get(id=question_id)
                        handwritten_answers[question_id] = file
                    except HandwrittenQuestion.DoesNotExist:
                        return Response(
                            {"detail": f"Invalid handwritten question ID: {question_id}"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

            # Check if at least one type of answer is provided
            if not mcq_answers and not handwritten_answers and not coding_answers:
                print("No answers provided")
                return Response(
                    {"detail": "At least one answer (MCQ or handwritten or coding) must be provided"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Update submission and create scores
            with transaction.atomic():
                # Update submission
                if mcq_answers:
                    submission.mcq_answers = mcq_answers
                if handwritten_answers:
                    submission.handwritten_answers = handwritten_answers
                if coding_answers:
                    submission.codequestions_answers = coding_answers
                submission.is_submitted = True
                submission.save()
                print(f"Updated submission with answers. MCQ: {len(mcq_answers)}, Handwritten: {len(handwritten_answers)}, Coding: {len(coding_answers)}")

                # Update assessment score
                submission.update_assessment_score()
                print("Updated assessment score")

            # Return success message with details
            response_data = {
                "message": "Assessment submitted successfully",
                "submission_details": {
                    "mcq_answers_count": len(mcq_answers) if mcq_answers else 0,
                    "handwritten_answers_count": len(handwritten_answers) if handwritten_answers else 0,
                    "coding_answers_count": len(coding_answers) if coding_answers else 0
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
