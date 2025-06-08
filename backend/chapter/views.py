from django.shortcuts import render
from chapter.serializers import ChapterSerializer, ChapterBulkCreateSerializer
from chapter.models import Chapter
from rest_framework import generics
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from users.permissions import isInstitution, isTeacher
from rest_framework.permissions import IsAuthenticated
from courses.models import Course
import json
from lecture.models import Lecture
from django.db import transaction


class ChapterListCreateAPIView(generics.ListCreateAPIView):
    filterset_fields = ['id', 'title', 'course']
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ChapterBulkCreateSerializer
        return ChapterSerializer

    def get_queryset(self):
        user = self.request.user

        if user.role == "Institution":
            # This returns chapters of their courses
            return Chapter.objects.filter(course__institution=user)

        elif user.role in ["Student", "Teacher"]:
            institutions = user.institution.all()
            if institutions.exists():
                return Chapter.objects.filter(course__institution__in=institutions)

        return Chapter.objects.none()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method == 'POST':
            self.permission_classes = [isTeacher | isInstitution]
        return super().get_permissions()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Custom create method that handles:
        1. JSON string with chapters and lectures data
        2. Separate file uploads for videos and attachments
        """
        try:
            # Check if the request has chapters data
            if 'chapters' not in request.data:
                return Response(
                    {"error": "Missing 'chapters' field in request"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get chapters data from JSON string
            try:
                if isinstance(request.data['chapters'], str):
                    chapters_data = json.loads(request.data['chapters'])
                else:
                    # If it's already parsed as JSON by DRF
                    chapters_data = request.data['chapters']
            except json.JSONDecodeError:
                return Response(
                    {"error": "Invalid JSON in 'chapters' field"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate user permissions for each chapter
            user = request.user
            created_chapters = []

            for chapter_data in chapters_data:
                # Validate course access
                try:
                    course_id = chapter_data.get('courseId')
                    course = Course.objects.get(id=course_id)

                    if user.role == "Institution" and course.institution != user:
                        return Response(
                            {"error": f"You do not have permission to add a chapter to course: {course.name}"},
                            status=status.HTTP_403_FORBIDDEN
                        )

                    elif user.role == "Teacher" and course.institution not in user.institution.all():
                        return Response(
                            {"error": f"You do not have permission to add a chapter to course: {course.name}"},
                            status=status.HTTP_403_FORBIDDEN
                        )

                except Course.DoesNotExist:
                    return Response(
                        {"error": f"Course with ID {course_id} does not exist"},
                        status=status.HTTP_404_NOT_FOUND
                    )

                # Create chapter
                chapter = Chapter.objects.create(
                    title=chapter_data.get('title'),
                    course=course
                )

                # Process lectures for this chapter
                lectures_data = chapter_data.get('lectures', [])
                created_lectures = []

                for lecture_idx, lecture_data in enumerate(lectures_data):
                    lecture = Lecture(
                        title=lecture_data.get('title', ''),
                        description=lecture_data.get('description', ''),
                        chapter=chapter
                    )

                    # Look for video file
                    video_key = f"chapter_{chapters_data.index(chapter_data)}_lecture_{lecture_idx}_video"
                    if video_key in request.FILES:
                        lecture.video = request.FILES[video_key]

                    # Look for attachment file
                    attachment_key = f"chapter_{chapters_data.index(chapter_data)}_lecture_{lecture_idx}_attachment"
                    if attachment_key in request.FILES:
                        lecture.attachment = request.FILES[attachment_key]

                    lecture.save()
                    self._create_lecture_progress(lecture)
                    created_lectures.append(lecture)

                # Add lectures to response data
                chapter_data = {
                    'id': str(chapter.id),
                    'title': chapter.title,
                    'course': str(chapter.course.id),
                    'lectures': [
                        {
                            'id': str(lecture.id),
                            'title': lecture.title,
                            'description': lecture.description,
                            'video': lecture.video.url if lecture.video else None,
                            'attachment': lecture.attachment.url if lecture.attachment else None,
                        }
                        for lecture in created_lectures
                    ]
                }

                created_chapters.append(chapter_data)

            return Response(created_chapters, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Rollback transaction on error
            transaction.set_rollback(True)
            print(e)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _create_lecture_progress(self, lecture):
        """Helper method to create progress entries for a lecture"""
        from lecture.models import LectureProgress
        from users.models import User

        chapter = lecture.chapter
        course = chapter.course
        semester = course.semester

        students = User.objects.filter(
            institution=course.institution,
            role="Student",
            semester=semester
        )

        progress_entries = [
            LectureProgress(user=student, lecture=lecture, completed=False)
            for student in students
        ]

        if progress_entries:
            LectureProgress.objects.bulk_create(progress_entries)

    def perform_single_create(self, serializer):
        """Legacy method for single chapter creation - not used with new approach"""
        course = serializer.validated_data['course']
        user = self.request.user
        if user.role == "Institution" and course.institution != user:
            raise serializers.ValidationError(
                "You do not have permission to add a chapter to this course.")
        elif user.role == "Teacher" and course.institution not in user.institution.all():
            raise serializers.ValidationError(
                "You do not have permission to add a chapter to this course.")
        serializer.save()


class ChapterRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChapterSerializer
    queryset = Chapter.objects.all()
    lookup_url_kwarg = 'p_id'

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [isInstitution | isTeacher]
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
            raise serializers.ValidationError(
                "You do not have permission to assign this chapter to that course.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if instance.course.institution != user:
            raise serializers.ValidationError(
                "You do not have permission to delete this chapter.")
        instance.delete()
