from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from courses.models import Course
from enrollments.models import Enrollments
from courses.serializers import CourseSerializer
from enrollments.serializers import EnrollMultipleCoursesSerializer
from enrollments.serializers import EnrollmentsSerializer

class EnrolledCoursesAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        enrolled_course_ids = Enrollments.objects.filter(
            user=user
        ).values_list('course_id', flat=True)

        return Course.objects.filter(id__in=enrolled_course_ids)

class EligibleCoursesAPIView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EnrollMultipleCoursesSerializer
        return CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        completed_course_ids = Enrollments.objects.filter(
            user=user,
            is_completed=True
        ).values_list('course_id', flat=True)

        enrolled_course_ids = Enrollments.objects.filter(
            user=user
        ).values_list('course_id', flat=True)

        potential_courses = Course.objects.exclude(id__in=enrolled_course_ids)

        eligible_courses = potential_courses.filter(
            (Q(prerequisite_course__isnull=True) |
            Q(prerequisite_course__in=completed_course_ids)) &
            Q(semester__lte=user.semester)
        )

        return eligible_courses
    
    def create(self, request, *args, **kwargs):
        user = request.user
        print(request.data)
        course_ids = request.data.get("courses", [])

        if not isinstance(course_ids, list) or not course_ids:
            return Response({"error": "Please provide a list of course IDs."}, status=status.HTTP_400_BAD_REQUEST)

        completed_course_ids = set(Enrollments.objects.filter(
            user=user,
            is_completed=True
        ).values_list('course_id', flat=True))

        enrolled_course_ids = set(Enrollments.objects.filter(
            user=user
        ).values_list('course_id', flat=True))

        enrolled_courses = []
        skipped_courses = {}

        for course_id in course_ids:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                skipped_courses[course_id] = "Course not found."
                continue

            if course.id in enrolled_course_ids:
                skipped_courses[course_id] = "Already enrolled."
                continue

            prereq = course.prerequisite_course
            if prereq and prereq.id not in completed_course_ids:
                skipped_courses[course_id] = "Prerequisite not completed."
                continue

            enrollment = Enrollments.objects.create(user=user, course=course)
            enrolled_courses.append(enrollment)

        return Response({
            "enrolled": EnrollmentsSerializer(enrolled_courses, many=True).data,
            "skipped": skipped_courses
        }, status=status.HTTP_201_CREATED)
