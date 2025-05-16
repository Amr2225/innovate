from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer
from courses.models import Course
from enrollments.models import Enrollments

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
                return Enrollments.objects.filter(
                    user=user,
                    course=obj.course,
                    is_completed=False
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
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=False
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
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=False
            ).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['assessment', 'student']

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
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=False
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
        if not Enrollments.objects.filter(
            user=user,
            course=assessment.course,
            is_completed=False
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
            enrolled_courses = Enrollments.objects.filter(
                user=user,
                is_completed=False
            ).values_list('course', flat=True)
            return queryset.filter(
                assessment__course__id__in=enrolled_courses,
                student=user
            )
        return AssessmentScore.objects.none()
