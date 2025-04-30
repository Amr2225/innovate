from django.shortcuts import render
from chapter.serializers import ChapterSerializer
from chapter.models import Chapter
from rest_framework import generics
from rest_framework import serializers
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

# Create your views here.
class ChapterListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ChapterSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "Institution":
            return Chapter.objects.filter(course__institution=user)  # This returns chapters of their courses

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Chapter.objects.filter(course__institution__in=institutions)

        return Chapter.objects.none()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [isInstitution]
        return super().get_permissions()

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if course.institution != self.request.user:
            raise serializers.ValidationError("You do not have permission to add a chapter to this course.")
        serializer.save()

class ChapterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all()
    lookup_url_kwarg = 'p_id'

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user

        if user.role == "Institution":
            return Chapter.objects.filter(course__institution=user)

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Chapter.objects.filter(course__institution__in=institutions)

        return Chapter.objects.none()

    def perform_update(self, serializer):
        course = serializer.validated_data.get('course')
        if course and course.institution != self.request.user:
            raise serializers.ValidationError("You do not have permission to assign this chapter to that course.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.course.institution != user:
            raise serializers.ValidationError("You do not have permission to delete this chapter.")
        instance.delete()


class CourseChaptersAPIView(generics.ListAPIView):
    serializer_class = ChapterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['course_id']
        user = self.request.user

        if user.role == "Institution":
            return Chapter.objects.filter(course__id=course_id, course__institution=user)

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Chapter.objects.filter(course__id=course_id, course__institution__in=institutions)

        return Chapter.objects.none()