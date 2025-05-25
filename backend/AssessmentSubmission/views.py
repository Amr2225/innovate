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
                # For students, only get their own questions
                mcq_questions = assessment.mcq_questions.filter(
                    assessment=assessment,
                    created_by=enrollment.user
                )
                handwritten_questions = assessment.handwritten_questions.filter(
                    assessment=assessment,
                    created_by=enrollment.user
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
            except Enrollments.DoesNotExist:
                return Response(
                    {"detail": "You are not enrolled in this course"},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Get or create submission
            submission = AssessmentSubmission.get_or_create_submission(assessment, enrollment)

            # Check if already submitted
            if submission.is_submitted:
                return Response(
                    {"detail": "You have already submitted this assessment"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get all questions for the assessment that were generated for this student
            all_questions = McqQuestion.objects.filter(
                assessment=assessment,
                created_by=enrollment.user
            )
            
            # Get question details for better error messages
            question_details = {
                str(q.id): {
                    'question': q.question,
                    'options': q.options,
                    'answer_key': q.answer_key,
                    'question_grade': str(q.question_grade)
                } for q in all_questions
            }
            question_ids = list(question_details.keys())

            # Process MCQ answers
            mcq_answers = {}
            mcq_data = request.data.get('mcq_answers')
            if mcq_data is None:
                return Response(
                    {"detail": "MCQ answers are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

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

            # Check if all questions are answered
            missing_questions = set(question_ids) - set(mcq_data.keys())
            if missing_questions:
                return Response(
                    {
                        "detail": "Missing answers for some questions",
                        "missing_questions": list(missing_questions),
                        "question_details": {qid: question_details[qid] for qid in missing_questions}
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate answers
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
            handwritten_answers = {}
            for question_id, image in request.FILES.items():
                if question_id.startswith('handwritten_'):
                    question_id = question_id.replace('handwritten_', '')
                    # Verify the question exists and belongs to this student
                    try:
                        question = HandwrittenQuestion.objects.get(
                            id=question_id,
                            assessment=assessment,
                            created_by=enrollment.user
                        )
                    except HandwrittenQuestion.DoesNotExist:
                        continue

                    # Save the image and get its path
                    score = HandwrittenQuestionScore(
                        question=question,
                        enrollment=enrollment,
                        answer_image=image
                    )
                    score.save()
                    handwritten_answers[str(question_id)] = score.answer_image.path

            # Update submission
            with transaction.atomic():
                submission.mcq_answers = mcq_answers
                submission.handwritten_answers = handwritten_answers
                submission.is_submitted = True
                submission.save()

            # Prepare detailed response with questions and answers
            response_data = {
                "message": "Assessment submitted successfully",
                "submission_id": str(submission.id),
                "questions": []
            }

            # Add question details with answers
            for question_id, answer in mcq_answers.items():
                question = all_questions.get(id=question_id)
                if question:
                    question_data = {
                        "id": str(question.id),
                        "question": question.question,
                        "options": question.options,
                        "answer_key": question.answer_key,
                        "question_grade": str(question.question_grade),
                        "selected_answer": answer,
                        "is_correct": answer == question.answer_key
                    }
                    response_data["questions"].append(question_data)

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
