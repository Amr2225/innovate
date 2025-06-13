from rest_framework import generics
from lecture.models import Lecture, LectureProgress
from lecture.serializers import LectureSerializer, LectureProgressSerializer, LectureBulkCreateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from enrollments.models import Enrollments


class LectureListCreateAPIView(generics.ListCreateAPIView):
    filterset_fields = ['id', 'title',
                        'description', 'chapter', 'chapter__course']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LectureBulkCreateSerializer
        return LectureSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "Institution":
            return Lecture.objects.filter(
                chapter__course__institution=user
            )

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Lecture.objects.filter(
                    chapter__course__institution__in=institutions
                )

        return Lecture.objects.none()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [isTeacher | isInstitution]

        return super().get_permissions()

    def perform_create(self, serializer):
        # For bulk creation, validation is handled in the serializer
        if isinstance(serializer, LectureBulkCreateSerializer):
            serializer.save()
            return

        # For single lecture creation
        chapter = serializer.validated_data['chapter']
        user = self.request.user

        if user.role == "Teacher":
            if user not in chapter.course.instructors.all():
                raise serializers.ValidationError(
                    "You are not the instructor of this course.")

        elif user.role == "Institution":
            if chapter.course.institution != user:
                raise serializers.ValidationError(
                    "You do not have permission to add a lecture to this chapter.")

        serializer.save()


class LectureRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LectureSerializer
    lookup_url_kwarg = 'p_id'

    def get_queryset(self):
        user = self.request.user

        if user.role == "Institution":
            return Lecture.objects.filter(
                chapter__course__institution=user
            )

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Lecture.objects.filter(
                    chapter__course__institution__in=institutions
                )

        return Lecture.objects.none()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution | isTeacher]
        return super().get_permissions()

    def perform_update(self, serializer):
        chapter = serializer.validated_data.get(
            'chapter', self.get_object().chapter)
        user = self.request.user

        if user.role == "Teacher":
            if chapter.course.instructor != user:
                raise serializers.ValidationError(
                    "You are not the instructor of this course.")

        elif user.role == "Institution":
            if chapter.course.institution != user:
                raise serializers.ValidationError(
                    "You do not have permission to update this lecture.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "Teacher":
            if instance.chapter.course.instructor != user:
                raise serializers.ValidationError(
                    "You are not the instructor of this course.")
        elif user.role == "Institution":
            if instance.chapter.course.institution != user:
                raise serializers.ValidationError(
                    "You do not have permission to delete this lecture.")

        instance.delete()


class LecturesProgressListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LectureProgressSerializer
    permission_classes = [isStudent]
    filterset_fields = ['id', 'lecture', 'completed']

    def get_queryset(self):
        enrollments = Enrollments.objects.filter(user=self.request.user)
        return LectureProgress.objects.filter(enrollment__in=enrollments)

    def perform_create(self, serializer):
        serializer.save()
