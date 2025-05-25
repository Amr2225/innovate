from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer
from courses.models import Course
from enrollments.models import Enrollments
from mcqQuestion.models import McqQuestion
from mcqQuestion.serializers import McqQuestionSerializer
from MCQQuestionScore.models import MCQQuestionScore
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.shortcuts import render
from HandwrittenQuestion.models import HandwrittenQuestion, HandwrittenQuestionScore
from django.utils import timezone

# ----------------------
# Assessment Views
# ----------------------

class AssessmentPermission(permissions.BasePermission):
    """Custom permission class for assessments"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # Allow all authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Only teachers and institutions can create/edit
        return request.user.role in ["Teacher", "Institution"]
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Students can only view their own assessments
        if request.user.role == "Student":
            return Enrollments.objects.filter(
                user=request.user,
                course=obj.course
            ).exists()
        
        # Teachers can access assessments for their courses
        if request.user.role == "Teacher":
            return obj.course.teacher == request.user.teacher
        
        # Institutions can access assessments for their courses
        if request.user.role == "Institution":
            return obj.course.institution == request.user.institution
        
        return False

class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see assessments for courses they are enrolled in
            return Assessment.objects.filter(
                course__enrollments__user=user
            ).distinct()
        
        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return Assessment.objects.filter(
                course__teacher=user.teacher
            )
        
        elif user.role == "Institution":
            # Institutions can see assessments for their courses
            return Assessment.objects.filter(
                course__institution=user.institution
            )
        
        return Assessment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can create assessments")
        
        # Check if user has permission to create assessment for this course
        course = serializer.validated_data['course']
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied("You can only create assessments for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied("You can only create assessments for your institution's courses")
        
        serializer.save()

class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see assessments for courses they are enrolled in
            return Assessment.objects.filter(
                course__enrollments__user=user
            ).distinct()
        
        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return Assessment.objects.filter(
                course__teacher=user.teacher
            )
        
        elif user.role == "Institution":
            # Institutions can see assessments for their courses
            return Assessment.objects.filter(
                course__institution=user.institution
            )
        
        return Assessment.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can update assessments")
        
        # Check if user has permission to update assessment for this course
        course = serializer.instance.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied("You can only update assessments for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied("You can only update assessments for your institution's courses")
        
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can delete assessments")
        
        # Check if user has permission to delete assessment for this course
        course = instance.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied("You can only delete assessments for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied("You can only delete assessments for your institution's courses")
        
        instance.delete()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see their own scores
            return AssessmentScore.objects.filter(
                enrollment__user=user
            )
        
        elif user.role == "Teacher":
            # Teachers can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__teacher=user.teacher
            )
        
        elif user.role == "Institution":
            # Institutions can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__institution=user.institution
            )
        
        return AssessmentScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != "Student":
            raise PermissionDenied("Only students can submit assessment scores")

        assessment = Assessment.objects.get(id=self.request.data.get('assessment'))
        
        # Check if the assessment is still accepting submissions
        if not assessment.accepting_submissions:
            raise PermissionDenied("This assessment is no longer accepting submissions as it has passed its due date")
        
        # Check if student is enrolled in the course
        is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
        if not Enrollments.objects.filter(
            user=user,
            course=assessment.course,
            is_completed=is_completed
        ).exists():
            raise PermissionDenied("You are not enrolled in this course")
        
        enrollment = Enrollments.objects.get(user=user, course=assessment.course)
        # Check if student has already submitted
        if AssessmentScore.objects.filter(assessment=assessment, enrollment=enrollment).exists():
            raise PermissionDenied("You have already submitted this assessment")
        
        serializer.save(enrollment=enrollment)

class AssessmentScoreDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Student":
            # Students can only see their own scores
            return AssessmentScore.objects.filter(
                enrollment__user=user
            )
        
        elif user.role == "Teacher":
            # Teachers can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__teacher=user.teacher
            )
        
        elif user.role == "Institution":
            # Institutions can see scores for their courses
            return AssessmentScore.objects.filter(
                assessment__course__institution=user.institution
            )
        
        return AssessmentScore.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can update assessment scores")
        
        # Check if user has permission to update score for this course
        course = serializer.instance.assessment.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied("You can only update scores for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied("You can only update scores for your institution's courses")
        
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if user.role not in ["Teacher", "Institution"]:
            raise PermissionDenied("Only teachers and institutions can delete assessment scores")
        
        # Check if user has permission to delete score for this course
        course = instance.assessment.course
        if user.role == "Teacher" and course.teacher != user.teacher:
            raise PermissionDenied("You can only delete scores for courses you teach")
        if user.role == "Institution" and course.institution != user.institution:
            raise PermissionDenied("You can only delete scores for your institution's courses")
        
        instance.delete()

class AssessmentQuestionsAPIView(generics.ListAPIView):
    """View to get all questions for a specific assessment"""
    serializer_class = McqQuestionSerializer
    permission_classes = [AssessmentPermission]

    def get_queryset(self):
        assessment_id = self.kwargs.get('pk')
        user = self.request.user

        try:
            assessment = Assessment.objects.get(id=assessment_id)
        except Assessment.DoesNotExist:
            return McqQuestion.objects.none()

        # Check permissions
        if user.role == "Student":
            # Students can only view questions for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            if not Enrollments.objects.filter(
                user=user,
                course=assessment.course,
                is_completed=is_completed
            ).exists():
                return McqQuestion.objects.none()
        elif user.role == "Teacher":
            # Teachers can view questions for courses they teach
            if not assessment.course.instructors.filter(id=user.id).exists():
                return McqQuestion.objects.none()
        elif user.role == "Institution":
            # Institution can view questions for their courses
            if assessment.course.institution != user:
                return McqQuestion.objects.none()
        else:
            return McqQuestion.objects.none()

        # Get all questions for the assessment
        return McqQuestion.objects.filter(assessment=assessment)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add request to context for role-based answer key visibility
        context['request'] = self.request
        return context

class StudentGradesAPIView(generics.GenericAPIView):
    """View to get total grade for a student's assessment"""
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        try:
            enrollment_id = request.data.get('enrollment_id')
            assessment_id = request.data.get('assessment_id')

            if not enrollment_id or not assessment_id:
                return Response({
                    'detail': 'Both enrollment_id and assessment_id are required in request body'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get the assessment score
            try:
                assessment_score = AssessmentScore.objects.select_related(
                    'assessment__course',
                    'enrollment__user'
                ).get(
                    enrollment_id=enrollment_id,
                    assessment_id=assessment_id
                )
            except AssessmentScore.DoesNotExist:
                return Response({
                    'detail': 'No assessment score found for this Student and assessment'
                }, status=status.HTTP_404_NOT_FOUND)

            # Check permissions
            user = request.user
            if user.role == "Student" and str(assessment_score.enrollment.user.id) != str(user.id):
                return Response({
                    'detail': 'You can only view your own grades'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == "Teacher" and not assessment_score.assessment.course.instructors.filter(id=user.id).exists():
                return Response({
                    'detail': 'You can only view grades for your courses'
                }, status=status.HTTP_403_FORBIDDEN)
            elif user.role == "Institution" and assessment_score.assessment.course.institution != user:
                return Response({
                    'detail': 'You can only view grades for your institution'
                }, status=status.HTTP_403_FORBIDDEN)

            # Get all MCQ questions and scores for this assessment and student
            mcq_scores = MCQQuestionScore.objects.filter(
                question__assessment=assessment_score.assessment,
                enrollment=assessment_score.enrollment
            ).select_related('question')

            # Calculate total score of answered questions
            total_answered_score = mcq_scores.aggregate(total=Sum('score'))['total'] or 0

            # Build questions data with student scores
            questions_data = []
            for mcq_score in mcq_scores:
                question_data = {
                    'question_id': str(mcq_score.question.id),
                    'question_text': mcq_score.question.question,
                    'student_answer': mcq_score.selected_answer,
                    'is_correct': mcq_score.is_correct,
                    'score': str(mcq_score.score),
                    'max_score': str(mcq_score.question.question_grade)
                }
                
                if user.role in ['Teacher', 'Institution','Student']:
                    question_data.update({
                        'options': mcq_score.question.options,
                        'correct_answer': mcq_score.question.answer_key
                    })
                
                questions_data.append(question_data)

            response_data = {
                'assessment_id': str(assessment_score.assessment.id),
                'assessment_title': assessment_score.assessment.title,
                'enrollment_id': str(assessment_score.enrollment.id),
                'student_name': f"{assessment_score.enrollment.user.first_name} {assessment_score.enrollment.user.last_name}",
                'questions': questions_data,
                'total_score': int(total_answered_score),
                'total_max_score': int(assessment_score.assessment.grade)
            }

            return Response(response_data)

        except Exception as e:
            return Response({
                'detail': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AssessmentAllQuestionsAPIView(generics.RetrieveAPIView):
    """API view to get all questions for an assessment"""
    permission_classes = [permissions.IsAuthenticated, AssessmentPermission]
    serializer_class = AssessmentSerializer

    def get_object(self):
        try:
            return Assessment.objects.select_related('course').get(pk=self.kwargs['pk'])
        except Assessment.DoesNotExist:
            raise Http404("Assessment not found")

    def retrieve(self, request, *args, **kwargs):
        try:
            assessment = self.get_object()
            
            # Get student's enrollment
            enrollment = None
            if request.user.role == 'Student':
                try:
                    is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
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
            
            # Get all questions based on user role
            if request.user.role == "Student":
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
                'questions': []
            }

            # Add MCQ questions
            for question in mcq_questions:
                question_data = {
                    'id': str(question.id),
                    'type': 'mcq',
                    'question': question.question,
                    'options': question.options,
                    'answer_key': question.answer_key,
                    'question_grade': str(question.question_grade)
                }
                response_data['questions'].append(question_data)

            # Add Handwritten questions
            for question in handwritten_questions:
                question_data = {
                    'id': str(question.id),
                    'type': 'handwritten',
                    'question': question.question_text,
                    'answer_key': question.answer_key,
                    'max_grade': str(question.max_grade)
                }
                response_data['questions'].append(question_data)

            return Response(response_data)

        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AssessmentStudentQuestionsAPIView(generics.RetrieveAPIView):
    """
    API view to get all questions for a student in an assessment.
    This includes:
    1. Dynamic MCQ questions (generated if not exists)
    2. Regular MCQ questions
    3. Handwritten questions
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AssessmentSerializer

    def get_object(self):
        assessment_id = self.kwargs.get('pk')
        try:
            assessment = Assessment.objects.get(id=assessment_id)
        
            # Check if student is enrolled in the course
            if not Enrollments.objects.filter(
                user=self.request.user,
                course=assessment.course
            ).exists():
                raise PermissionDenied("You are not enrolled in this course")
            
            # Check if assessment is still accepting submissions
            if not assessment.accepting_submissions:
                raise PermissionDenied("This assessment is no longer accepting submissions")
            
            # Check if assessment has started
            if assessment.start_date > timezone.now():
                raise PermissionDenied("This assessment has not started yet")
            
            return assessment
        except Assessment.DoesNotExist:
            raise Http404("Assessment not found")

    def retrieve(self, request, *args, **kwargs):
        assessment = self.get_object()
        
        try:
            # Get all questions for the student
            questions = assessment.get_all_questions_for_student(request.user)
            
            # Format all questions into a single list with their types
            formatted_questions = []
            
            # Add dynamic MCQ questions
            formatted_questions.extend([
                {
                    'type': 'dynamic_mcq',
                    'id': str(q['id']),
                    'question': q['question'],
                    'options': q['options'],
                    'difficulty': q['difficulty'],
                    'grade': q.get('grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('dynamic_mcq', [])
            ])
            
            # Add regular MCQ questions
            formatted_questions.extend([
                {
                    'type': 'mcq',
                    'id': str(q['id']),
                    'question': q['question'],
                    'options': q['options'],
                    'grade': q.get('grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('mcq', [])
            ])
            
            # Add handwritten questions
            formatted_questions.extend([
                {
                    'type': 'handwritten',
                    'id': str(q['id']),
                    'question': q['question'],
                    'max_grade': q.get('max_grade', 0),
                    'section_number': q.get('section_number', 1)
                } for q in questions.get('handwritten', [])
            ])
            
            # Sort questions by section number
            formatted_questions.sort(key=lambda x: x['section_number'])
            
            # Add assessment details
            response_data = {
                'assessment': {
                    'id': str(assessment.id),
                    'title': assessment.title,
                    'type': assessment.type,
                    'due_date': assessment.due_date,
                    'grade': assessment.grade,
                    'total_grade': assessment.total_grade
                },
                'questions': formatted_questions
            }
            
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
