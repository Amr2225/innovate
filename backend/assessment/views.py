from rest_framework import generics, permissions
from .models import Assessment, AssessmentScore
from .serializers import AssessmentSerializer, AssessmentScoreSerializer
from users.permissions import isTeacher, isStudent
from enrollments.models import Enrollments
from rest_framework.exceptions import PermissionDenied

# ----------------------
# Assessment Views
# ----------------------

class AssessmentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentSerializer
    filterset_fields = ['due_date', 'type', 'title']

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated, isTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            enrolled_courses = Enrollments.objects.filter(user=user).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

    def perform_create(self, serializer):
        # Verify teacher is an instructor of the course
        course = serializer.validated_data.get('course')
        if not course.instructors.filter(id=self.request.user.id).exists():
            raise PermissionDenied("You must be an instructor of this course to create assessments.")
        serializer.save()


class AssessmentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, isTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return Assessment.objects.filter(course__instructors=user)
        elif user.role == "Student":
            enrolled_courses = Enrollments.objects.filter(user=user).values_list('course', flat=True)
            return Assessment.objects.filter(course__id__in=enrolled_courses)
        return Assessment.objects.none()

# ----------------------
# Assessment Score Views
# ----------------------

class AssessmentScoreListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = AssessmentScoreSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated, isStudent]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return AssessmentScore.objects.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            enrolled_courses = Enrollments.objects.filter(user=user).values_list('course', flat=True)
            return AssessmentScore.objects.filter(assessment__course__id__in=enrolled_courses, user=user)
        return AssessmentScore.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        assessment = serializer.validated_data.get('assessment')
        
        # Verify student is enrolled in the course
        if not Enrollments.objects.filter(user=user, course=assessment.course).exists():
            raise PermissionDenied("You must be enrolled in this course to submit scores.")
        # Verify assessment is still accepting submissions
        if not assessment.accepting_submissions:
            raise PermissionDenied("This assessment is no longer accepting submissions.")
        # Save with the current user
        serializer.save(user=user)


class AssessmentScoreRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AssessmentScoreSerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [permissions.IsAuthenticated, isTeacher]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.role == "Teacher":
            return AssessmentScore.objects.filter(assessment__course__instructors=user)
        elif user.role == "Student":
            enrolled_courses = Enrollments.objects.filter(user=user).values_list('course', flat=True)
            return AssessmentScore.objects.filter(assessment__course__id__in=enrolled_courses, user=user)
        return AssessmentScore.objects.none()
