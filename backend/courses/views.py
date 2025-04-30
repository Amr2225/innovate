from courses.serializers import CourseSerializer
from courses.models import Course
from rest_framework import generics
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound



class CourseListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        
        if user.role == "Institution":
            return Course.objects.filter(institution_id=user.id)
        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Course.objects.filter(institution_id__in=institutions.values_list('id', flat=True))

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [isInstitution]
        return super().get_permissions()


class RetrieveUpdateDestroyCourseDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    lookup_url_kwarg = 'p_id'

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution]
        return super().get_permissions()


class CourseProgressListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # We don't actually need a queryset because it's just a calculation
        return []

    def list(self, request, *args, **kwargs):
        course_id = self.kwargs.get('course_id')
        course = Course.objects.get(id=course_id)
        progress = course.get_user_course_progress(request.user)
        return Response({"course_progress": progress})