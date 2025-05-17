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
from rest_framework.parsers import JSONParser

# ----------------------
# Assessment Views
# ----------------------

class AssessmentPermission(permissions.BasePermission):
    """Custom permission class for assessments"""
    
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
                # Students can only view assessments for courses they're enrolled in
                is_completed = request.query_params.get('is_completed', 'false').lower() == 'true'
                return Enrollments.objects.filter(
                    user=user,
                    course=obj.course,
                    is_completed=is_completed
                ).exists()
            elif user.role == "Teacher":
                # Teachers can view assessments for courses they teach
                return obj.course.instructors.filter(id=user.id).exists()
            elif user.role == "Institution":
                # Institution can view any assessment in their courses
                return obj.course.institution == user
            return False

        # For write operations (create/update/delete)
        if user.role == "Teacher":
            # Teachers can modify assessments for courses they teach
            return obj.course.instructors.filter(id=user.id).exists()
        elif user.role == "Institution":
            # Institution can modify any assessment in their courses
            return obj.course.institution == user
        return False

class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [AssessmentPermission]
    filterset_fields = ['due_date', 'type', 'title']

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            # Institution can see all assessments in their courses
            return Assessment.objects.filter(course__institution=user)
        elif user.role == "Teacher":
            # Teachers can see assessments for courses they teach
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            # Students can only see assessments for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        course = Course.objects.get(id=self.request.data.get('course'))
        
        # Check permissions based on role
        if user.role == "Teacher" and not course.instructors.filter(id=user.id).exists():
            raise PermissionDenied("You are not an instructor for this course")
        elif user.role == "Institution" and course.institution != user:
            raise PermissionDenied("This course does not belong to your institution")
            
        serializer.save()

class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer
    permission_classes = [AssessmentPermission]
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
        user = self.request.user
        if user.role == "Institution":
            # Institution can access any assessment in their courses
            return Assessment.objects.filter(course__institution=user)
        elif user.role == "Teacher":
            # Teachers can access assessments for courses they teach
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            # Students can only access assessments for courses they're enrolled in
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['assessment']

    def get_queryset(self):
        user = self.request.user
        queryset = AssessmentScore.objects.all()

        # Filter by assessment_id if provided
        assessment_id = self.request.query_params.get('assessment_id')
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)

        # Filter by student_id if provided
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        if user.role == "Institution":
            return queryset.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only see their own scores for enrolled courses
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return queryset.filter(
                assessment__course__id__in=enrolled_courses,
                student=user
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
        
        # Check if student has already submitted
        if AssessmentScore.objects.filter(assessment=assessment, student=user).exists():
            raise PermissionDenied("You have already submitted this assessment")
        
        serializer.save(student=user)

class AssessmentScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = AssessmentScore.objects.all()

        # Filter by assessment_id if provided
        assessment_id = self.request.query_params.get('assessment_id')
        if assessment_id:
            queryset = queryset.filter(assessment_id=assessment_id)

        # Filter by student_id if provided
        student_id = self.request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)

        if user.role == "Institution":
            return queryset.filter(assessment__course__institution=user)
        elif user.role == "Teacher":
            return queryset.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            # Students can only access their own scores for enrolled courses
            is_completed = self.request.query_params.get('is_completed', 'false').lower() == 'true'
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=is_completed
            ).values_list('course', flat=True)
            return queryset.filter(
                assessment__course__id__in=enrolled_courses,
                student=user
            )
        return AssessmentScore.objects.none()

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
                        'options': mcq_score.question.answer,
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
