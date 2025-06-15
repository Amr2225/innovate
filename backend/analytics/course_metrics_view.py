from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Avg, Count
from courses.models import Course
from enrollments.models import Enrollments
from lecture.models import Lecture, LectureProgress
from assessment.models import Assessment, AssessmentScore


class CourseMetricsView(generics.GenericAPIView):
    """
    API endpoint for course metrics.

    GET /api/analytics/course-metrics/{course_id}/

    Accessible by:
    - Teachers (only if assigned to the course)
    - Institutions (only if course belongs to them)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        user = request.user

        # Role-based access control
        if user.role not in ["Teacher", "Institution"]:
            return Response(
                {"detail": "Only teachers or institutions can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Course validation based on role
        try:
            if user.role == "Teacher":
                course = Course.objects.get(id=course_id, instructors=user)
            elif user.role == "Institution":
                course = Course.objects.get(id=course_id, institution=user)
        except Course.DoesNotExist:
            return Response(
                {"detail": "Course not found or you don't have permission to access it"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Enrollment metrics
        enrollments = Enrollments.objects.filter(course=course)
        total_enrollments = enrollments.count()
        active_enrollments = enrollments.filter(is_completed=False).count()
        completed_enrollments = enrollments.filter(is_completed=True).count()
        completion_rate = (completed_enrollments / total_enrollments * 100) if total_enrollments else 0
        dropout_rate = 100 - completion_rate

        # Assessment metrics
        assessments = Assessment.objects.filter(course=course)
        total_assessments = assessments.count()
        assessment_types = {
            'exam': assessments.filter(type='Exam').count(),
            'assignment': assessments.filter(type='Assignment').count(),
            'quiz': assessments.filter(type='Quiz').count()
        }
        assessment_scores = AssessmentScore.objects.filter(assessment__course=course)
        total_attempts = assessment_scores.count()
        submission_rate = (total_attempts / (total_enrollments * total_assessments) * 100) if total_assessments and total_enrollments else 0

        # Performance metrics
        scores = [float(score.total_score) for score in assessment_scores]
        overall_average = sum(scores) / len(scores) if scores else 0

        sorted_scores = sorted(scores)
        mid = len(sorted_scores) // 2
        median_score = (sorted_scores[mid] + sorted_scores[~mid]) / 2 if sorted_scores else 0

        if scores:
            mean = sum(scores) / len(scores)
            variance = sum((x - mean) ** 2 for x in scores) / len(scores)
            standard_deviation = variance ** 0.5
        else:
            standard_deviation = 0

        passing_threshold = 60
        excellence_threshold = 85
        passing_count = sum(1 for score in scores if score >= passing_threshold)
        excellence_count = sum(1 for score in scores if score >= excellence_threshold)
        passing_rate = (passing_count / len(scores) * 100) if scores else 0
        excellence_rate = (excellence_count / len(scores) * 100) if scores else 0

        # Engagement metrics
        lecture_progress = LectureProgress.objects.filter(enrollment__course=course)
        total_lectures = Lecture.objects.filter(chapter__course=course).count()
        completed_lectures = lecture_progress.filter(completed=True).count()
        average_completion_time = lecture_progress.aggregate(avg_time=Avg('time_spent'))['avg_time'] or 0
        active_students_percentage = (active_enrollments / total_enrollments * 100) if total_enrollments else 0
        average_attempts = (total_attempts / total_assessments) if total_assessments else 0

        most_attempted = assessment_scores.values('assessment__title').annotate(
            attempt_count=Count('id')
        ).order_by('-attempt_count').first()
        most_attempted_assessment = most_attempted['assessment__title'] if most_attempted else "No attempts"

        # Placeholder for trend metrics
        enrollment_trend = []
        performance_trend = []

        # Build final response
        response_data = {
            "course_id": str(course.id),
            "course_name": course.name,
            "enrollment_metrics": {
                "total_enrollments": total_enrollments,
                "active_enrollments": active_enrollments,
                "completion_rate": round(completion_rate, 2),
                "dropout_rate": round(dropout_rate, 2),
                "average_enrollment_duration": 0  # Placeholder
            },
            "assessment_metrics": {
                "total_assessments": total_assessments,
                "assessment_types": assessment_types,
                "submission_rate": round(submission_rate, 2),
                "average_grading_time": 0  # Placeholder
            },
            "performance_metrics": {
                "overall_average": round(overall_average, 2),
                "median_score": round(median_score, 2),
                "standard_deviation": round(standard_deviation, 2),
                "passing_rate": round(passing_rate, 2),
                "excellence_rate": round(excellence_rate, 2),
            },
            "engagement_metrics": {
                "average_completion_time": round(float(average_completion_time), 2),
                "active_students_percentage": round(active_students_percentage, 2),
                "average_attempts_per_assessment": round(average_attempts, 2),
                "most_attempted_assessment": most_attempted_assessment,
            },
            "trend_metrics": {
                "enrollment_trend": enrollment_trend,
                "performance_trend": performance_trend,
            }
        }

        return Response(response_data)
