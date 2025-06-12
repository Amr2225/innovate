from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore
from AssessmentSubmission.models import AssessmentSubmission

class CourseCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all course IDs the user is enrolled in
        enrolled_course_ids = Enrollments.objects.filter(user=user).values_list('course_id', flat=True)

        # Count distinct courses
        course_count = enrolled_course_ids.distinct().count()

        # Count assessments of type 'Assignment' for enrolled courses
        assignment_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids,
            type='Assignment'
        ).count()

        # Count assessments of type 'Exam' for enrolled courses
        exam_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids,
            type='Exam'
        ).count()

        # Count assessments of type 'Quiz' for enrolled courses
        quiz_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids,
            type='Quiz'
        ).count()

        # Count submissions for enrolled courses
        submission_count = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrolled_course_ids,
            is_submitted=True
        ).count()

        
        return Response({
            "course_count": course_count,
            "assignment_count": assignment_count,
            "exam_count": exam_count,
            "quiz_count": quiz_count,
            "submission_count": submission_count,
        })
