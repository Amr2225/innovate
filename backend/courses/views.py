from courses.serializers import CourseSerializer
from courses.models import Course
from rest_framework import generics
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView


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

class CoursesByInstitutionAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        institution_id = self.kwargs.get("institution_id")
        return Course.objects.filter(institution_id=institution_id)