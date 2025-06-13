from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from users.models import User

class CourseLectureProgressView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, course_id):
        user = request.user

        try:
            enrollment = Enrollments.objects.get(user=user, course_id=course_id)
        except Enrollments.DoesNotExist:
            return Response({'detail': 'You are not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)

        lectures = Lecture.objects.filter(chapter__course_id=course_id)

        total_lectures = lectures.count()
        completed_count = 0

        for lecture in lectures:
            progress = LectureProgress.objects.filter(enrollment=enrollment, lecture=lecture).first()
            is_completed = progress.completed if progress else False
            if is_completed:
                completed_count += 1

        completion_rate = (completed_count / total_lectures) * 100 if total_lectures > 0 else 0

        return Response({
            'course_id': course_id,
            'completion_rate': int(completion_rate),
        })