from rest_framework import generics
from lecture.models import Lecture, LectureProgress
from lecture.serializers import LectureSerializer, LectureProgressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from users.permissions import isInstitution, isStudent, isTeacher
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

class LectureListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LectureSerializer

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
            user = self.request.user
            if user.role == "Institution":
                self.permission_classes = [isInstitution]
            elif user.role == "Teacher":
                self.permission_classes = [isTeacher]
            else:
                self.permission_classes = [isTeacher]

        return super().get_permissions()

    def perform_create(self, serializer):
        chapter = serializer.validated_data['chapter']
        user = self.request.user

        if user.role == "Teacher":
            if chapter.course.instructor != user:
                raise serializers.ValidationError("You are not the instructor of this course.")

        elif user.role == "Institution":
            if chapter.course.institution != user:
                raise serializers.ValidationError("You do not have permission to add a lecture to this chapter.")

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
            self.permission_classes = [isInstitution]
        return super().get_permissions()

    def perform_update(self, serializer):
        chapter = serializer.validated_data.get('chapter', self.get_object().chapter)
        user = self.request.user

        if user.role == "Teacher":
            if chapter.course.instructor != user:
                raise serializers.ValidationError("You are not the instructor of this course.")

        elif user.role == "Institution":
            if chapter.course.institution != user:
                raise serializers.ValidationError("You do not have permission to update this lecture.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user

        if user.role == "Teacher":
            if instance.chapter.course.instructor != user:
                raise serializers.ValidationError("You are not the instructor of this course.")
        elif user.role == "Institution":
            if instance.chapter.course.institution != user:
                raise serializers.ValidationError("You do not have permission to delete this lecture.")

        instance.delete()



class LecturesProgressListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LectureProgressSerializer
    permission_classes = [isStudent]

    def get_queryset(self):
        # List only the lecture progresses of the current user
        return LectureProgress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Make sure the progress is linked to the logged-in user
        serializer.save(user=self.request.user)


class LectureProgressRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LectureProgressSerializer
    permission_classes = [isStudent]

    def get_object(self):
        lecture_id = self.kwargs.get('lecture_id')
        try:
            return LectureProgress.objects.get(user=self.request.user, lecture_id=lecture_id)
        except LectureProgress.DoesNotExist:
            raise NotFound("Progress not found for this lecture and user.")
        


class ChapterLecturesAPIView(generics.ListAPIView):
    serializer_class = LectureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        chapter_id = self.kwargs['chapter_id']
        user = self.request.user

        if user.role == "Institution":
            return Lecture.objects.filter(chapter__id=chapter_id, chapter__course__institution=user)

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Lecture.objects.filter(chapter__id=chapter_id, chapter__course__institution__in=institutions)

        return Lecture.objects.none()