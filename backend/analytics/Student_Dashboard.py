from rest_framework import generics
from rest_framework.response import Response
from enrollments.models import Enrollments
from assessment.models import Assessment
from AssessmentSubmission.models import AssessmentSubmission
from users.permissions import isStudent


class CourseCountView(generics.GenericAPIView):
    permission_classes = [isStudent]

    def get(self, request):
        user = request.user

        # Get all course and enrollment IDs for this user
        enrolled_course_ids = Enrollments.objects.filter(
            user=user, is_completed=False).values_list('course_id', flat=True)
        enrollment_ids = Enrollments.objects.filter(
            user=user, is_completed=False).values_list('id', flat=True)

        # Count courses
        course_count = enrolled_course_ids.distinct().count()

        # Count assessments by type
        assignment_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Assignment',).count()
        exam_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Exam').count()
        quiz_count = Assessment.objects.filter(
            course_id__in=enrolled_course_ids, type='Quiz').count()

        # Base queryset for submitted assessments
        submitted_qs = AssessmentSubmission.objects.filter(
            enrollment_id__in=enrollment_ids,
            is_submitted=True
        ).select_related('assessment')

        # Count total submitted assessments
        submission_count = submitted_qs.count()

        # Count submitted assessments by type
        submitted_assignments = submitted_qs.filter(
            assessment__type='Assignment').count()
        submitted_exams = submitted_qs.filter(assessment__type='Exam').count()
        submitted_quizzes = submitted_qs.filter(
            assessment__type='Quiz').count()

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
