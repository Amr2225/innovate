from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore
from AssessmentSubmission.models import AssessmentSubmission
from users.models import User


class StudentDashboardView(generics.GenericAPIView):
    def get(self, request):
        if request.user.role != "Student":
            return Response({"message": "You Can't use this"}, status=status.HTTP_403_FORBIDDEN)

        user = request.user

        enrolled_course_ids = Enrollments.objects.filter(
            user=user).values_list('course_id', flat=True)
        enrollment_ids = Enrollments.objects.filter(
            user=user).values_list('id', flat=True)
        course_count = enrolled_course_ids.count()
        assignment_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Assignment').count()
        exam_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Exam').count()
        quiz_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Quiz').count()
        submission_count = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids).count()
        submitted_assignments = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids, assessment__type='Assignment').count()
        submitted_exams = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids, assessment__type='Exam').count()
        submitted_quizzes = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids, assessment__type='Quiz').count()
        return Response({
            "course_count": course_count,
            "assignment_count": assignment_count,
            "exam_count": exam_count,
            "quiz_count": quiz_count,
            "submission_count": submission_count,
            "submitted_assignments_count": submitted_assignments,
            "submitted_exams_count": submitted_exams,
            "submitted_quizzes_count": submitted_quizzes
        })


class CourseCountView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != "Institution":
            return Response({"message": "You Can't use this"}, status=status.HTTP_403_FORBIDDEN)

        TeacherCount = User.objects.filter(
            role='Teacher', institution=user).count()
        StudentCount = User.objects.filter(
            role='Student', institution=user).count()
        course_count = Course.objects.filter(institution=user).count()
        return Response({
            "course_count": course_count,
            "TeacherCount": TeacherCount,
            "StudentCount": StudentCount,
        })
